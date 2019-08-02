from functools import wraps
from typing import Callable, Union


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
