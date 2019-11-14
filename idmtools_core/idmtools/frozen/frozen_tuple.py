class ImTuple(tuple):
    """
    Doc: Once a tuple is created, you cannot add items to it. Tuples are unchangeable.
    """
    _frozen = False

    # def __init__(self, t=None):
    #     if t:
    #         super().__init__(t)
    #     # self._frozen = False

    def __add__(self, *args, **kwargs):  # real signature unknown
        """ Return self+value. """
        if self._frozen:
            raise Exception('Frozen')
        else:
            super().__add__(*args, **kwargs)

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
