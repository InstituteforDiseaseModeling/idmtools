"""
idmtools logging module.

We configure our logging here, manage multi-process logging, alternate logging level, and additional utilities to manage logging.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import atexit
import logging
import os
import sys
import time
from contextlib import suppress
from logging import getLogger
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from multiprocessing import Queue
from signal import SIGINT, signal, SIGTERM
from typing import NoReturn, Union
import coloredlogs as coloredlogs
from idmtools.core import TRUTHY_VALUES

LISTENER = None
LOGGING_NAME = None
LOGGING_STARTED = False

VERBOSE = 15
NOTICE = 25
SUCCESS = 35
CRITICAL = 50


class SafeRotatingFileHandler(RotatingFileHandler):
    """
    SafeRotatingFileHandler allows us to handle errors that occur during roll-over of multi-process log events.
    """

    def doRollover(self) -> None:
        """
        Perform rollover safely.

        We loop and try to move the log file. If we encounter an issue, we try to retry three times.
        If we failed after three times, we try a new process id appended to file name.

        Returns:
            None
        """
        attempts = 0
        while True:
            try:
                super().doRollover()
                break
            except PermissionError:
                attempts += 1
                if attempts > 3:
                    # add a pid to make unique or expand
                    self.baseFilename += f".{os.getpid()}"
                    attempts = 0
                time.sleep(0.08)


class IDMQueueListener(QueueListener):
    """
    IDMQueueListener provided a queue for multi-processing logging.
    """

    def dequeue(self, block):
        """
        Dequeue a record and return it, optionally blocking.

        The base implementation uses get. You may want to override this method
        if you want to use timeouts or work with custom queue implementations.
        """
        try:
            result = self.queue.get(block)
            return result
        except EOFError:
            return None


class IDMQueueHandler(QueueHandler):
    """
    IDMQueueHandler provided a log handler that references a queue.
    """

    def prepare(self, record):
        """
        Prepare a record for queuing.

        Args:
            record: Record to queue

        Returns:
            Queue record
        """
        with suppress(ImportError):
            return super().prepare(record)


class PrintHandler(logging.Handler):
    """
    A simple print handler. Used in cases where logging fails.
    """

    def handle(self, record: logging.LogRecord) -> None:
        """
        Simple log handler that prints to stdout.

        Args:
            record: Record to print

        Returns:
            None
        """
        print(record.message)


def setup_logging(level: Union[int, str] = logging.WARN, filename: str = 'idmtools.log',
                  console: Union[str, bool] = False, file_level: str = 'DEBUG',
                  enable_file_logging: Union[str, bool] = True, force: bool = False) -> QueueListener:
    """
    Set up logging.

    Args:
        level: Log level. Default to warning. This should be either a string that matches a log level
            from logging or an int that represent that level.
        filename: Name of file to log messages to. If set to -1, file logging is disabled
        console: When set to True or the strings "1", "y", "yes", or "on", console logging will be enabled.
        file_level: Level for logging in file
        enable_file_logging: When set to True or any of the values allowed for console, writes idmtools logging to a file
        force: Force setup, even if we have done it once

    Returns:
        Returns the ``QueueListener`` created that writes the log messages. In advanced scenarios with
        multi-processing, you may need to manually stop the logger.

    See Also:
        For logging levels, see https://coloredlogs.readthedocs.io/en/latest/api.html#id26
    """
    global LISTENER, LOGGING_NAME, LOGGING_STARTED
    if not LOGGING_STARTED or force:
        logging.addLevelName(15, 'VERBOSE')
        logging.addLevelName(25, 'NOTICE')
        logging.addLevelName(35, 'SUCCESS')

        if type(level) is str:
            level = logging.getLevelName(level)
        if type(file_level) is str:
            file_level = logging.getLevelName(file_level)
        if type(console) is str:
            console = console.lower() in TRUTHY_VALUES
        if type(enable_file_logging) is str:
            enable_file_logging = enable_file_logging.lower() in TRUTHY_VALUES

        # get a file handler
        root = logging.getLogger()
        user = logging.getLogger('user')
        # allow setting the debug of logger via environment variable
        root.setLevel(level)
        user.setLevel(logging.DEBUG)

        if LOGGING_NAME is None or force:
            filename = filename.strip()
            if filename == "-1" or not enable_file_logging:
                filename = ""
            file_handler = setup_handlers(level, filename, console, file_level)

            # see https://docs.python.org/3/library/logging.handlers.html#queuelistener
            # setup file logger handler that rotates after 10 mb of logging and keeps 5 copies

            # now attach a listener to the logging queue and redirect all messages to our handler
            if (LISTENER is None and file_handler) or (force and file_handler):
                LISTENER = IDMQueueListener(LOGGING_NAME, file_handler)
                LISTENER.start()
                # register a stop signal
                register_stop_logger_signal_handler(LISTENER)
            # python logger creates default stream handler when no handlers are set so create null handler
            if not file_handler and not console:
                root.addHandler(logging.NullHandler())
        if root.isEnabledFor(logging.DEBUG):
            from idmtools import __version__
            root.debug(f"idmtools core version: {__version__}")
        LOGGING_STARTED = True
        return LISTENER
    return None


def setup_handlers(level: int, filename, console: bool, file_level: int):
    """
    Setup Handlers for Global and user Loggers.

    Args:
        level: Level for the common logger
        filename: Log filename. Set to "" to disable file based logging
        file_level: File Level logging
        console: Enable console based logging


    Returns:
        FileHandler or None
    """
    global LOGGING_NAME
    # We only one to do this setup once per process. Having the logging_queue setup help prevent that issue
    # get a file handler

    exclude_logging_classes()
    reset_logging_handlers()
    file_handler = None
    if len(filename):
        if level == logging.DEBUG:
            # Enable detailed logging format
            format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] (%(process)d,%(thread)d) - %(message)s'
        else:
            format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] - %(message)s'
        formatter = logging.Formatter(format_str)
        # set the logging to either common level or the filelevel
        file_handler = set_file_logging(file_level if file_level else level, formatter, filename)

    if console or len(filename) == 0:
        coloredlogs.install(level=level, milliseconds=True, stream=sys.stdout)
    setup_user_logger(console or len(filename) == 0)
    return file_handler


def setup_user_logger(console: bool):
    """
    Setup the user logger. This logger is meant for user output only.

    Args:
        console: Is Console enabled. If so, we don't install a user logger.

    Returns:
        None
    """
    from idmtools import IdmConfigParser
    # should we do colored log output. We only should if
    # 1. Console has been set in config/environment
    # 2. USE_PRINT_OUTPUT is not enabled
    if not console and IdmConfigParser.get_option("Logging", "USER_PRINT", fallback="F").lower() not in TRUTHY_VALUES:
        # install colored logs for user logger only
        coloredlogs.install(logger=getLogger('user'), level=logging.DEBUG, fmt='%(message)s', stream=sys.stdout)
    elif not console:  # This is mainly for test and local platform
        handler = PrintHandler(level=logging.DEBUG)
        # should everything be printed using the print logger or filename was set to be empty. This means log everything to the screen without color
        getLogger('user').addHandler(handler)


def set_file_logging(file_level: int, formatter: logging.Formatter, filename: str):
    """
    Set File Logging.

    Args:
        file_level: File Level
        formatter: Formatter
        filename: Log Filename

    Returns:
        Return File handler
    """
    global LOGGING_NAME
    file_handler = create_file_handler(file_level, formatter, filename)
    if file_handler is None:
        # We had an issue creating filehandler, so let's try using default name + pids
        for i in range(64):  # We go to 64. This is a reasonable max id for any computer we might actually run item.
            file_handler = create_file_handler(file_level, formatter, f"idmtools.{i}.log")
            if file_handler:
                break
        if file_handler is None:
            raise ValueError("Could not file a valid log. Either all the files are opened or you are on a read-only filesystem. You can disable file-based logging by setting")
    # disable normal logging
    LOGGING_NAME = Queue()
    # set root the use send log messages to a queue by default
    queue_handler = IDMQueueHandler(LOGGING_NAME)
    queue_handler.setLevel(file_level)
    logging.root.addHandler(queue_handler)
    logging.getLogger('user').addHandler(queue_handler)
    return file_handler


def create_file_handler(file_level, formatter: logging.Formatter, filename: str):
    """
    Create a SafeRotatingFileHandler for idmtools.log.

    Args:
        file_level: Level to log to file
        formatter: Formatter to set on the handler
        filename: Filename to use

    Returns:
        SafeRotatingFileHandler with properties provided
    """
    try:
        file_handler = SafeRotatingFileHandler(filename, maxBytes=(2 ** 20) * 10, backupCount=5)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
    except PermissionError:
        return None
    return file_handler


def reset_logging_handlers():
    """
    Reset all the logging handlers by removing the root handler.

    Returns:
        None
    """
    with suppress(KeyError):
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)


def exclude_logging_classes(items_to_exclude=None):
    """
    Exclude items from our logger by setting level to warning.

    Args:
        items_to_exclude: Items to exclude

    Returns:
        None
    """
    if items_to_exclude is None:
        items_to_exclude = ['urllib3', 'paramiko', 'matplotlib']
    # remove comps by default
    for item in items_to_exclude:
        other_logger = getLogger(item)
        other_logger.setLevel(logging.WARN)


def register_stop_logger_signal_handler(listener) -> NoReturn:
    """
    Register a signal watcher that will stop our logging gracefully in the case of queue based logging.

    Args:
        listener: The log listener object.

    Returns:
        None
    """

    def stop_logger(*args, **kwargs):
        with suppress(Exception):
            listener.stop()

    for s in [SIGINT, SIGTERM]:
        try:
            signal(s, stop_logger)
        except ValueError as ex:
            if ex.args[0] == "signal only works in main thread":
                pass

    atexit.register(stop_logger)
