class FrozenBase:
    _frozen = False

    # def __init__(self):
    #     pass

    def frozen(self):
        from idmtools.frozen.frozen_utils import frozen_transform
        # import inspect
        # print(inspect.signature(MyClass.__init__))

        # Make sure don't do it twice
        if self._frozen:
            return

        for key, value in self.__dict__.items():
            # Approach: recursively transform object
            setattr(self, key, frozen_transform(value))

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
