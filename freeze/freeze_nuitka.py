import glob
import logging
import os
import stat
import subprocess
import sys
import time

log = logging.getLogger()
log.setLevel(logging.DEBUG)

stream_formatter = logging.Formatter("%(message)s")

file_formatter = logging.Formatter("%(message)s")
file_handler = logging.FileHandler(filename="freeze_log.txt")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(stream_formatter)

log.addHandler(file_handler)
log.addHandler(stream_handler)

# Intercept stdout and stderr then dump them to both console and file
log = logging.getLogger("freeze")

try:
    subprocess.run("tee --version", shell=True, check=True)
    has_tee = True
except:
    has_tee = False

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _run_cmd(cmd, *args, **kwargs):
    log.debug(f"Executing: {cmd}")
    return subprocess.run(cmd, *args, **kwargs)


def freeze():
    import humanfriendly

    start_time = time.time()

    src = r"../ansys/rep/template/__main__.py"
    exe = "rep-repo-template"
    tgt = "build"

    include_modules = [
        # "opentelemetry.propagate",
    ]

    no_follows = [
        "pytest-xdist",
        "pytest-timeout",
        "debugpy",
        "pytest-xprocess",
        "pygments",
        "ipython",
    ]

    data_files = []
    plugin_dirs = []
    plugin_files = []

    data_dirs = []
    # if sys.platform != "darwin":
    #     for p in sys.path:
    #         if not os.path.isdir(p):
    #             continue
    #         for root, dirs, _ in os.walk(p):
    #             for dir in dirs:
    #                 if dir.startswith("opentelemetry_") and dir.endswith(".dist-info"):
    #                     data_dirs.append((os.path.join(root, dir), dir))

    args = [
        f"--output-file={exe}",  # does not have .bin extension like default
        f"--output-dir={tgt}",
        f"--show-progress",
        f"--show-modules",
        f"--follow-imports",
        f"--full-compat",
        f"--standalone",
        f"--onefile ",
        f"--noinclude-default-mode=nofollow",
        f"--noinclude-unittest-mode=warning",  # Needed by humanfriendly package
        f"--noinclude-pytest-mode=nofollow",
        f"--noinclude-setuptools-mode=nofollow",
        f"--assume-yes-for-downloads",
    ]
    if sys.platform != "win32":
        args.extend(
            [
                f"--onefile-tempdir-spec='%TEMP%/rep-repo-template_%PID%_%TIME%'",
            ]
        )

    if include_modules:
        args.extend([f"--include-module={n}" for n in include_modules])
    if data_files:
        args.extend([f"--include-data-files={d[0]}={d[1]}" for d in data_files])
    if data_dirs:
        args.extend([f"--include-data-dir={d[0]}={d[1]}" for d in data_dirs])
    if no_follows:
        args.extend([f"--nofollow-import-to={n}" for n in no_follows])
        args.extend([f"--noinclude-custom-mode={n}:nofollow" for n in no_follows])
    if plugin_dirs:
        args.extend([f"--include-plugin-directory={n}" for n in plugin_dirs])
    if plugin_files:
        args.extend([f"--include-plugin-files={n}" for n in plugin_files])

    cmd = f"{sys.executable} -m nuitka {' '.join(args)} {src}"
    if has_tee:
        cmd = f"{cmd} | tee nuitka_log.txt"
    _run_cmd(cmd, shell=True, check=True)

    if sys.platform != "win32":
        for f in glob.glob(os.path.join(os.getcwd(), "**", "nuitka.bin"), recursive=True):
            st = os.stat(f)
            os.chmod(f, st.st_mode | stat.S_IEXEC)

    finished_time = time.time()
    log.info(f"Freezing took {humanfriendly.format_timespan(finished_time - start_time)}")


def prepare_modules():
    required = {
        "nuitka": None,
        "zstandard": None,
        "humanfriendly": None,
    }

    remove = []
    if sys.platform == "win32":
        remove.append("pyreadline")

    missing = []
    for k, v in required.items():
        try:
            __import__(k)
        except:
            version = "" if not v else f"=={v}"
            missing.append(f"{k}{version}")

    if missing:
        subprocess.run(f"{sys.executable} -m pip install {' '.join(missing)}", check=True, shell=True)

    if remove:
        subprocess.run(f"{sys.executable} -m pip uninstall -y {' '.join(remove)}", check=True, shell=True)


if __name__ == "__main__":
    if not hasattr(sys, "base_prefix") or sys.base_prefix == sys.prefix:
        log.info(f"This script should only be ran inside of a virtual env")
        sys.exit(1)

    prepare_modules()
    freeze()
