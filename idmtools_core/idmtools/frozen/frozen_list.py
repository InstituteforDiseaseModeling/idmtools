class ImList(list):
    _frozen = False

    # def __init__(self, l=None):
    #     if l:
    #         super().__init__(l)

    def append(self, *args, **kwargs):  # real signature unknown
        """ Append object to the end of the list. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().append(*args, **kwargs)

    def clear(self, *args, **kwargs):  # real signature unknown
        """ Remove all items from list. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().clear(*args, **kwargs)

    def extend(self, *args, **kwargs):  # real signature unknown
        """ Extend list by appending elements from the iterable. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().extend(*args, **kwargs)

    def insert(self, *args, **kwargs):  # real signature unknown
        """ Insert object before index. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().insert(*args, **kwargs)

    def pop(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().pop(*args, **kwargs)

    def remove(self, *args, **kwargs):  # real signature unknown
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().remove(*args, **kwargs)

    def __setitem__(self, key, item):
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().__setitem__(key, item)

    def __delitem__(self, key):
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().__delitem__(key)

    def __setattr__(self, key, value):  # real signature unknown
        """ Set self[key] to value. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().__setattr__(key, value)

    def __delattr__(self, item):
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().__delattr__(item)

    # def insert(self, index, item):
    #     if self._frozen:
    #         raise Exception('Frozen')
    #     else:
    #         super().insert(index, item)

    # [ZDU] Seems good but prevent user from access the item from index!
    # def __getitem__(self, *args, **kwargs):  # real signature unknown
    #     """ Return self[key]. """
    #     if self._frozen:
    #         raise Exception('Frozen')
    #     else:
    #         super().__getitem__(*args, **kwargs)

    # def __iter__(self): # real signature unknown
    #     """ Implement iter(self). """
    #     if self._frozen:
    #         raise Exception('Frozen')
    #     else:
    #         super().__iter__()

    # def __iter__(self, *args, **kwargs): # real signature unknown
    #     """ Implement iter(self). """
    #     if self._frozen:
    #         raise Exception('Frozen')
    #     else:
    #         super().__iter__(*args, **kwargs)

    # def __setslice__(self, *args, **kwargs):
    #     if self._frozen:
    #         raise Exception('Frozen')
    #     else:
    #         super().__setslice__(*args, **kwargs)
    #
    # def index(self, *args, **kwargs):  # real signature unknown
    #     """
    #     Return first index of value.
    #
    #     Raises ValueError if the value is not present.
    #     """
    #     if self._frozen:
    #         raise Exception('Frozen')
    #     else:
    #         super().pop(*args, **kwargs)
