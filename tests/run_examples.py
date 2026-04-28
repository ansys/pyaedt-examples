import subprocess
from pathlib import Path
import sys
import tempfile
import re
import os
import time
from datetime import timedelta

# --- Configuration ---
AEDT_VERSION="2026.1"
ROOT_DIR = Path(r"C:\Users\jvelasco\Documents\pyaedt-examples\examples")
VENV_PYTHON = Path(r"C:\Users\jvelasco\Documents\pyaedt-examples\.venv\Scripts\python.exe")
LOG_DIR = Path(r"C:\Users\jvelasco\AppData\Roaming\JetBrains\PyCharm2025.3\scratches\examples\logs")
RUN_ONLY = {"resistance.py"}

# ----------- Do not edit under this line -------------
LOG_FILE = LOG_DIR / f"failed_scripts_{AEDT_VERSION.replace('.','R')}.log"
SUMMARY_FILE = LOG_DIR / f"test_summary_{AEDT_VERSION.replace('.','R')}.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Select Python executable
python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
print(f"Using Python: {python_exe}")

# Fresh start for logs
for f in [LOG_FILE, SUMMARY_FILE]:
    if f.exists():
        f.unlink()

SKIP_FILES = {"template.py", "__init__.py", "index.rst"}
TEST_DIR = Path(__file__).parent / "tests"


def inject_test_code(script_content, script_name):
    """Inject test code from test/ref_<script_name>.py before the last save_project()/release_desktop() pair."""
    ref_file = TEST_DIR / f"ref_{script_name}"
    if not ref_file.exists():
        return script_content

    with ref_file.open('r') as f:
        test_code = f.read()

    # Find the last release_desktop() and inject before its preceding save_project()
    last_release = script_content.rfind('.release_desktop()')
    if last_release == -1:
        return script_content

    # Find the preceding save_project() line
    save_pos = script_content.rfind('.save_project()', 0, last_release)
    if save_pos != -1:
        inject_pos = script_content.rfind('\n', 0, save_pos) + 1
    else:
        inject_pos = script_content.rfind('\n', 0, last_release) + 1

    return (
        script_content[:inject_pos]
        + "\n# --- Injected test code ---\n"
        + test_code
        + "\n# --- End test code ---\n\n"
        + script_content[inject_pos:]
    )


def patch_script_for_non_gui(script_content):
    """Patch script to run in non-GUI mode by modifying NG_MODE and commenting out plots."""

    # Makes sure everything is running in NG mode
    patched = re.sub(r'NG_MODE\s*=\s*False', 'NG_MODE = True', script_content)
    patched = re.sub(r'non_graphical\s*=\s*False', 'non_graphical = True', patched)

    # Add non_graphical=NG_MODE to Desktop() calls
    # Handles: Desktop(new_desktop=True, version=SOME_VERSION)
    patched = re.sub(r'Desktop\(new_desktop=True,\s*version=([^)]+)\)', r'Desktop(new_desktop=True, version=\1, non_graphical=NG_MODE)', patched)

    # select AEDT version
    patched = re.sub(r'AEDT_VERSION\s*=\s*["\']?[\d.]+["\']?', f'AEDT_VERSION="{AEDT_VERSION}"', patched)

    # select EDB version
    patched = re.sub(r'edb_version\s*=\s*["\']?[\d.]+["\']?', f'edb_version="{AEDT_VERSION}"', patched)

    # Comment out .plot() and .show() calls that have no arguments (GUI-only calls)
    # Avoid commenting out .plot(filepath) calls that save to files
    # patched = re.sub(r'^(\s*)((?!#).*\.(plot|show)\(\))', r'\1# \2  # (disabled for non-GUI)', patched, flags=re.MULTILINE)

    # Handles OLD_AEDT_VERSION = "2024.1" from component conversion example - Not instaleld in my machine
    patched = re.sub(r'OLD_AEDT_VERSION\s*=\s*"2024\.1"', 'OLD_AEDT_VERSION = "2024.2"', patched)

    # Comment out pyvista animations
    patched = re.sub(r'^(\s*)((?!#).*\.animate\(\))', r'\1# \2  # (disabled for non-GUI)', patched, flags=re.MULTILINE)

    # Disable SSL verification in case of proxy/firewall issues
    requests_patch = (
        "import requests\n"
        "requests.packages.urllib3.disable_warnings()\n"
        "_orig_request = requests.Session.request\n"
        "def _patched_request(self, *args, **kwargs): kwargs.setdefault('verify', False); return _orig_request(self, *args, **kwargs)\n"
        "requests.Session.request = _patched_request\n"
    )

    # Disable runtime plotting using matplotlib or pyvista
    visualization_patch = (
        "import matplotlib\n"
        "matplotlib.use('Agg')\n"
        "import os\n"
        "os.environ['PYVISTA_OFF_SCREEN']='true'\n"
    )

    patched = visualization_patch + requests_patch + patched

    return patched


