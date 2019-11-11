import argparse
import signal
import subprocess
import sys
from os.path import abspath, join, dirname

from typing import List, Optional

base_directory = abspath(join(dirname(__file__), '..'))
modules = ['idmtools_core', 'idmtools_cli', 'idmtools_platform_comps', 'idmtools_platform_local',
           'idmtools_model_emod', 'idmtools_models', 'idmtools_test']


def run_command_on_all(idm_modules: List[str], command: str, parallel: bool = False, subdir: Optional[str] = None):

    processes = []

    def signal_handler(sig, frame):
        print('Stopping running processes')
        for p in processes:
            print(f'Trying to kill {p.pid}')
            p.kill()
            p.terminate()
            p.wait()
        sys.exit(0)

    # register signal handler to stop on ctrl c and ctrl k
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    for module in idm_modules:
        wd = join(base_directory, module)
        if subprocess:
            wd = join(wd, subdir)
        print(f'Running {command} in {wd}')
        p = subprocess.Popen(f'{command}', cwd=wd, shell=True)
        if parallel:
            processes.append(p)
        else:
            p.wait()
    if parallel:
        print('Waiting to finish')
        [p.wait() for p in processes]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(f'--parallel', default=False, action='store_true', help='Parallel Run')
    for module in modules:
        parser.add_argument(f'--no-{module.replace("_", "-")}', default=False, action='store_false',
                            help=f'Disable running {module}')
    parser.add_argument('-sd', '--sub-dir', default=None, help='Subdirectory within module to use as working directory')
    parser.add_argument('-ex', '--exec', help='command to run')
    args = parser.parse_args()

    args.modules = []
    for module in modules:
        if not getattr(args, f'no_{module}'):
            args.modules.append(module)

    print(f'Running on {args.modules}')
    if args.parallel:
        print('Running in Parallel')
    run_command_on_all(args.modules, args.exec, args.parallel, args.sub_dir)
