import subprocess
from os.path import abspath, dirname

# convenience script to run install for packing environment

base_directory = abspath(dirname(__file__))
subprocess.run(["pip", "install", "-r", "package_requirements.txt"], cwd=base_directory)
