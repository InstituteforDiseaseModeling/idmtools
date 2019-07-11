import signal
from logging import getLogger
import logging
from logging.handlers import QueueHandler, RotatingFileHandler, QueueListener
from multiprocessing import Queue


logging_queue: Queue = None


def register_stop_logger_signal_handler(listener: QueueListener):
    """
    Setups a signal handler for common processing stopping events where we should try to stop the log gracefully

    Args:
        listener (QueueListener): Listern to attempt to stop

    Returns:
        None
    """
    def stop_logger_handle(signal, frame):
        listener.stop()

    for sig in [signal.CTRL_C_EVENT, signal.CTRL_BREAK_EVENT, signal.SIGTERM, signal.SIGKILL, signal.SIGINT]:
        signal.signal(sig, stop_logger_handle)


def setup_logging():
    """
    Default setup logging function
    Returns:

    """
    global logging_queue
    if logging_queue is None:
        logging_queue = Queue()
        try:
            # Remove all handlers associated with the root logger object.
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
        except KeyError as e:
            # set root the use send log messages to a queue by default
            queue_handler = QueueHandler(logging_queue)
            root = logging.getLogger()
            root.addHandler(queue_handler)


            # see https://docs.python.org/3/library/logging.handlers.html#queuelistener
            # setup file logger handler that rotates after 10 mb of logging and keeps 5 copies
            handler = RotatingFileHandler('idmtools.log', maxBytes= (2 ** 20) * 10, backupCount=5)
            # now attach a listener to the logging queue and redirect all messages to our handler
            listener = QueueListener(logging_queue, handler)
            listener.start()
            # register a stop signal
            register_stop_logger_signal_handler(listener)

            # set the default level for comps logging to warning as well since this will be picked up in idmtools
            # log
            comps_logger = getLogger("COMPS")
            comps_logger.setLevel(logging.WARN)


def init_logger(name=None):
    # Ensure logger has been initialized using the config
    setup_logging()

    return getLogger(name)