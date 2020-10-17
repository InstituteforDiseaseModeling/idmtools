import atexit
import logging
import os
import sys
from logging import getLogger
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from multiprocessing import Queue
from signal import SIGINT, signal, SIGTERM
from typing import NoReturn, Union
import coloredlogs as coloredlogs

listener = None
logging_queue = None
handlers = None

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
                  console: Union[str, bool] = False, file_level: str = 'DEBUG') -> QueueListener:
    """
    Set up logging.

    Args:
        level: Log level. Default to warning. This should be either a string that matches a log level
            from logging or an int that represent that level.
        log_filename: Name of file to log messages to.
        console: When set to True or the strings "1", "y", "yes", or "on", console logging will be enabled.
        file_level: Level for logging in file

    Returns:
        Returns the ``QueueListener`` created that writes the log messages. In advanced scenarios with
        multi-processing, you may need to manually stop the logger.

    See Also:
        For logging levels, see https://coloredlogs.readthedocs.io/en/latest/api.html#id26
    """
    global listener, logging_queue
    logging.addLevelName(15, 'VERBOSE')
    logging.addLevelName(25, 'NOTICE')
    logging.addLevelName(35, 'SUCCESS')
    logging.addLevelName(50, 'CRITICAL')

    if type(level) is str:
        level = logging.getLevelName(level)
    if type(file_level):
        file_level = logging.getLevelName(file_level)
    if type(console) is str:
        console = console.lower() in ['1', 'y', 'yes', 'on', 'true', 't']

    # get a file handler
    root = logging.getLogger()
    user = logging.getLogger('user')
    # allow setting the debug of logger via environment variable
    root.setLevel(logging.DEBUG if os.getenv('IDM_TOOLS_DEBUG', False) else level)
    user.setLevel(logging.DEBUG)

    if logging_queue is None:
        file_handler = setup_handlers(level, log_filename, console, file_level)

        # see https://docs.python.org/3/library/logging.handlers.html#queuelistener
        # setup file logger handler that rotates after 10 mb of logging and keeps 5 copies

        # now attach a listener to the logging queue and redirect all messages to our handler
        if listener is None:
            listener = IDMQueueListener(logging_queue, file_handler)
            listener.start()
            # register a stop signal
            register_stop_logger_signal_handler(listener)
    if root.isEnabledFor(logging.DEBUG):
        from idmtools import __version__
        root.debug(f"idmtools core version: {__version__}")
    return listener


def setup_handlers(level, log_filename, console: bool = False, file_level: str = 'DEBUG'):
    global logging_queue, handlers
    # We only one to do this setup once per process. Having the logging_queue setup help prevent that issue
    # get a file handler
    if os.getenv('IDM_TOOLS_DEBUG', '0') in ['1', 'y', 't', 'yes', 'true', 'on'] or level == logging.DEBUG:
        # Enable detailed logging format
        format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] (%(process)d,%(thread)d) - %(message)s'
    else:
        format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s [%(levelname)s] - %(message)s'
    formatter = logging.Formatter(format_str)
    try:
        file_handler = RotatingFileHandler(log_filename, maxBytes=(2 ** 20) * 10, backupCount=5)
        file_handler.setLevel()
        file_handler.setFormatter(formatter)
    except PermissionError:
        file_handler = logging.StreamHandler(sys.stdout)
        file_handler.setLevel(logging.getLevelName(file_level))
        file_handler.setFormatter(formatter)
        logging.warning(f"Could not open the log file '{log_filename}'. Using Console output instead")
        # disable normal logging
        console = False
    exclude_logging_classes()
    logging_queue = Queue()
    try:
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
    except KeyError as e:  # noqa F841
        pass

    # set root the use send log messages to a queue by default
    queue_handler = IDMQueueHandler(logging_queue)
    logging.root.addHandler(queue_handler)
    logging.getLogger('user').addHandler(queue_handler)

    # Use print based output. Mainly for test of CLI commands
    if os.getenv('IDMTOOLS_USE_PRINT_OUTPUT', 'F').lower() not in ['1', 'y', 't', 'yes', 'true', 'on']:
        if console or os.getenv('IDM_TOOLS_CONSOLE_LOGGING', 'F').lower() in ['1', 'y', 't', 'yes', 'true', 'on']:
            coloredlogs.install(level=level, milliseconds=True, stream=sys.stdout)
        else:
            # install colored logs for user logger only
            coloredlogs.install(logger=getLogger('user'), level=VERBOSE, fmt='%(message)s', stream=sys.stdout)
    else:
        handler = PrintHandler(level=VERBOSE)
        handler.setLevel(VERBOSE)
        getLogger('user').addHandler(handler)
    handlers = logging.root.handlers
    return file_handler


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
