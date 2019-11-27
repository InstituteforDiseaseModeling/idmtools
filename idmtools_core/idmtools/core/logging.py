from signal import SIGTERM, SIGINT, signal
from logging import getLogger
import logging
from logging.handlers import QueueHandler, RotatingFileHandler, QueueListener
from multiprocessing import Queue
import os
from typing import NoReturn, Union

import coloredlogs as coloredlogs

listener = None
logging_queue = None


class IDMQueueListener(QueueListener):
    def dequeue(self, block):
        """
        Dequeue a record and return it, optionally blocking.

        The base implementation uses get. You may want to override this method
        if you want to use timeouts or work with custom queue implementations.
        """
        try:
            return self.queue.get(block)
        except EOFError:
            return None


def setup_logging(level: Union[int, str] = logging.WARN, log_filename: str = 'idmtools.log',
                  console: Union[str, bool] = False) -> QueueListener:
    """
    Set up logging.

    Args:
        level: Log level. Default to warning. This should be either a string that matches a log level
            from logging or an int that represent that level.
        log_filename: Name of file to log messages to.
        console: When set to True or the strings "1", "y", "yes", or "on", console logging will be enabled.

    Returns:
        Returns the ``QueueListener`` created that writes the log messages. In advanced scenarios with
        multi-processing, you may need to manually stop the logger.
    """
    global listener, logging_queue
    if type(level) is str:
        level = logging.getLevelName(level)
    if type(console) is str:
        console = console.lower() in ['1', 'y', 'yes', 'on']

    # get a file handler
    root = logging.getLogger()
    # allow setting the debug of logger via environment variable
    root.setLevel(logging.DEBUG if os.getenv('IDM_TOOLS_DEBUG', False) else level)

    if logging_queue is None:
        # We only one to do this setup once per process. Having the logging_queue setup help prevent that issue
        # get a file handler
        root = logging.getLogger()
        if os.getenv('IDM_TOOLS_DEBUG', False) or level == logging.DEBUG:
            # Enable detailed logging format
            format_str = '%(asctime)s.%(msecs)d %(pathname)s:%(lineno)d %(funcName)s ' \
                         '[%(levelname)s] (%(process)d,(%(thread)d) - %(message)s'
        else:
            format_str = '%(asctime)s.%(msecs)d %(funcName)s: [%(levelname)s] - %(message)s'
        formatter = logging.Formatter(format_str)
        file_handler = RotatingFileHandler(log_filename, maxBytes=(2 ** 20) * 10, backupCount=5)
        file_handler.setFormatter(formatter)

        exclude_logging_classes()
        logging_queue = Queue()
        try:
            # Remove all handlers associated with the root logger object.
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
        except KeyError as e:  # noqa F841
            pass
        # set root the use send log messages to a queue by default
        queue_handler = QueueHandler(logging_queue)
        root.addHandler(queue_handler)

        if console:
            coloredlogs.install(level='DEBUG')

        # see https://docs.python.org/3/library/logging.handlers.html#queuelistener
        # setup file logger handler that rotates after 10 mb of logging and keeps 5 copies

        # now attach a listener to the logging queue and redirect all messages to our handler
        listener = IDMQueueListener(logging_queue, file_handler)
        listener.start()
        # register a stop signal
        register_stop_logger_signal_handler(listener)

    exclude_logging_classes()
    return listener


def exclude_logging_classes():
    # remove comps by default
    for l in ['urllib3', 'COMPS', 'paramiko']:
        comps_logger = getLogger(l)
        comps_logger.setLevel(logging.WARN)


def register_stop_logger_signal_handler(listener) -> NoReturn:
    """
    Register a signal watcher that will stop our logging gracefully in the case of queue based logging.

    Args:
        listener: The log listener object.

    Returns:
        None
    """

    def stop_logger(*args, **kwargs):
        listener.stop()

    for s in [SIGINT, SIGTERM]:
        signal(s, stop_logger)
