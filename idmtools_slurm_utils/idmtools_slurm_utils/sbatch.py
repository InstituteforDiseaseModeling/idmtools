"""Handles interaction with sbatch command."""
import subprocess
from logging import DEBUG, getLogger
from pathlib import Path
from typing import Dict

ERROR_NO_WORKING_DIRECTORY = "No working directory provided for command"

logger = getLogger()


def command_sbatch(info: Dict) -> Dict:
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
            output, return_code = run_sbatch(wd)
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


def run_sbatch(working_directory: Path):
    """
    Just a sbatch script.

    Args:
        working_directory: Working directory

    """
    sbp = working_directory.joinpath("sbatch.sh")
    if not sbp.exists():
        return f"FAILED: No Directory name {sbp}"
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Running 'sbatch sbatch.sh' in {working_directory}")
    result = subprocess.run(['sbatch', '--parsable', 'sbatch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
    stdout = result.stdout.decode('utf-8').strip()
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Result for {sbp}\n=============\n{stdout}\n=============\n\n")
    return stdout, result.returncode
