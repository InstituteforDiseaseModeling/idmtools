"""
utilities for command line.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import contextlib
import logging
import sys

from io import StringIO
from itertools import cycle

animation = cycle(("|", "/", "-", "\\"))


@contextlib.contextmanager
def suppress_output(stdout=True, stderr=True):
    """
    Suppress any print/logging from a block of code.

    Args:
        stdout: If True, hide output from stdout; if False, show it.
        stderr: If True, hide output from stderr; if False, show it.
    """
    # Remember existing output streams for restoration
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Suppress requested channel output
    if stdout:
        sys.stdout = StringIO()
    if stderr:
        sys.stderr = StringIO()

    # Deactivate logging
    previous_level = logging.root.manager.disable
    logging.disable(logging.ERROR)

    yield

    # Restore original output streams
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    logging.disable(previous_level)
