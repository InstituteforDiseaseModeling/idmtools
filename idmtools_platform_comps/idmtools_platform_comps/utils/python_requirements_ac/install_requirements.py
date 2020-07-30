import os
import subprocess
import sys
import traceback

CURRENT_DIRECTORY = os.getcwd()
LIBRARY_ROOT = 'L'
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, LIBRARY_ROOT)
REQUIREMENT_FILE = 'requirements_updated.txt'
INDEX_URL = 'https://packages.idmod.org/artifactory/api/pypi/pypi-production/simple'


def install_packages_from_requirements(python_paths=None):
    """
    Install our packages to a local directory
    Args:
        requirements_file: requirements file
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
        # should use date of py file + checksum to produce hash of pyc to determine if need to recompile and prevent need to resuse
        env['PYTHONHASHSEED'] = '2429763551'

    print("Running pip install -r {} to tmp directory".format(REQUIREMENT_FILE))
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-t", LIBRARY_PATH, "-r", f"Assets/{REQUIREMENT_FILE}", "-i",
         f"{INDEX_URL}"], env=env)


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
    except Exception:
        tb = traceback.format_exc()
        print(tb)
    finally:
        if tb:
            sys.exit(-1)
