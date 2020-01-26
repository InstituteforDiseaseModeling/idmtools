import typing
from itertools import tee
from typing import Tuple, List, Mapping, Union, Iterable, Generator

from more_itertools import take


def cut_iterable_to(obj: Iterable, to: int) -> Tuple[Union[List, Mapping], int]:
    """
       Cut an iterable to a certain length.

    Args:
        obj: The iterable to cut.
        to: The number of elements to return.

    Returns:
        A list or dictionary (depending on the type of object) of elements and
        the remaining elements in the original list or dictionary.
    """
    if isinstance(obj, dict):
        slice = {k: v for (k, v) in take(to, obj.items())}
    else:
        slice = take(to, obj)

    remaining = len(obj) - to
    remaining = 0 if remaining < 0 else remaining
    return slice, remaining


class ParentIterator(typing.Iterator):
    def __init__(self, lst, parent: 'IEntity'):
        self.items = lst
        self.__iter = iter(self.items) if not isinstance(self.items, (typing.Iterator, Generator)) else self.items
        self.parent = parent

    def __iter__(self):
        return self

    def __next__(self):
        i = next(self.__iter)
        i._parent = self.parent
        if hasattr(i, 'parent_id') and self.parent.uid is not None:
            i.parent_id = self.parent.uid
        return i

    def __getitem__(self, item):
        return self.items[item]

    def __getattr__(self, item):
        return getattr(self.items, item)

    def __len__(self):
        if isinstance(self.items, typing.Sized):
            return len(self.items)
        raise ValueError("Cannot get the length of a generator object")

    def append(self, item):
        if isinstance(self.items, (list, set)):
            self.items.append(item)
            return
        raise ValueError("Items doesn't support appending")


class ResetGenerator(typing.Iterator):
    """Iterator that counts upward forever."""

    def __init__(self, generator_init):
        self.generator_init = generator_init
        self.generator = generator_init()
        self.generator, self.__next_gen = tee(self.generator)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = next(self.generator)
        except StopIteration:
            self.generator, self.__next_gen = tee(self.__next_gen)
            raise StopIteration
        return result


def duplicate_list_of_generators(lst: List[Generator]):
    """
    Copy a list of iterators using tee
    Args:
        lst: List of generators

    Returns:
        Tuple with duplicate of iterators
    """
    new_sw = []
    old_sw = []
    for sw in lst:
        o, n = tee(sw)
        new_sw.append(n)
        old_sw.append(o)
    return old_sw, new_sw
