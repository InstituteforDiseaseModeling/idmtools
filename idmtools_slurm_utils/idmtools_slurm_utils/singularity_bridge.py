"""Allows bridged mode for idmtools."""
import argparse
import json
import os
import subprocess
import sys
import time
from logging import getLogger, basicConfig, DEBUG, FileHandler, StreamHandler, INFO
from os import PathLike
from pathlib import Path
from typing import Dict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = getLogger(__name__)
VALID_COMMANDS = ['sbatch', 'scancel', 'verify']


class IdmtoolsJobWatcher:
    """
    Watches the bridge directory and communicates jobs to slurm.
    """

    def __init__(self, directory_to_watch: PathLike, directory_for_status: PathLike, check_every: int = 5):
        """
        Creates our watcher.

        Args:
            directory_to_watch: Directory to sync from
            directory_for_status: Directory for status messages
            check_every: How often should directory be synced
        """
        self.observer = Observer()
        self._directory_to_watch = directory_to_watch
        self._directory_for_status = directory_for_status
        self._check_every = check_every

    def run(self):
        """
        Run the watcher.
        """
        event_handler = IdmtoolsJobHandler(self._directory_for_status)
        self.observer.schedule(event_handler, str(self._directory_to_watch), recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(self._check_every)
        except Exception as e:
            self.observer.stop()
            logger.exception(e)
        self.observer.join()


class IdmtoolsJobHandler(FileSystemEventHandler):
    """
    Handles messages about new messages.
    """

    def __init__(self, directory_for_status: PathLike, cleanup_job: bool = True):
        """
        Creates handler.

        Args:
            directory_for_status: Directory to use for status
            cleanup_job: Should the job be cleaned up after submission
        """
        self._directory_for_status = directory_for_status
        self._cleanup_job = cleanup_job
        super().__init__()

    def on_created(self, event):
        """
        On Created events.

        Args:
            event: Event details.
        """
        if str(event.src_path).endswith(".json"):
            process_job(event.src_path, self._directory_for_status, self._cleanup_job)


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
        with open(job_path, "r") as jin:
            info = json.load(jin)

            if "command" not in info or info['command'].lower() not in VALID_COMMANDS:
                result = dict(
                    status="error",
                    output="No command specified. You must specify either sbatch, scancel, or verify"
                )
            else:
                command = info['command'].lower()
                if command == "sbatch":
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
                write_result(result, result_name)
                if cleanup_job:
                    os.unlink(job_path)
    except Exception as e:
        logger.exception(e)
        pass


def write_result(result: Dict, result_name: Path):
    """
    Write the result of a job to a directory.

    Args:
        result: Result to write
        result_name: Path to write result to.
    """
    with open(result_name, "w") as rout:
        json.dump(result, rout)


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
        logger.debug(f"Result\n=============\n{stdout}\n=============\n")
    return stdout, result.returncode


def dir_path(directory_path):
    """
    Options that are path based.

    Args:
        directory_path: String to validate

    Raises:
        NotADirectoryError if directory_path is not a valid path

    Returns:
        Value is it is a path
    """
    if os.path.isdir(directory_path):
        return directory_path
    else:
        raise NotADirectoryError(directory_path)


def main():
    """
    CLI main.
    """
    bp = Path.home().joinpath(".idmtools").joinpath("singularity-bridge")
    bp.mkdir(parents=True, exist_ok=True)
    basicConfig(level=INFO, handlers=[
        StreamHandler(sys.stdout),
        FileHandler(bp.joinpath("sb.log"))
    ])

    parser = argparse.ArgumentParser("idmtools Slurm Bridge")
    parser.add_argument("--job-directory", default=str(bp))
    parser.add_argument("--status-directory", default=str(bp.joinpath("results")))
    parser.add_argument("--check-every", type=int, default=5)

    args = parser.parse_args()

    if not Path(args.status_directory).exists():
        Path(args.status_directory).mkdir(parents=True, exist_ok=True)

    if not Path(args.job_directory).exists():
        Path(args.job_directory).mkdir(parents=True, exist_ok=True)

    logger.info(f"Bridging jobs from {args.job_directory}")
    w = IdmtoolsJobWatcher(args.job_directory, args.status_directory, args.check_every)
    w.run()


if __name__ == '__main__':
    main()
