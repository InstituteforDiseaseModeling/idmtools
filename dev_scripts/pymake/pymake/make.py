#!/usr/bin/env python

"""
make.py

A drop-in or mostly drop-in replacement for GNU make.
"""

import sys, os
from .pymake import command, process
import gc


def main():
    if sys.version_info < (3, 0):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
    else:
        # Unbuffered text I/O is not allowed in Python 3.
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w')
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w')
    gc.disable()
    command.main(sys.argv[1:], os.environ, os.getcwd(), cb=sys.exit)
    process.ParallelContext.spin()


if __name__ == '__main__':
    main()
    assert False, "Not reached"
