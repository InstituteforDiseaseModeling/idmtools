import argparse
import os
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--environment', nargs='+', help='Environment variables to set ')
    parser.add_argument('-wd', '--working-dir', help='Working Directory')
    parser.add_argument('-p', '--path', nargs='+', help='Add items to the path')
    parser.add_argument('-ex', help='Add items to the path')

    args = parser.parse_args()
    if args.environment:
        env = dict()
        for e in args.environment:
            parts = e.split("=")
            env[parts[0]] = parts[1]
        print(f"Environment opts: {env}")

    if args.path:
        for p in args.path:
            print(f'Adding {os.path.abspath(p)} to the path')
            sys.path.insert(0, os.path.abspath(p))

    if args.working_dir:
        print(f'Changing working directory to {os.path.abspath(args.working_dir)}')
        os.chdir(os.path.abspath(args.working_dir))
    print(f'Running {args.ex}')
    sys.exit(os.system(args.ex))
