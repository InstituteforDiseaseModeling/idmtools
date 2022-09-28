"""Provides facility to watch bridge files."""
import time
from logging import getLogger
from os import PathLike
from watchdog.events import FileSystemEventHandler
from watchdog_gevent import Observer

from idmtools_slurm_utils.utils import process_job

logger = getLogger()


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
