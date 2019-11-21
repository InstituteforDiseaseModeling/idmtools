class IFrozen:
    _frozen = False

    def freeze(self):
        from idmtools.frozen.frozen_utils import frozen_transform

        # Make sure don't do it twice
        if self._frozen:
            return

        if hasattr(self, '__dict__'):
            for key, value in self.__dict__.items():
                setattr(self, key, frozen_transform(value))

        self._frozen = True

    def __setattr__(self, key, value):
        """ Set self[key] to value. """
        if self._frozen:
            raise Exception('Frozen')
        super().__setattr__(key, value)

    def __delattr__(self, item):
        if self._frozen:
            raise Exception('Frozen')
        super().__delattr__(item)
