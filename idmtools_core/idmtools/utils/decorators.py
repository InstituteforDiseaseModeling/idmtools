import datetime
import importlib
import importlib.util
import os
from functools import wraps
from typing import Callable, Union


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


class SingletonDecorator:
    """
    Wraps a class in a singleton decorator.

    Example:
        In the below example, we would print out *99* since *z* is referring to the same object as *x*::

            class Thing:
                y = 14
            Thing = SingletonDecorator(Thing)
            x = Thing()
            x.y = 99
            z = Thing()
            print(z.y)
    """
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)

        return self.instance


class LoadOnCallSingletonDecorator:
    """
    Additional class decorator that creates a singleton instance only when a method or attribute is accessed. 
    This is useful for expensive tasks like loading plugin factories that should only be executed when finally 
    needed and not on declaration.

    Examples:
        ::

            import time
            class ExpensiveFactory:
                def __init__():
                    time.sleep(1000)
                    self.items = ['a', 'b', 'c']
                def get_items():
                    return self.items

            ExpensiveFactory = LoadOnCallSingletonDecorator(ExpensiveFactory)
            ExpensiveFactory.get_items()
    """
    def __init__(self, klass):
        self.instance = SingletonDecorator(klass)
        self.created = False

    def __getattr__(self, item):
        self.ensure_created()
        return getattr(self.instance, item)

    def ensure_created(self):
        if not self.created:
            self.instance = self.instance()
            self.created = True


def cache_for(ttl=datetime.timedelta(minutes=1)):
    def wrap(func):
        time, value = None, None
        @wraps(func)
        def wrapped(*args, **kw):
            # if we are testing, disable caching of functions as it complicates test-all setups
            if os.getenv('TESTING', '0') .lower() in ['1', 'y', 'true', 'yes', 'on']:
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


def retry_function(func, wait=1.5, max_retries=5):
    """
    Retry the call to a function with some time in between.

    Args:
        func: The function to retry.
        time_between_tries: The time between retries, in seconds.
        max_retries: The maximum number of times to retry the call.

    Returns:
        None

    Example::

        @retry_function
        def my_func():
            pass

        @retry_function(max_retries=10, wait=2)
        def my_func():
            pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        retExc = None
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RuntimeError as r:
                # Immediately raise if this is an error.
                # COMPS is reachable so let's be clever and trust COMPS
                if str(r) == "404 NotFound - Failed to retrieve experiment for given id":
                    raise r
            except Exception as e:
                retExc = e
                time.sleep(wait)
        raise retExc if retExc else Exception()

    return wrapper
