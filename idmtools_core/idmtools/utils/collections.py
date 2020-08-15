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


class ExperimentParentIterator(typing.Iterator['Simulation']):  # noqa F821
    def __init__(self, lst, parent: 'IEntity'):  # noqa F821
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
        from idmtools.entities.templated_simulation import TemplatedSimulations
        if isinstance(self.items, typing.Sized):
            return len(self.items)
        elif isinstance(self.items, TemplatedSimulations):
            return sum([len(b) for b in self.items.builders])
        raise ValueError("Cannot get the length of a generator object")

    def append(self, item: 'Simulation'): # noqa F821
        """
        Adds a simulation to an object

        Args:
            item: Item to add

        Returns:
            None
        """
        from idmtools.entities.templated_simulation import TemplatedSimulations
        from idmtools.entities.simulation import Simulation
        if not isinstance(item, Simulation):
            raise ValueError("You can only append simulations")
        if isinstance(self.items, (list, set)):
            self.items.append(item)
            return
        elif isinstance(self.items, TemplatedSimulations):
            self.items.add_simulation(item)
            return
        raise ValueError("Items doesn't support appending")

    def extend(self, item: Union[List['Simulation'], 'TemplatedSimulations']):  # noqa F821
        """
        Extends object(adds
        Args:
            item:

        Returns:
            None
        """
        from idmtools.entities.templated_simulation import TemplatedSimulations
        if isinstance(self.items, (list, set)):
            # if it is a template, try to preserve so we can user generators
            if isinstance(item, TemplatedSimulations):
                self.items.extend(list(item))
            else:
                self.items.extend(item)
            return
        if isinstance(self.items, TemplatedSimulations):
            if isinstance(item, TemplatedSimulations):
                self.items.add_simulations(list(item))
            else:
                self.items.add_simulations(item)
            return
        raise ValueError("Items doesn't support extending")


class ResetGenerator(typing.Iterator):
    """Iterator that counts upward forever."""

    def __init__(self, generator_init):
        self.generator_init = generator_init
        self.generator = generator_init()
        self.generator, self.__next_gen = tee(self.generator)

    def __iter__(self):
        return self

    def next_gen(self):
        return self.__next_gen

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
