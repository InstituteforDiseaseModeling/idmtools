import sys
from os.path import abspath, join, dirname
import subprocess

base_directory = abspath(join(dirname(__file__), '..'))


def run_command_on_all(command):

    p = ['idmtools_core', 'idmtools_cli', 'idmtools_platform_comps', 'idmtools_platform_local']
    [subprocess.run(f'pymake {command}', cwd=join(base_directory, f), shell=True) for f in p]


run_command_on_all(sys.argv[1])