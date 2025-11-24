"""
This is SlurmPlatform operations utils.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import os
import subprocess
from logging import getLogger

logger = getLogger(__name__)


def get_max_array_size():
    """
    Get Slurm MaxArraySize from configuration.
    Returns:
        Slurm system MaxArraySize
    """
    try:
        output = subprocess.check_output(['scontrol', 'show', 'config'])
        for line in output.decode().splitlines():
            if line.startswith("MaxArraySize"):
                max_array_size = int(line.split("=")[1])
                return max_array_size - 1
    except (subprocess.CalledProcessError, IndexError, ValueError):
        pass

    return None


def check_home(directory: str) -> bool:
    """
    Check if a directory is under HOME.
    Args:
        directory: a directory

    Returns:
        True/False
    """
    home = os.path.expanduser("~").replace('\\', '/')
    directory = directory.replace('\\', '/')
    if directory.startswith(home):
        return True
    else:
        return False
