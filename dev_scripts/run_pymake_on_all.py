import argparse
import os
import sys
from os.path import abspath, join, dirname

base_directory = abspath(join(dirname(__file__), '..'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', default=False, action='store_true', help='Parallel Run')
    parser.add_argument('--env', action="append", default=[], help="Environment variables in the form of NAME=val")
    parser.add_argument('command', help='Pymake Command to run')

    args = parser.parse_args()

    p_str = '--parallel ' if args.parallel else ''
    env_str = "--env ".join(args.env)
    if env_str:
        env_str = f"--env {env_str}"
    print(f'python {os.path.join(base_directory, "dev_scripts", "run_all.py")} {env_str} {p_str}--exec "pymake {args.command}"')
    sys.exit(os.system(f'python {os.path.join(base_directory, "dev_scripts", "run_all.py")} {env_str} {p_str}--exec "pymake {args.command}"'))
