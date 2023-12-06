"""
idmtools logging module.

We configure our logging here, manage multi-process logging, alternate logging level, and additional utilities to manage logging.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import os
import sys
import time
import threading
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
    #: Console level
    level: Union[str, int] = logging.WARN
    #: Filename for idmtools logs
    filename: Optional[str] = 'idmtools.log'
    #: Toggle to enable/disable console logging
    console: bool = False
    #: File log level
    file_level: Union[str, int] = 'DEBUG'
    #: Should we force reload
    force: bool = False
    #: File format string. See https://docs.python.org/3/library/logging.html#logrecord-attributes for format vars
    file_log_format_str: str = None
    #: Logging format. See https://docs.python.org/3/library/logging.html#logrecord-attributes for format vars
    user_log_format_str: str = '%(message)s'
    #: Toggle to enable/disable coloredlogs
    use_colored_logs: bool = True
    #: Toggle user output. This should only be used in certain situations like CLI's that output JSON
    user_output: bool = True
    #: Toggle enable file logging
    enable_file_logging: Union[str, bool] = True

    def __post_init__(self):
        """
        Validates logging config creation.
        """
        # load the user input from string
        if isinstance(self.user_output, str):
            self.user_output = self.user_output.lower() in TRUTHY_VALUES

        # load color logs from string
        if isinstance(self.use_colored_logs, str):
            self.use_colored_logs = self.use_colored_logs.lower() in TRUTHY_VALUES

        # load console from string
        if isinstance(self.console, str):
            self.console = self.console.lower() in TRUTHY_VALUES

        if type(self.enable_file_logging) is str:
            self.enable_file_logging = self.enable_file_logging.lower() in TRUTHY_VALUES

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
        if self.filename == "-1" or not self.enable_file_logging:
            self.filename = None

        # handle special case
        if not self.enable_file_logging and self.console is None:
            self.console = True

        # set default file log format str
        if self.file_log_format_str is None:
            if self.file_level == logging.DEBUG:
                # Enable detailed logging format
                self.file_log_format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] (%(process)d,%(thread)d) - %(message)s'
            else:
                self.file_log_format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] - %(message)s'


class MultiProcessSafeRotatingFileHandler(RotatingFileHandler):
    """
    Multi-process safe logger.
    """

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        """
        See RotatingFileHandler for full details on arguments.

        Args:
            filename:Filename to use
            mode:Mode
            maxBytes: Max bytes
            backupCount: Total backups
            encoding: Encoding
            delay: Delay
        """
        super().__init__(filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding,
                         delay=delay)
        self.logger_lock = threading.Lock()

    def handle(self, record: logging.LogRecord) -> None:
        """
        Thread safe logger.

        Args:
            record: Record to handle

        Returns:
            None
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


def setup_logging(logging_config: IdmToolsLoggingConfig) -> None:
    """
    Set up logging.

    Args:
        logging_config: IdmToolsLoggingConfig that defines our config

    Returns:
        Returns None

    See Also:
        For logging levels, see https://coloredlogs.readthedocs.io/en/latest/api.html#id26
    """
    global LOGGING_STARTED, LOGGING_FILE_STARTED, LOGGING_FILE_HANDLER
    if not LOGGING_STARTED or logging_config.force:
        # reset logging and remove all handlers and delete our current handler
        reset_logging_handlers()

        logging.addLevelName(15, 'VERBOSE')
        logging.addLevelName(25, 'NOTICE')
        logging.addLevelName(35, 'SUCCESS')

        # get a file handler
        root = logging.getLogger()
        user = logging.getLogger('user')
        # allow setting the debug of logger via environment variable
        root.setLevel(logging_config.level)
        user.setLevel(logging.DEBUG)

        # file logging config
        if not LOGGING_FILE_STARTED or logging_config.force:
            LOGGING_FILE_HANDLER = setup_handlers(logging_config)
            if LOGGING_FILE_HANDLER:
                LOGGING_FILE_STARTED = True

        # Show we enable user output. The only time we really should not do this is for specific CLI use cases
        # # such as json output
        setup_user_logger(logging_config)

        if root.isEnabledFor(logging.DEBUG):
            from idmtools import __version__
            root.debug(f"idmtools core version: {__version__}")

        # python logger creates default stream handler when no handlers are set so create null handler
        if len(root.handlers) == 0:
            root.addHandler(logging.NullHandler())

        # set file logging stated
        LOGGING_FILE_STARTED = True
        # set logging stated
        LOGGING_STARTED = True


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
    file_handler = None
    if logging_config.filename:
        formatter = logging.Formatter(logging_config.file_log_format_str)
        # set the logging to either common level or the file-level
        file_handler = set_file_logging(logging_config, formatter)

    # If user output is enabled and console is enabled
    if logging_config.user_output and logging_config.console:
        # is colored logging enabled? if so, add our logger
        # note: this will be used for user logging as well
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
    if logging_config.user_output and not logging_config.console:
        # is colored logs enabled? If so, make the user logger a coloredlogger
        if logging_config.use_colored_logs:
            coloredlogs.install(logger=getLogger('user'), level=VERBOSE, fmt='%(message)s', stream=sys.stdout)
        else:  # fall back to a print handler
            setup_user_print_logger()


def setup_user_print_logger():
    """
    Setup a print based logger for user messages.

    Returns:
        None
    """
    formatter = logging.Formatter(fmt='%(message)s')
    handler = PrintHandler(level=VERBOSE)
    handler.setFormatter(formatter)
    # should everything be printed using the print logger or filename was set to be empty. This means log
    # everything to the screen without color
    getLogger('user').addHandler(handler)


def set_file_logging(logging_config: IdmToolsLoggingConfig, formatter: logging.Formatter):
    """
    Set File Logging.

    Args:
        logging_config: Logging config object.
        formatter:  Formatter obj

    Returns:
        Return File handler
    """
    file_handler = create_file_handler(logging_config.file_level, formatter, logging_config.filename)
    if file_handler is None:
        # We had an issue creating file handler, so let's try using default name + pids
        for i in range(64):  # We go to 64. This is a reasonable max id for any computer we might actually run item.
            file_handler = create_file_handler(logging_config.file_level, formatter,
                                               f"{logging_config.filename}.{i}.log")
            if file_handler:
                break
        if file_handler is None:
            raise ValueError(
                "Could not file a valid log. Either all the files are opened or you are on a read-only filesystem. You can disable file-based logging by setting")
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
    global LOGGING_STARTED, LOGGING_FILE_STARTED, LOGGING_FILE_HANDLER

    with suppress(KeyError):
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
    # Clean up file handler now
    LOGGING_FILE_STARTED = False
    LOGGING_STARTED = False
    LOGGING_FILE_HANDLER = None


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
