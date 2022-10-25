"""
Frozen_list provided utilities for a read-only list.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from collections import UserList
from idmtools.frozen.ifrozen import IFrozen


class ImList(UserList, IFrozen):
    """FrozenList wrapper."""
    def append(self, *args, **kwargs):  # real signature unknown
        """Append object to the end of the list."""
        if self._frozen:
            raise Exception('Frozen')
        super().append(*args, **kwargs)

    def clear(self, *args, **kwargs):  # real signature unknown
        """Remove all items from list."""
        if self._frozen:
            raise Exception('Frozen')
        super().clear(*args, **kwargs)

    def extend(self, *args, **kwargs):  # real signature unknown
        """Extend list by appending elements from the iterable."""
        if self._frozen:
            raise Exception('Frozen')
        super().extend(*args, **kwargs)

    def insert(self, *args, **kwargs):  # real signature unknown
        """Insert object before index."""
        if self._frozen:
            raise Exception('Frozen')
        super().insert(*args, **kwargs)

    def pop(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().pop(*args, **kwargs)

    def remove(self, *args, **kwargs):  # real signature unknown
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().remove(*args, **kwargs)

    def __setitem__(self, key, item):
        """Set item. Raises exception if frozen."""
        if self._frozen:
            raise Exception('Frozen')
        super().__setitem__(key, item)

    def __delitem__(self, key):
        """Delete item. Raises exception if frozen."""
        if self._frozen:
            raise Exception('Frozen')
        super().__delitem__(key)
