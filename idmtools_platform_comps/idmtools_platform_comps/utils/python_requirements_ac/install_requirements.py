import sys
import os
import subprocess
import traceback

CURRENT_DIRECTORY = os.getcwd()
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'Libraries', 'site_packages')
REQUIREMENT_FILE = 'requirements_updated.txt'


def install_packages_from_requirements(requirements_file=REQUIREMENT_FILE, python_paths=None):
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

    print("Running pip install -r {} to tmp directory".format(requirements_file))
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-t", LIBRARY_PATH, "-r", requirements_file], env=env)


if __name__ == "__main__":
    if sys.platform == "win32":
        full_path = os.path.join(LIBRARY_PATH, 'lib', 'site-packages')
    else:
        full_path = os.path.join(LIBRARY_PATH, 'lib', 'python{}'.format(sys.version[:3]), 'site-packages')

    print('CURRENT_DIRECTORY: \n', CURRENT_DIRECTORY)
    print('LIBRARY_PATH: \n', LIBRARY_PATH)
    print("Adding {} to the system path".format(full_path))

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    sys.path.insert(1, full_path)
    tb = None

    try:
        install_packages_from_requirements(f'Assets/{REQUIREMENT_FILE}', sys.path)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
    finally:
        if tb:
            sys.exit(-1)
