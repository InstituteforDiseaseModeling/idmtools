import argparse
import json
import os
import subprocess
import sys
import time
from logging import getLogger, basicConfig, DEBUG, FileHandler, StreamHandler
from os import PathLike
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = getLogger(__name__)


class IdmtoolsJobWatcher:

    def __init__(self, directory_to_watch: PathLike, directory_for_status: PathLike, check_every: int = 5):
        self.observer = Observer()
        self._directory_to_watch = directory_to_watch
        self._directory_for_status = directory_for_status
        self._check_every = check_every

    def run(self):
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

    def __init__(self, directory_for_status: PathLike, cleanup_job: bool = True):
        self._directory_for_status = directory_for_status
        self._cleanup_job = cleanup_job
        super().__init__()

    def on_created(self, event):
        if str(event.src_path).endswith(".json"):
            process_job(event.src_path, self._directory_for_status, self._cleanup_job)


def process_job(job_path, result_dir, cleanup_job: bool = True):
    try:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir, exist_ok=True)
        result_name = os.path.join(result_dir, os.path.basename(job_path) + ".result")
        with open(job_path, "r") as jin:
            info = json.load(jin)
            if 'working_directory' in info:
                if not os.path.exists(info['working_directory']):
                    result = "FAILED: No Directory name %s" % info['working_directory']
                else:
                    result = run_sbatch(info['working_directory'])
                with open(result_name, "w") as rout:
                    rout.write(result)
                if cleanup_job:
                    os.unlink(job_path)
    except Exception as e:
        logger.exception(e)
        pass


def run_sbatch(working_directory):
    sbp = os.path.join(working_directory, "sbatch.sh")
    if not os.path.exists(sbp):
        return "FAILED: No Directory name %s" % sbp
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Running 'sbatch sbatch.sh' in {working_directory}")
    result = subprocess.run(['sbatch', 'sbatch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
    stdout = result.stdout.decode('utf-8').strip()
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Result\n=============\n{stdout}\n=============\n")
    return stdout


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def main():
    bp = Path.home().joinpath(".idmtools").joinpath("singularity-bridge")
    basicConfig(level=DEBUG, handlers=[
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
