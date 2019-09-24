import sys
from os.path import abspath, join, dirname
import subprocess

base_directory = abspath(join(dirname(__file__), '..'))


def run_command_on_all(command, parallel = False):

    modules = ['idmtools_core', 'idmtools_cli', 'idmtools_platform_comps', 'idmtools_platform_local',
               'idmtools_model_dtk', 'idmtools_models', 'idmtools_test']
    processes = []
    for module in modules:
        p = subprocess.Popen(f'pymake {command}', cwd=join(base_directory, module), shell=True)
        if parallel:
            processes.append(p)
        else:
            p.wait()
    if parallel:
        print('Waiting to finish')
        [p.wait() for p in processes]


run_command_on_all(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "p")
