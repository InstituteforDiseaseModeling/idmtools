import datetime
import importlib
import importlib.util
import os
import threading
from concurrent.futures import Executor, as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
from logging import getLogger, DEBUG
from typing import Callable, Union, Optional, Type

logger = getLogger(__name__)


class abstractstatic(staticmethod):
    """
    A decorator for defining a method both as static and abstract.
    """
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True


def optional_decorator(decorator: Callable, condition: Union[bool, Callable[[], bool]]):
    if callable(condition):
        condition = condition()

    def decorate_in(func):
        if condition:
            func = decorator(func)

        @wraps
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    return decorate_in


class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


def cache_for(ttl=datetime.timedelta(minutes=1)):
    def wrap(func):
        time, value = None, None

        @wraps(func)
        def wrapped(*args, **kw):
            # if we are testing, disable caching of functions as it complicates test-all setups
            from idmtools.core import TRUTHY_VALUES
            if os.getenv('TESTING', '0').lower() in TRUTHY_VALUES:
                return func(*args, **kw)

            nonlocal time
            nonlocal value
            now = datetime.datetime.now()
            if not time or now - time > ttl:
                value = func(*args, **kw)
                time = now
            return value

        return wrapped

    return wrap


def optional_yaspin_load(*yargs, **ykwargs) -> Callable:
    """
    Adds a CLI spinner to a function if:

    * yaspin package is present.
    * NO_SPINNER environment variable is not defined.

    Args:
        *yargs: Arguments to pass to yaspin constructor.
        **ykwargs: Keyword arguments to pass to yaspin constructor.

    Examples:
        ::

            @optional_yaspin_load(text="Loading test", color="yellow")
            def test():
                time.sleep(100)

    Returns:
        A callable wrapper function.
    """
    has_yaspin = importlib.util.find_spec("yaspin")
    spinner = None
    if has_yaspin and not os.getenv('NO_SPINNER', False):
        from yaspin import yaspin
        spinner = yaspin(*yargs, **ykwargs)

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if spinner and not os.getenv('NO_SPINNER', False):
                spinner.start()
            try:
                kwargs['spinner'] = spinner
                result = func(*args, **kwargs)
            except Exception as e:
                if spinner:
                    spinner.stop()
                raise e
            if spinner:
                spinner.stop()
            return result

        return wrapper

    return decorate


class ParallelizeDecorator:
    """
    ParallelizeDecorator allows you to easily parallelize a group of code. A simple of example would be

    Examples:
        ::

            op_queue = ParallelizeDecorator()

            class Ops:
                op_queue.parallelize
                def heavy_op():
                    time.sleep(10)

                def do_lots_of_heavy():
                    futures = [self.heavy_op() for i in range(100)]
                    results = op_queue.get_results(futures)
    """

    def __init__(self, queue=None, pool_type: Optional[Type[Executor]] = ThreadPoolExecutor):
        if queue is None:
            self.queue = pool_type()
        else:
            self.queue = queue

    def parallelize(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            future = self.queue.submit(func, *args, **kwargs)
            return future

        return wrapper

    def join(self):
        return self.queue.join()

    def get_results(self, futures, ordered=False):
        results = []
        if ordered:
            for f in futures:
                results.append(f.result())
        else:
            for f in as_completed(futures):
                results.append(f.result())

        if logger.isEnabledFor(DEBUG):
            logger.debug("Parallelize Total Results: " + str(results))
        return results

    def __del__(self):
        del self.queue
