#!/usr/bin/env python
"""Run a command and wait on the command to finish with an optional timeout parameter.

This is used by the build to time-box some build commands.
"""
import errno
from functools import wraps

import argparse
import os
import signal
import subprocess
import sys
from os.path import abspath, join, dirname
from typing import List

base_directory = abspath(join(dirname(__file__), '..'))


def timeout(seconds=10, error_message=None):
    """Decorator to add a timeout to a function. Default to 10 second timeout.

    Args:
        seconds: Seconds until a call should be considered timed out
        error_message: Optional error message to display

    Returns:
        None
    """
    if error_message is None:
        error_message = os.strerror(errno.ETIME)

    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def run_command_on_all(commands: List['str'], parallel: bool = True):
    """Run a set of commands.

    Args:
        commands: List of commands to run
        parallel: Should we run the commands in parallel mode

    Returns:
        None
    """
    processes = []

    @timeout(10)
    def signal_handler(sig, frame):
        print('Stopping running processes')
        for p in processes:
            print(f'Trying to kill {p.pid}')
            p.kill()
            p.terminate()
            p.wait()
        sys.exit(0)

    if os.name != 'nt':
        # register signal handler to stop on ctrl c and ctrl k
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTSTP, signal_handler)
    for command in commands:
        sub_dir = None
        if ";;;" in command:
            command, sub_dir = command.split(";;;")
        if sub_dir:
            wd = os.path.join(base_directory, sub_dir)
        else:
            wd = base_directory
        print(f'Running {command} in {wd}')
        p = subprocess.Popen(f'{command}', cwd=wd, shell=True)
        if parallel:
            processes.append(p)
        else:
            p.wait()
    if parallel:
        print('Waiting to finish')
        [p.wait() for p in processes]
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', default=True, action='store_true', help='Parallel Run')
    parser.add_argument('--command', action='append')
    args = parser.parse_args()

    if isinstance(args.command, str):
        args.command = []

    if args.parallel:
        print('Running in Parallel')
    run_command_on_all(args.command, args.parallel)
