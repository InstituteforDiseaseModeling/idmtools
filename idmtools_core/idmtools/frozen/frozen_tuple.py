from idmtools.frozen.ifrozen import IFrozen


class ImTuple(tuple, IFrozen):
    """
    Doc: Once a tuple is created, you cannot add items to it. Tuples are unchangeable.
    """

    def __add__(self, *args, **kwargs):  # real signature unknown
        """ Return self+value. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().__add__(*args, **kwargs)
