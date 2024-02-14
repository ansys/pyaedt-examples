import argparse
import glob
import json
import logging
import os
import subprocess
import sys
import time

file_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s")
stream_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s", datefmt="%H:%M:%S")
file_handler = logging.FileHandler("build.log")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.DEBUG)

log = logging.getLogger(__name__)

log.addHandler(file_handler)
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)


def build_dev(args):
    log.info("Updating pip")
    subprocess.run(f"{sys.executable} -m pip install --upgrade pip", shell=True, check=True)

    log.info("Installing requirements")
    reqs = os.path.join(os.path.dirname(__file__), "requirements", "requirements_build.txt")
    subprocess.run(f"{sys.executable} -m pip install -r {reqs}", shell=True, check=True)
    reqs = os.path.join(os.path.dirname(__file__), "requirements", "requirements_tests.txt")
    subprocess.run(f"{sys.executable} -m pip install -r {reqs}", shell=True, check=True)
    reqs = os.path.join(os.path.dirname(__file__), "requirements", "requirements_example.txt")
    subprocess.run(f"{sys.executable} -m pip install -r {reqs}", shell=True, check=True)

    log.info("Installing in dev mode")
    cmd = f"{sys.executable} -m pip install -e ."
    log.info(f"Calling: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def build_wheels(args):
    log.info("Building wheels")

    subprocess.run(f"{sys.executable} setup.py build", shell=True, check=True)
    subprocess.run(f"{sys.executable} setup.py bdist_wheel", shell=True, check=True)
    wheels = glob.glob(os.path.join("dist", "*.whl"))
    log.info(f"Found {len(wheels)} wheels")
    for w in wheels:
        log.info(f"- {w}")


def gather_licenses(args):
    bin_directory = os.path.join(os.path.dirname(__file__), "bin")
    target_dir = os.path.join(bin_directory, "dependencies_info")
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    subprocess.run(
        f"{sys.executable} -m pip install pip-licenses pipdeptree --index=https://pypi.org/simple",
        shell=True,
        check=True,
    )
    out = subprocess.check_output(f"{sys.executable} -m piplicenses --from=classifier", shell=True)
    out = out.decode()
    with open(os.path.join(target_dir, "pypi.txt"), "w") as f:
        for line in out.splitlines():
            f.write(f"{line}\n")

    out = subprocess.check_output(f"{sys.executable} -m pipdeptree", shell=True)
    out = out.decode()
    with open(os.path.join(target_dir, "pypi_dep_tree.txt"), "w") as f:
        for line in out.splitlines():
            f.write(f"{line}\n")
    log.info(f"Dependencies written to {target_dir}")


def run_tests(args):
    # test_dir = os.path.abspath(args.test_dir)

    # if not os.path.isdir(test_dir):
    #     os.makedirs(test_dir)

    modules = glob.glob(os.path.join(os.path.dirname(__file__), "rep_*", "setup.py"))
    modules = [os.path.relpath(os.path.dirname(m)) for m in modules]

    modules_str = " ".join(modules)

    return_code = 0
    try:
        base_cmd = f"{sys.executable} -m pytest -v --durations=10 --timeout={args.test_timeout}\
             --junitxml {args.test_results} -rf"
        if args.num_workers > 1:
            base_cmd += f" -n{args.num_workers}"
        if args.max_fail:
            base_cmd += f" --maxfail={args.max_fail}"
        if args.no_traceback:
            base_cmd += " --tb=no"
        p = subprocess.run(f"{base_cmd} {modules_str}", shell=True)
        return_code = p.returncode
    finally:
        return return_code


def write_build_info(args):
    root_dir = os.path.dirname(__file__)
    tgt_dir = os.path.join(root_dir, "ansys", "rep", "template")
    tgt = os.path.join(tgt_dir, "build_info.py")

    about = {}
    with open(
        os.path.join(root_dir, "ansys", "rep", "template", "__version__.py"),
        "r",
    ) as f:
        exec(f.read(), about)

    info = {
        "version": about["__version__"],
        "external_version": about["__internal_version__"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "branch": args.branch,
        "short_revision": args.short_revision,
        "revision": args.revision,
    }
    try:
        from ansys.rep.common.build_info import extract_build_info

        detected = extract_build_info(tgt_dir, no_defaults=True)
        log.debug(f"Detected build info: {', '.join([f'{k}={v}' for k,v in detected.items()])}")
        info.update(detected)
    except Exception as ex:
        log.debug(f"Detecting build info not possible: {ex}")

    with open(tgt, "w") as f:
        f.write(f"build_info = {json.dumps(info, indent=4)}")
    log.debug(f"Build info: {', '.join([f'{k}={v}' for k,v in info.items()])}")


def build_dist(args):
    # try:
    #     build_docs(args)
    # except Exception as ex:
    #     log.debug(traceback.format_exc())
    #     log.warning(f"Building docs failed: {ex}")

    if not args.no_freeze:
        run_freeze(args)


def run_freeze(args):

    write_build_info(args)

    if sys.platform == "win32":
        venv_name = "freeze_env"
        if not os.path.isdir(venv_name):
            subprocess.run(f"{sys.executable} -m venv {venv_name}", shell=True, check=True)
        py_bin = os.path.join(venv_name, "Scripts", "python.exe")
        py_bin = os.path.abspath(py_bin)
    else:
        py_bin = "python3"

    subprocess.run(f"{py_bin} -m pip install --force-reinstall .", shell=True, check=True)

    old_cwd = os.getcwd()
    freeze_dir = os.path.join(os.path.dirname(__file__), "freeze")
    os.chdir(freeze_dir)
    subprocess.run(f"{py_bin} freeze_nuitka.py", shell=True, check=True)

    os.chdir(old_cwd)


if __name__ == "__main__":
    log.debug(f"Using python at: {sys.executable}")
    # if not hasattr(sys, "base_prefix") or sys.base_prefix == sys.prefix:
    #     log.info(f"This script should only be ran inside of a virtual env")
    #     sys.exit(1)

    test_directory = "test_run"
    num_workers = os.cpu_count()

    parser = argparse.ArgumentParser(description="Build and test")
    parser.set_defaults(func=build_dev)
    parser.add_argument("--revision", default="dev", help="Set the revision")
    parser.add_argument("--short-revision", default="dev", help="Set short revision")
    parser.add_argument("--branch", default="dev", help="Set branch")
    commands = parser.add_subparsers(title="commands", description="valid commands", dest="cmd")

    dev = commands.add_parser("dev")
    dev.set_defaults(func=build_dev)

    build_info = commands.add_parser("build-info")
    build_info.set_defaults(func=write_build_info)

    licenses = commands.add_parser("licenses")
    licenses.set_defaults(func=gather_licenses)

    tests = commands.add_parser("tests")
    tests.set_defaults(func=run_tests)
    tests.add_argument(
        "-o",
        "--test_dir",
        default=test_directory,
        help="Directory to switch to before running tests",
    )
    tests.add_argument(
        "--test_results",
        default=os.path.join(test_directory, "test_results.xml"),
        help="Where to dump test results",
    )
    tests.add_argument("-t", "--test_timeout", default=300, help="Time after which to kill the test, in seconds")
    tests.add_argument(
        "-j",
        "--num_workers",
        type=int,
        default=num_workers,
        help="Number of workers to use for running tasks",
    )
    tests.add_argument(
        "-x",
        "--max_fail",
        type=int,
        default=0,
        help="Number of tests that are allowed to fail before stopping",
    )
    tests.add_argument(
        "-T",
        "--no_traceback",
        action="store_true",
        help="Don't print tracebacks at end of a test run",
    )

    wheels = commands.add_parser("wheels")
    wheels.set_defaults(func=build_wheels)

    dist = commands.add_parser("dist")
    dist.set_defaults(func=build_dist)
    dist.add_argument("-f", "--no-freeze", action="store_true", help="Skip freezing")

    args = parser.parse_args()
    result = args.func(args)
    if isinstance(result, int):
        sys.exit(result)
