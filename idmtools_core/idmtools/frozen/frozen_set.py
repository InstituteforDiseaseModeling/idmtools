"""
Frozen_set provided utilities for a read-only set.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools.frozen.ifrozen import IFrozen


class ImSet(set, IFrozen):
    """
    ImSet is a frozen wrapper for Sets.
    """

    def add(self, *args, **kwargs):  # real signature unknown
        """
        Add an element to a set.

        This has no effect if the element is already present.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().add(*args, **kwargs)

    def clear(self, *args, **kwargs):  # real signature unknown
        """Remove all elements from this set."""
        if self._frozen:
            raise Exception('Frozen')
        super().clear(*args, **kwargs)

    def difference_update(self, *args, **kwargs):  # real signature unknown
        """Remove all elements of another set from this set."""
        if self._frozen:
            raise Exception('Frozen')
        super().difference_update(*args, **kwargs)

    def discard(self, *args, **kwargs):  # real signature unknown
        """
        Remove an element from a set if it is a member.

        If the element is not a member, do nothing.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().discard(*args, **kwargs)

    def intersection_update(self, *args, **kwargs):  # real signature unknown
        """Update a set with the intersection of itself and another."""
        if self._frozen:
            raise Exception('Frozen')
        super().intersection_update(*args, **kwargs)

    def pop(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return an arbitrary set element.

        Raises KeyError if the set is empty.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().pop(*args, **kwargs)

    def remove(self, *args, **kwargs):  # real signature unknown
        """
        Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().remove(*args, **kwargs)

    def union(self, *args, **kwargs):  # real signature unknown
        """
        Return the union of sets as a new set.

        (i.e. all elements that are in either set.)
        """
        if self._frozen:
            raise Exception('Frozen')
        super().union(*args, **kwargs)

    def update(self, *args, **kwargs):  # real signature unknown
        """Update a set with the union of itself and others."""
        if self._frozen:
            raise Exception('Frozen')
        super().update(*args, **kwargs)
