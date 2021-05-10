"""
Frozen_tuple provided utilities for a read-only tuple.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools.frozen.ifrozen import IFrozen


class ImTuple(tuple, IFrozen):
    """
    Doc: Once a tuple is created, you cannot add items to it. Tuples are unchangeable.
    """

    def __add__(self, *args, **kwargs):  # real signature unknown
        """Return self+value."""
        if self._frozen:
            raise Exception('Frozen')
        super().__add__(*args, **kwargs)
