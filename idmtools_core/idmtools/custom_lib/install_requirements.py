import sys
import os
import subprocess
import traceback

CURRENT_DIRECTORY = os.getcwd()
LIB_PATH = os.path.join(CURRENT_DIRECTORY, 'Libraries')

PIP_COMMANDS = ['pip3', 'pip3.7', 'pip3.6', 'pip']
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

    # get right pip command
    # PIP_COMMAND = get_pip_command()
    PIP_COMMAND = "pip"

    print("Running pip install -r {} to tmp directory".format(requirements_file))
    subprocess.check_call([sys.executable, "-m", PIP_COMMAND, "install", "--prefix", LIB_PATH, "-r", requirements_file],
                          env=env)


def get_pip_command():
    """
    Utility to retrieve right pip command
    Returns: str
    Note: is is not used as COMPS can't find pip
    """
    from distutils import spawn

    for pip in PIP_COMMANDS:
        if spawn.find_executable(pip):
            return pip

    # If we get to this point, no pip was found -> exception
    raise OSError("pip could not be found on this system.\n"
                  "Make sure Python is installed correctly and pip is in the PATH")


if __name__ == "__main__":
    if sys.platform == "win32":
        full_path = os.path.join(LIB_PATH, 'lib', 'site-packages')
    else:
        full_path = os.path.join(LIB_PATH, 'lib', 'python{}'.format(sys.version[:3]), 'site-packages')

    print('CURRENT_DIRECTORY: \n', CURRENT_DIRECTORY)
    print('LIB_PATH: \n', LIB_PATH)
    print("Adding {} to the system path".format(full_path))

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    sys.path.insert(1, full_path)
    tb = None

    try:
        install_packages_from_requirements(f'Assets/{REQUIREMENT_FILE}', sys.path)
        print('Check directory: \n', os.path.abspath('.'))
        print(
            'Asset size: {} mb'.format(sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f)) / 2 ** 20))


    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
    finally:
        if tb:
            sys.exit(-1)
