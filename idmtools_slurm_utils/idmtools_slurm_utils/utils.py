"""
Utils for slurm bridge.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import os
from os import PathLike
from pathlib import Path
from typing import Dict
from logging import getLogger, DEBUG
from idmtools_slurm_utils.bash import command_bash
from idmtools_slurm_utils.sbatch import command_sbatch
from idmtools_slurm_utils.scancel import command_scancel
from idmtools_slurm_utils.verify import command_verify

ERROR_INVALID_COMMAND = "No command specified. You must specify either sbatch, scancel, or verify"

logger = getLogger()

VALID_COMMANDS = ['sbatch', 'scancel', 'verify']


def process_job(job_path, result_dir, cleanup_job: bool = True):
    """
    Process a job.

    Args:
        job_path: Path to the job
        result_dir: Result directory
        cleanup_job: Cleanup job when done(true), false leave it in place.
    """
    try:
        result_dir = Path(result_dir)
        if not result_dir.exists():
            result_dir.mkdir(parents=True, exist_ok=True)
        result_name = result_dir.joinpath(f'{os.path.basename(Path(job_path))}.result')
        result = get_job_result(job_path)
        write_result(result, result_name)
        if cleanup_job:
            os.unlink(job_path)
    except Exception as e:
        logger.exception(e)
        pass


def get_job_result(job_path: PathLike) -> Dict:
    """
    Read a job file in from path and return a result.

    Args:
        job_path: Path

    Returns:
        Result
    """
    with open(job_path, "r") as jin:
        info = json.load(jin)

        if "command" not in info or info['command'].lower() not in VALID_COMMANDS:
            result = dict(
                status="error",
                output=ERROR_INVALID_COMMAND
            )
        else:
            command = info['command'].lower()
            if command == "sbatch":
                result = command_sbatch(info)
            elif command == "bash":
                result = command_bash(info)
            elif command == "verify":
                result = command_verify(info)
            elif command == "scancel":
                result = command_scancel(info)
            else:
                result = dict(
                    status="error",
                    output=ERROR_INVALID_COMMAND
                )
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Result for {job_path}: {json.dumps(result, indent=4, sort_keys=True)}')
    return result


def write_result(result: Dict, result_name: Path):
    """
    Write the result of a job to a directory.

    Args:
        result: Result to write
        result_name: Path to write result to.
    """
    with open(result_name, "w") as rout:
        json.dump(result, rout)