# --- Execution ---
env = os.environ.copy()
results = []
overall_start = time.time()

# Gather all .py files excluding skips
scripts = [p for p in sorted(ROOT_DIR.rglob("*.py")) if p.name not in SKIP_FILES]

# Filter to run only specific scripts (comment out to run all)
if RUN_ONLY:
    scripts = [p for p in scripts if p.name in RUN_ONLY]

for i, script_path in enumerate(scripts, 1):
    script_start = time.time()
    print(f"[{i}/{len(scripts)}] Running: {script_path.name}", end="", flush=True)

    try:
        with open(script_path, 'r') as f:
            content = patch_script_for_non_gui(f.read())
        content = inject_test_code(content, script_path.name)
        # print(content)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        # Run process and capture results
        process = subprocess.run(
            [python_exe, str(tmp_path)],
            capture_output=True,
            text=True,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )

        elapsed = time.time() - script_start
        success = (process.returncode == 0)
        results.append({'name': script_path.name, 'time': elapsed, 'success': success})

        if success:
            print(f" ✓ ({elapsed:.1f}s)")
            with open(SUMMARY_FILE, "a") as f:
                f.write(f"PASSED: {script_path.name} ({elapsed:.1f}s)\n")
        else:
            # Exit Code and Error reporting
            print(f" ✗ ({elapsed:.1f}s) - Exit Code: {process.returncode}")

            if process.stderr:
                # Filter for the last non-empty line (usually the specific Python error)
                error_lines = [line.strip() for line in process.stderr.split('\n') if line.strip()]
                last_error = error_lines[-1] if error_lines else "Unknown error"
                print(f"    Error: {last_error[:100]}")

            with open(LOG_FILE, "a") as f:
                f.write(f"FAILED: {script_path}\nExit Code: {process.returncode}\n")
                f.write(f"STDERR:\n{process.stderr}\n")
                f.write(f"STDOUT:\n{process.stdout}\n")
                f.write(f"{'-' * 40}\n")
            with open(SUMMARY_FILE, "a") as f:
                f.write(f"FAILED: {script_path.name} ({elapsed:.1f}s) [Exit {process.returncode}]\n")

    except Exception as e:
        results.append({'name': script_path.name, 'time': 0, 'success': False})
        print(f"  ✗ SYSTEM ERROR - {str(e)[:50]}")
    finally:
        if 'tmp_path' in locals():
            tmp_path.unlink(missing_ok=True)

# --- Summary & Performance ---
overall_elapsed = time.time() - overall_start
passed = sum(1 for r in results if r['success'])
failed = len(results) - passed

print(f"\n{'=' * 60}")
print(f"Summary: {passed} passed, {failed} failed out of {len(scripts)} scripts")
print(f"Total time: {timedelta(seconds=int(overall_elapsed))}")
print(f"{'=' * 60}")
