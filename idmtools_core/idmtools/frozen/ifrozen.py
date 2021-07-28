"""
IFrozen provided utilities for a read-only objects.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""


class IFrozen:
    """
    Allows for frozen(read-only) items.
    """
    _frozen = False

    def freeze(self):
        """
        Freeze the object.

        Returns:
            None
        """
        from idmtools.frozen.frozen_utils import frozen_transform

        # Make sure don't do it twice
        if self._frozen:
            return

        if hasattr(self, '__dict__'):
            for key, value in self.__dict__.items():
                setattr(self, key, frozen_transform(value))

        self._frozen = True

    def __setattr__(self, key, value):
        """
        Attempt to set attr. For frozen objects, this throws an error.

        Args:
            key:
            value:

        Returns:
            None

        Raises:
            ValueError - If item is frozen
        """
        if self._frozen:
            raise ValueError('Frozen')
        super().__setattr__(key, value)

    def __delattr__(self, item):
        """
        Delete attr replace. Frozen doesn't allow deletes.

        Args:
            item: Item to delete

        Returns:
            None

        Raises:
            ValueError - Frozen
        """
        if self._frozen:
            raise ValueError('Frozen')
        super().__delattr__(item)
