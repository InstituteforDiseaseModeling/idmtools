"""
Helps user verify environment information.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import sys
from typing import Dict


def command_verify(info: Dict):
    """
    Processes the verify command.

    Args:
        info: Info from container

    Returns:
        Info about server
    """
    # Verify we can access the user's config
    # Verify we can access the user's job directory
    # print out python version on both sides
    # Print out process ids from both sides
    return dict(
        sbridge_python_version=sys.version,
        sbrige_python_executable=sys.executable,
        sbridge_os=os.name,
        sbridge_pid=os.getpid()
    )
