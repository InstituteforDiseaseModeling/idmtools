"""
idmtools logging module.

We configure our logging here, manage multi-process logging, alternate logging level, and additional utilities to manage logging.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import os
import sys
import threading
import time
from contextlib import suppress
from dataclasses import dataclass
from logging import getLogger
from logging.handlers import RotatingFileHandler
from typing import Union, Optional
import coloredlogs as coloredlogs
from idmtools.core import TRUTHY_VALUES


LOGGING_STARTED = False
LOGGING_FILE_STARTED = False
LOGGING_FILE_HANDLER = None

VERBOSE = 15
NOTICE = 25
SUCCESS = 35
CRITICAL = 50


@dataclass
class IdmToolsLoggingConfig:
    """
    Defines the config options available for idmtools logs.
    """
    level: Union[str, int] = logging.WARN
    filename: Optional[str] = 'idmtools.log'
    console: bool = False
    file_level: Union[str, int] = 'DEBUG'
    force: bool = False
    file_log_format_str: str = None
    user_log_format_str: str = '%(message)s'
    use_colored_logs: bool = True

    def __post_init__(self):
        """
        Validates logging config creation
        """
        if isinstance(self.use_colored_logs, str):
            self.use_colored_logs = self.use_colored_logs.lower() in TRUTHY_VALUES

        if type(self.console) is str:
            self.console = self.console.lower() in TRUTHY_VALUES
        # ensure level is a logging level
        for attr in ['level', 'file_level']:
            if isinstance(getattr(self, attr), str):
                setattr(self, attr, logging.getLevelName(getattr(self, attr)))
        # set default name is not set.
        if self.filename is None:
            self.filename = 'idmtools.log'
        # ensure whitespace is gone
        self.filename = self.filename.strip()
        # disable file logging when set to -1
        if self.filename == "-1":
            self.filename = None
        # set default file log format str
        if self.file_log_format_str is None:
            if self.filename == logging.DEBUG:
                # Enable detailed logging format
                self.file_log_format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] (%(process)d,%(thread)d) - %(message)s'
            else:
                self.file_log_format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] - %(message)s'


class MultiProcessSafeRotatingFileHandler(RotatingFileHandler):
    """
    Multi-process safe logger
    """

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        """
        See RotatingFileHandler for full details on arguments

        Args:
            filename:
            mode:
            maxBytes:
            backupCount:
            encoding:
            delay:
        """
        super().__init__(filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)
        self.logger_lock = threading.Lock()

    def handle(self, record: logging.LogRecord) -> None:
        """
        Thread safe logger
        Args:
            record: Record to handle

        Returns:

        """
        self.logger_lock.acquire()
        try:
            super(MultiProcessSafeRotatingFileHandler, self).handle(record)
        finally:
            self.logger_lock.release()

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
        try:
            print(record.msg)
        except:  # noqa: E722
            pass


def setup_logging(logging_config: IdmToolsLoggingConfig, force: bool = False) -> None:
    """
    Set up logging.

    Args:
        logging_config: IdmToolsLoggingConfig that defines our config
        force: Force setup, even if we have done it once

    Returns:
        Returns None

    See Also:
        For logging levels, see https://coloredlogs.readthedocs.io/en/latest/api.html#id26
    """
    global LOGGING_STARTED, LOGGING_FILE_STARTED, LOGGING_FILE_HANDLER
    if not LOGGING_STARTED or force:
        logging.addLevelName(15, 'VERBOSE')
        logging.addLevelName(25, 'NOTICE')
        logging.addLevelName(35, 'SUCCESS')

        # get a file handler
        root = logging.getLogger()
        user = logging.getLogger('user')
        # allow setting the debug of logger via environment variable
        root.setLevel(logging_config.level)
        user.setLevel(logging.DEBUG)

        if not LOGGING_FILE_STARTED or force:
            # reset logging and remove all handlers and delete our current handler
            if LOGGING_FILE_HANDLER is not None:
                reset_logging_handlers()
                del LOGGING_FILE_HANDLER
            LOGGING_FILE_HANDLER = setup_handlers(logging_config)
            if LOGGING_FILE_HANDLER:
                LOGGING_FILE_STARTED = True
        setup_user_logger(logging_config)

        if root.isEnabledFor(logging.DEBUG):
            from idmtools import __version__
            root.debug(f"idmtools core version: {__version__}")


def setup_handlers(logging_config: IdmToolsLoggingConfig):
    """
    Setup Handlers for Global and user Loggers.

    Args:
        logging_config: Logging config

    Returns:
        FileHandler or None
    """
    # We only one to do this setup once per process. Having the logging_queue setup help prevent that issue
    # get a file handler

    exclude_logging_classes()
    reset_logging_handlers()
    file_handler = None
    if logging_config.filename:
        formatter = logging.Formatter(logging_config.file_log_format_str)
        # set the logging to either common level or the file-level
        file_handler = set_file_logging(logging_config, formatter)

    if logging_config.console or not logging_config.filename:
        if logging_config.use_colored_logs:
            coloredlogs.install(level=logging_config.level, milliseconds=True, stream=sys.stdout)
        else:
            # Mainly for test/local platform
            print_handler = PrintHandler(level=logging_config.level)
            getLogger().addHandler(print_handler)
    return file_handler


def setup_user_logger(logging_config: IdmToolsLoggingConfig):
    """
    Setup the user logger. This logger is meant for user output only.

    Args:
        logging_config: Logging config object.

    Returns:
        None
    """
    # check if we should use console
    if logging_config.console and logging_config.use_colored_logs in TRUTHY_VALUES:
        coloredlogs.install(logger=getLogger('user'), level=logging.DEBUG, fmt='%(message)s', stream=sys.stdout)
    else:  # no matter if console is set, we should fallback to print handler here
        formatter = logging.Formatter(fmt='%(message)s')
        handler = PrintHandler(level=logging.DEBUG)
        handler.setFormatter(formatter)
        # should everything be printed using the print logger or filename was set to be empty. This means log
        # everything to the screen without color
        getLogger('user').addHandler(handler)


def set_file_logging(logging_config: IdmToolsLoggingConfig, formatter: logging.Formatter):
    """
    Set File Logging.

    Args:
        logging_config: Logging config object.
        formatter:  Formater obj

    Returns:
        Return File handler
    """
    file_handler = create_file_handler(logging_config.file_level, formatter, logging_config.filename)
    if file_handler is None:
        # We had an issue creating file handler, so let's try using default name + pids
        for i in range(64):  # We go to 64. This is a reasonable max id for any computer we might actually run item.
            file_handler = create_file_handler(logging_config.filename, formatter, f"{logging_config.file_level}.{i}.log")
            if file_handler:
                break
        if file_handler is None:
            raise ValueError("Could not file a valid log. Either all the files are opened or you are on a read-only filesystem. You can disable file-based logging by setting")
    logging.root.addHandler(file_handler)
    return file_handler


def create_file_handler(file_level, formatter: logging.Formatter, filename: str):
    """
    Create a MultiProcessSafeRotatingFileHandler for idmtools.log.

    Args:
        file_level: Level to log to file
        formatter: Formatter to set on the handler
        filename: Filename to use

    Returns:
        SafeRotatingFileHandler with properties provided
    """
    try:
        file_handler = MultiProcessSafeRotatingFileHandler(filename, maxBytes=(2 ** 20) * 10, backupCount=5)
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
        items_to_exclude = ['urllib3', 'paramiko', 'matplotlib', 'COMPS']
    # remove comps by default
    for item in items_to_exclude:
        other_logger = getLogger(item)
        other_logger.setLevel(logging.WARN)
