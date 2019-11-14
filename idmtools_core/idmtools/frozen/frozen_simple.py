class FrozenSimple:
    _frozen = False

    def __init__(self):
        pass

    def frozen(self):
        # Make sure don't do it twice
        if self._frozen:
            return

        self._frozen = True

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
