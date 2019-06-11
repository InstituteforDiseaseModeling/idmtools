from idmtools.utils.hashing import hash_obj


class IPicklableObject:
    pickle_ignore_fields = []

    # region Events methods
    def post_setstate(self):
        """
        Function called after restoring the state if additional initialization is required
        """
        pass

    # endregion

    # region State management and Hashing
    def __getstate__(self):
        """
        Ignore the fields in pickle_ignore_fields during pickling.
        """
        state = self.__dict__.copy()
        # Don't pickle baz
        for f in self.pickle_ignore_fields:
            del state[f]

        return state

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle
        """
        self.__dict__.update(state)
        for f in self.pickle_ignore_fields:
            setattr(self, f, None)
        self.post_setstate()

    def __eq__(self, other):
        return hash_obj(self) == hash_obj(other)
    # endregion
