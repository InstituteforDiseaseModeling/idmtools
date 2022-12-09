"""Handles interaction with scancel command."""
import subprocess
from logging import DEBUG, getLogger
from typing import Dict, Tuple, List, Union

ERROR_NO_JOB_ID = "No job id provided for command"

logger = getLogger()


def command_scancel(info: Dict) -> Dict:
    """
    Interacts with the scancel command.

    Args:
        info: Info on what to cancel

    Returns:
        Result from cancel
    """
    if 'job_ids' in info:
        job_ids = info['job_ids']
        output, return_code = run_cancel(job_ids)
        result = dict(
            status="success" if return_code == 0 else "error",
            return_code=return_code,
            output=output
        )
    else:
        result = dict(
            status="error",
            return_code=-1,
            output=ERROR_NO_JOB_ID
        )
    return result


def run_cancel(job_ids: Union[str, List[str]]) -> Tuple:
    """
    Kick out slurm scancel command.

    Args:
        job_ids: slurm job id list
    """
    if isinstance(job_ids, str):
        job_ids = [job_ids]

    result = subprocess.run(['scancel', *job_ids], stdout=subprocess.PIPE)
    print('result: ', result)
    stdout = "success" if result.returncode == 0 else 'error'
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Result for scancel job {job_ids}\n=============\n{stdout}\n=============\n\n")
    return stdout, result.returncode
