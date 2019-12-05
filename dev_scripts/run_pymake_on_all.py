import argparse
import os
import sys
from os.path import abspath, join, dirname

base_directory = abspath(join(dirname(__file__), '..'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(f'--parallel', default=False, action='store_true', help='Parallel Run')
    parser.add_argument(f'command', help='Pymake Command to run')

    args = parser.parse_args()

    p_str = '--parallel ' if args.parallel else ''
    sys.exit(os.system(f'python {os.path.join(base_directory, "dev_scripts", "run_all.py")} {p_str}--exec "pymake {args.command}"'))
