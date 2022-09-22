"""Handles CLI portion of idmtools-slurm-bridge."""
import argparse
import os
import signal
import sys
from functools import partial
from logging import DEBUG, StreamHandler, getLogger, Formatter, getLevelName
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import coloredlogs
from idmtools_slurm_utils.watcher import IdmtoolsJobWatcher

logger = getLogger()
user_logger = getLogger('user')


def setup_loggers(config_directory: Path, console_level: int, file_level: int):
    """
    Setup loggers.

    Args:
        config_directory: Directory where config lives
        console_level: Level to log to console
        file_level: Level to log to file

    Returns:
        None
    """
    formatter = Formatter('%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
    logger.setLevel(DEBUG)

    stream_handler = StreamHandler()
    stream_handler.setLevel(console_level)
    stream_handler.setFormatter(formatter)

    log_file_path = config_directory.joinpath("idmtools-slurm-bridge.log")
    file_handler = TimedRotatingFileHandler(filename=log_file_path, when='midnight', backupCount=30)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    coloredlogs.install(level='DEBUG', logger=user_logger)


def existing_process_running(pid_file: Path):
    """
    Existing Process running.

    Args:
        pid_file:

    Returns:
        None
    """
    with open(pid_file, 'r') as p_in:
        current_process = p_in.read()
    user_logger.warning(
        f"It appears another slurm-bridge process is running. Running multiple instances can cause issues. It appears {current_process} is running"
        f"(If a previous run of idmtools-slurm-bridge crashed, you may need to remove {pid_file}."
    )
    while True:
        answer = input("Are you sure you want to continue [y/n]?")
        answer = answer.lower()
        if answer in ["n", "no"]:
            return
        elif answer in ["y", "yes"]:
            break
        else:
            user_logger.warning("Please answer y or n")


def main():
    """
    CLI main.
    """
    bp = Path.home().joinpath(".idmtools").joinpath("singularity-bridge")

    bp.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser("idmtools Slurm Bridge")
    parser.add_argument("--job-directory", default=str(bp))
    parser.add_argument("--status-directory", default=str())
    parser.add_argument("--check-every", type=int, default=5)
    parser.add_argument("--console-level", type=str, default='INFO', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])
    parser.add_argument("--file-level", type=str, default='DEBUG', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])

    args = parser.parse_args()

    args.status_directory = Path(args.status_directory)
    args.job_directory = Path(args.job_directory)
    args.console_level = getLevelName(args.console_level)
    args.file_level = getLevelName(args.file_level)

    pid_file = args.job_directory.joinpath("slurm-bridge.pid")
    if not args.status_directory.exists():
        Path(args.status_directory).mkdir(parents=True, exist_ok=True)

    if not args.job_directory.exists():
        Path(args.job_directory).mkdir(parents=True, exist_ok=True)

    setup_loggers(args.job_directory, args.console_level, args.file_level)

    if pid_file.exists():
        existing_process_running(pid_file)

    user_logger.info(f"Bridging jobs from {args.job_directory}")
    # Capture control C
    signal.signal(signal.SIGINT, partial(cleanup, config_directory=args.job_directory))
    with open(pid_file, 'w') as pid_out:
        pid_out.write(str(os.getpid()))
    w = IdmtoolsJobWatcher(args.job_directory, args.status_directory, args.check_every)
    w.run()
    # We shouldn't ever hit here as user has to end process using ctrl+c
    cleanup(config_directory=args.job_directory)


def cleanup(config_directory: Path, *args, **kwargs):
    """
    Cleanup pid when user tries to kill process.

    Args:
        config_directory: The base config directory
    """
    pid_file = config_directory.joinpath("slurm-bridge.pid")
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Deleting {pid_file}')
    pid_file.unlink(missing_ok=True)
    sys.exit(0)
