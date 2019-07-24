from signal import SIGTERM, SIGINT, signal
from logging import getLogger
import logging
from logging.handlers import QueueHandler, RotatingFileHandler, QueueListener
from multiprocessing import Queue
import os
from typing import NoReturn

listener = None
logging_queue = None


def setup_logging(level: int = logging.WARN, log_file_name:str = 'idmtools.log') -> QueueListener:
    """

    Args:
        level:
        log_file_name:

    Returns:

    """

    # get a file handler
    root = logging.getLogger()
    # allow setting the debug of logger via environment variable
    root.setLevel(logging.DEBUG if os.getenv('IDM_TOOL_DEBUG', False) else level)
    global listener, logging_queue

    if logging_queue is None:
        # We only one to do this setup once per process. Having the logging_queue setup help prevent that issue
        # get a file handler
        root = logging.getLogger()
        if os.getenv('IDM_TOOL_DEBUG', False) or level == logging.DEBUG:
            # Enable detailed logging format
            format_str = '%(asctime)s.%(msecs)d %(pathname)s/%(filename)s:%(lineno)d %(funcName)-s: ' \
                         '[%(levelname)s] (%(process)d,(%(thread)d) - %(message)s'
        else:
            format_str = '%(asctime)s.%(msecs)d %(funcName)-s: [%(levelname)s] - %(message)s'
        formatter = logging.Formatter(format_str)
        file_handler = RotatingFileHandler(log_file_name, maxBytes=(2 ** 20) * 10, backupCount=5)
        file_handler.setFormatter(formatter)

        comps_logger = getLogger("COMPS")
        comps_logger.setLevel(logging.WARN)
        logging_queue = Queue()
        try:
            # Remove all handlers associated with the root logger object.
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
        except KeyError as e:
            pass
        # set root the use send log messages to a queue by default
        queue_handler = QueueHandler(logging_queue)
        root.addHandler(queue_handler)

        # see https://docs.python.org/3/library/logging.handlers.html#queuelistener
        # setup file logger handler that rotates after 10 mb of logging and keeps 5 copies

        # now attach a listener to the logging queue and redirect all messages to our handler
        listener = QueueListener(logging_queue, file_handler)
        listener.start()
        # register a stop signal
        register_stop_logger_signal_handler(listener)

    exclude_logging_classes()
    return listener


def exclude_logging_classes():
    # remove comps by default
    comps_logger = getLogger("COMPS")
    comps_logger.setLevel(logging.WARN)


def register_stop_logger_signal_handler(listener) -> NoReturn:
    """
    Register a signal watcher that will stop our logging gracefully in the case of queue based logging

    Args:
        listener: Log listener object

    Returns:

    """
    def stop_logger():
        listener.stop()

    for s in [SIGINT, SIGTERM]:
        signal(s, stop_logger)