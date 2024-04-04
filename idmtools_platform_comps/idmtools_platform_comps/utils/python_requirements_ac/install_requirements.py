"""idmtools script to run on Slurm to install python files.

This is part of the RequirementsToAssetCollection tool. This will run on the HPC in an Experiment to install the python requirements
as output that will be converted to an AssetCollection later.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import compileall
import glob
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

CURRENT_DIRECTORY = os.getcwd()
LIBRARY_ROOT = 'L'
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, LIBRARY_ROOT)
REQUIREMENT_FILE = 'requirements_updated.txt'
INDEX_URL = 'https://packages.idmod.org/artifactory/api/pypi/pypi-production/simple'


def install_packages_from_requirements(python_paths=None):
    """
    Install our packages to a local directory.

    Args:
        python_paths: system Python path
    Returns: None
    """
    if python_paths is None:
        env = dict()
    else:
        if type(python_paths) is not list:
            python_paths = [python_paths]

        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(python_paths)

    print("Running pip install -r {} to tmp directory".format(REQUIREMENT_FILE))
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-t", LIBRARY_PATH, "-r", f"Assets/{REQUIREMENT_FILE}", "-i",
         f"{INDEX_URL}"], env=env)


def set_python_dates():
    """
    Set python to the same dates so we don't create pyc files with differing dates.

    Pyc embed the date, so this is a workaround for that behaviour.
    """
    print("Updating file dates")
    pool = ThreadPoolExecutor()
    date = datetime(year=2020, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    mod_time = time.mktime(date.timetuple())
    for filename in glob.glob(f"{LIBRARY_PATH}{os.path.sep}**/*.py", recursive=True):
        print(f"Updating date on {filename}")
        pool.submit(os.utime, filename, (mod_time, mod_time))
    pool.shutdown(True)


def compile_all(python_paths=None):
    """
    Compile all the python files to pyc.

    This is useful to reduce how often this happens since python will be an asset
    """
    print("Compiling pyc files")
    if python_paths is None:
        env = dict()
    else:
        if type(python_paths) is not list:
            python_paths = [python_paths]

        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(python_paths)
    print(f'Compiling {LIBRARY_PATH}')
    compileall.compile_dir(os.path.relpath(LIBRARY_PATH).strip(os.path.sep), force=True)
    print(f'Pyc Files Generated: {len(glob.glob(f"{LIBRARY_PATH}{os.path.sep}**/*.pyc", recursive=True))}')


if __name__ == "__main__":
    print('CURRENT_DIRECTORY: \n', CURRENT_DIRECTORY)
    print('LIBRARY_PATH: \n', LIBRARY_PATH)

    if sys.platform == "win32":
        full_path = os.path.join(LIBRARY_PATH, 'lib', 'site-packages')
    else:
        full_path = os.path.join(LIBRARY_PATH, 'lib', 'python{}'.format(sys.version[:3]), 'site-packages')

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    print("Adding {} to the system path".format(full_path))
    sys.path.insert(1, full_path)

    tb = None
    try:
        install_packages_from_requirements(sys.path)
        set_python_dates()
        compile_all(sys.path)
    except Exception:
        tb = traceback.format_exc()
        print(tb)
    finally:
        if tb:
            sys.exit(-1)
