import atexit
import logging
import sys
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


class IDMQueueListener(QueueListener):

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
    def prepare(self, record):
        try:
            return super().prepare(record)
        except ImportError:
            pass


class PrintHandler(logging.Handler):
    def handle(self, record: logging.LogRecord) -> None:
        print(record.message)


def setup_logging(level: Union[int, str] = logging.WARN, log_filename: str = 'idmtools.log',
                  console: Union[str, bool] = False, file_level: str = 'DEBUG', force: bool = False) -> QueueListener:
    """
    Set up logging.

    Args:
        level: Log level. Default to warning. This should be either a string that matches a log level
            from logging or an int that represent that level.
        log_filename: Name of file to log messages to. If set to empty string, file logging is disabled
        console: When set to True or the strings "1", "y", "yes", or "on", console logging will be enabled.
        file_level: Level for logging in file
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

        # get a file handler
        root = logging.getLogger()
        user = logging.getLogger('user')
        # allow setting the debug of logger via environment variable
        root.setLevel(level)
        user.setLevel(logging.DEBUG)

        if LOGGING_NAME is None or force:
            file_handler = setup_handlers(level, log_filename, console, file_level)

            # see https://docs.python.org/3/library/logging.handlers.html#queuelistener
            # setup file logger handler that rotates after 10 mb of logging and keeps 5 copies

            # now attach a listener to the logging queue and redirect all messages to our handler
            if (LISTENER is None and file_handler) or (force and file_handler):
                LISTENER = IDMQueueListener(LOGGING_NAME, file_handler)
                LISTENER.start()
                # register a stop signal
                register_stop_logger_signal_handler(LISTENER)
        if root.isEnabledFor(logging.DEBUG):
            from idmtools import __version__
            root.debug(f"idmtools core version: {__version__}")
        LOGGING_STARTED = True
        return LISTENER
    return None


def setup_handlers(level: int, log_filename, console: bool = False, file_level: int = None):
    """
    Setup Handlers for Global and user Loggers

    Args:
        level: Level for the common logger
        log_filename: Log filename. Set to "" to disable file based logging
        console: Enable console based logging only
        file_level: File Level logging

    Returns:
        FileHandler or None
    """
    global LOGGING_NAME
    # We only one to do this setup once per process. Having the logging_queue setup help prevent that issue
    # get a file handler

    exclude_logging_classes()
    reset_logging_handlers()
    file_handler = None
    if len(log_filename):
        if level == logging.DEBUG:
            # Enable detailed logging format
            format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] (%(process)d,%(thread)d) - %(message)s'
        else:
            format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] - %(message)s'
        formatter = logging.Formatter(format_str)
        # set the logging to either common level or the filelevel
        file_handler = set_file_logging(file_level if file_level else level, formatter, log_filename)

    if console or len(log_filename) == 0:
        coloredlogs.install(level=level, milliseconds=True, stream=sys.stdout)
    setup_user_logger(console or len(log_filename) == 0)
    return file_handler


def setup_user_logger(console: bool):
    """
    Setup the user logger. This logger is meant for user output only

    Args:
        console: Is Console enabled. If so, we don't install a user loger

    Returns:

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


def set_file_logging(file_level: int, formatter: logging.Formatter, log_filename: str):
    """
    Set File Logging

    Args:
        file_level: File Level
        formatter: Formatter
        log_filename: Log Filename

    Returns:
        Return File handler
    """
    global LOGGING_NAME
    file_handler = create_file_handler(file_level, formatter, log_filename)
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
    logging.root.addHandler(queue_handler)
    logging.getLogger('user').addHandler(queue_handler)
    return file_handler


def create_file_handler(file_level, formatter, log_filename):
    try:
        file_handler = RotatingFileHandler(log_filename, maxBytes=(2 ** 20) * 10, backupCount=5)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
    except PermissionError:
        return None
    return file_handler


def reset_logging_handlers():
    try:
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
    except KeyError as e:  # noqa F841
        pass


def exclude_logging_classes(items_to_exclude=None):
    if items_to_exclude is None:
        items_to_exclude = ['urllib3', 'COMPS', 'paramiko', 'matplotlib']
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
        try:
            listener.stop()
        except Exception:
            pass

    for s in [SIGINT, SIGTERM]:
        try:
            signal(s, stop_logger)
        except ValueError as ex:
            if ex.args[0] == "signal only works in main thread":
                pass

    atexit.register(stop_logger)
