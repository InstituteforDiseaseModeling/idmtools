#!/usr/bin/env python
"""Runs a commnad in all the idmtools modules in this repo.

This is used in build processes to parallelize some operations.
"""
import argparse
import os
import signal
import subprocess
import sys
from os.path import abspath, join, dirname

from typing import List, Optional, Dict

base_directory = abspath(join(dirname(__file__), '..'))
modules = ['idmtools_core', 'idmtools_cli', 'idmtools_platform_comps', 'idmtools_platform_local',
           'idmtools_models', 'idmtools_test', 'idmtools_platform_slurm', 'idmtools_slurm_utils']


def run_command_on_all(idm_modules: List[str], command: str, parallel: bool = False, subdir: Optional[str] = None,
                       env_override: Dict[str, str] = None):
    """Runs a command in all the idmtools packages.

    Args:
        idm_modules: List of modules to execute against
        command: Command to run
        parallel: Should we run the instances in parallel mode
        subdir: Should we use a subdirect(eg, idmtools_platform_comps/tests)
        env_override: Any environment overides

    Returns:
        None
    """
    processes = []

    if env_override is None:
        env_override = dict()

    def signal_handler(sig, frame):
        print('Stopping running processes')

        for p in processes:
            if os.name != "nt":
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            else:
                os.kill(os.getpid(), signal.CTRL_BREAK_EVENT)

        sys.exit(0)

    if os.name != 'nt':
        # register signal handler to stop on ctrl c and ctrl k
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTSTP, signal_handler)
    else:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGBREAK, signal_handler)
    for module in idm_modules:
        wd = join(base_directory, module)
        if subdir:
            wd = join(wd, subdir)
        print(f'Running {command} in {wd}')
        if len(env_override):
            print(f"Extra Environment vars {env_override}")
        current_env = dict(os.environ)
        current_env.update(env_override)
        p = subprocess.Popen(f'{command}', cwd=wd, shell=True, env=current_env)
        processes.append(p)
        if not parallel:
            p.wait()
            processes.pop()
    if parallel:
        print('Waiting to finish')
        [p.wait() for p in processes]
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', default=False, action='store_true', help='Parallel Run')
    for module in modules:
        parser.add_argument(f'--no-{module.replace("_", "-")}', default=False, action='store_false',
                            help=f'Disable running {module}')
    parser.add_argument('-sd', '--sub-dir', default=None, help='Subdirectory within module to use as working directory')
    parser.add_argument('--env', action="append", default=[], help="Environment variables in the form of NAME=val")
    parser.add_argument('-ex', '--exec', help='command to run')
    args = parser.parse_args()

    args.modules = []
    for module in modules:
        if not getattr(args, f'no_{module}'):
            args.modules.append(module)

    env_override = dict()
    for v in args.env:
        if "=" not in v:
            print(f"No value specified in environment line {v}")
            sys.exit(-1)
        else:
            name = v[:v.index("=")]
            env_override[name] = v[v.index("=") + 1:]
    print(f'Running on {args.modules}')
    if args.parallel:
        print('Running in Parallel')
    run_command_on_all(args.modules, args.exec, args.parallel, args.sub_dir, env_override)
