import importlib
import os
from functools import wraps
from typing import Callable, Union

from yaspin import yaspin


class abstractstatic(staticmethod):
    """
    Decorator for defining a method both as static and abstract
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
    Wraps a class in a Singleton Decorator.


    Examples:
        ```
        class Thing:
            y = 14
        Thing = SingletonDecorator(Thing)

        x = Thing()
        x.y = 99
        z = Thing()
        print(z.y)

        ```
        The above example should print out 99 since z ends up being the same object as X

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
    Additional class decorator that creates a singleton instance only when a method/attr is accessed. This is useful
    for expensive items like plugin factories loads that should only be executed when finally needed and not on
    declaration

    Examples:
        ```
        import time
        class ExpensiveFactory:
            def __init__():
                time.sleep(1000)
                self.items = ['a', 'b', 'c']

            def get_items():
                return self.items



        ExpensiveFactory = LoadOnCallSingletonDecorator(ExpensiveFactory)
        ExpensiveFactory.get_items()
        ```

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


def optional_yaspin_load(*yargs, **ykwargs):
    has_yaspin = importlib.util.find_spec("yaspin")
    spinner = None
    if has_yaspin and not os.get.env('NO_SPINNER', False):
        spinner = yaspin(*yargs, **ykwargs)

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if spinner:
                spinner.start()
            result = func(*args, **kwargs)
            if spinner:
                spinner.stop()
            return result
        return wrapper
    return decorate
