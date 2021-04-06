"""
Frozen_dict provided utilities for a read-only dict.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from collections import UserDict
from idmtools.frozen.ifrozen import IFrozen


class ImDict(UserDict, IFrozen):
    """
    ImDict is a frozen wrapper for dict.
    """

    def __setitem__(self, *args, **kwargs):  # real signature unknown
        """Set self[key] to value."""
        if self._frozen:
            raise Exception('Frozen')
        super().__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):  # real signature unknown
        """Delete self[key]."""
        if self._frozen:
            raise Exception('Frozen')
        super().__delitem__(*args, **kwargs)

    def setdefault(self, *args, **kwargs):  # real signature unknown
        """
        Insert key with a value of default if key is not in the dictionary.

        Return the value for key if key is in the dictionary, else default.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().setdefault(*args, **kwargs)

    def update(self, E=None, **F):  # known special case of dict.update
        """
        Update the dict.

        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.

        If E is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]
        """
        if self._frozen:
            raise Exception('Frozen')
        super().update(E, **F)

    def pop(self, k, d=None):  # real signature unknown; restored from __doc__
        """
        Pop from dictionary.

        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.

        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        if self._frozen:
            raise Exception('Frozen')
        super().pop(k, d)

    def popitem(self):  # real signature unknown; restored from __doc__
        """
        Pop item from dictionary.

        Popitem - D.popitem() -> (k, v), remove and return some (key, value) pair as a 2-tuple; but raise KeyError if D is empty.
        """
        if self._frozen:
            raise Exception('Frozen')
        super().popitem()
