from contextlib import suppress

import allure
import concurrent
import allure
import os
import sys
import threading
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from logging import DEBUG, getLogger
from unittest import TestCase, skip

from idmtools.core.logging import setup_logging, IdmToolsLoggingConfig
from idmtools_test.utils.decorators import run_test_in_n_seconds


def log_process_id():
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    logger.info(f'Hello from process {os.getpid()}')
    return True


# Check if we have a debugger running. If we are, expect fifth of the performance, espcially the ProcessPoolExecutor
# portions since that is quite slow in debugger
LOG_TESTS_TO_RUN = 50000 if getattr(sys, 'gettrace', None) is None else 5000


@skip
@allure.story("Core")
@allure.suite("idmtools_core")
class TestLoggingBenchmark(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setup_logging(IdmToolsLoggingConfig())

    @run_test_in_n_seconds(10)
    def test_logger_threaded_performance(self):
        # our loggers are our of scope of package name so what be on
        # unless we enable it
        logger = getLogger(__name__)
        logger.setLevel(DEBUG)

        def log_thread_id():
            logger.info(f'Hello from thread {threading.get_ident()}')
            return True

        with ThreadPoolExecutor() as p:
            futures = [p.submit(log_thread_id) for i in range(LOG_TESTS_TO_RUN)]
            for future in concurrent.futures.as_completed(futures):
                self.assertTrue(future.result())

    @run_test_in_n_seconds(10)
    def test_logger_processes_performance(self):
        with ProcessPoolExecutor() as p:
            futures = [p.submit(log_process_id) for i in range(LOG_TESTS_TO_RUN)]
            for future in concurrent.futures.as_completed(futures):
                self.assertTrue(future.result())

    def test_logging_rotation_safe(self):
        # create all backups so we trigger delete and move
        logs = []
        try:
            for i in range(1, 5):
                with suppress(PermissionError):
                    logs.append(open(f"idmtools.log.{i}", "w"))

                # now write to the log
                logger = getLogger("test_logging_rotation_safe")
                for i in range(125000):
                    logger.info(f"{i}")
        finally:
            del logs
