"""
Handles interaction with bash command.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import subprocess
from logging import DEBUG, getLogger
from pathlib import Path
from typing import Dict

ERROR_NO_WORKING_DIRECTORY = "No working directory provided for command"

logger = getLogger()


def command_bash(info: Dict) -> Dict:
    """
    Process command request for sbatch commands to be executed.

    Args:
        info: Info command

    Returns:
        Result dict
    """
    if 'working_directory' in info:
        wd = Path(info['working_directory'])
        if not wd.exists():
            output = "FAILED: No Directory name %s" % info['working_directory']
            return_code = -1
        else:
            output, return_code = run_bash(wd)
        result = dict(
            status="success" if return_code == 0 else "error",
            return_code=return_code,
            output=output
        )
    else:
        result = dict(
            status="error",
            return_code=-1,
            output=ERROR_NO_WORKING_DIRECTORY
        )
    return result


def run_bash(working_directory: Path):
    """
    Just a bash script.

    Args:
        working_directory: Working directory

    """
    sbp = working_directory.joinpath("batch.sh")
    if not sbp.exists():
        return f"FAILED: No Directory name {sbp}"
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Running 'bash batch.sh' in {working_directory}")
    result = subprocess.run(['bash', 'batch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
    return '', result.returncode
