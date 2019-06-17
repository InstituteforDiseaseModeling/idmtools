from idmtools.utils.hashing import hash_obj


class PicklableObject:
    """
    Represent a custom way to pickle an object.
    This will rely on the `pickle_ignore_fields` to not add those fields in the pickle and restore them to None when
    unpickling.

    Also this class has a `post_setstate` method that can be overwritten to restore fields that were ignored to
    something else than None.

    Warnings:
        The equality between 2 instances of this class relies on the `hash_obj` function that relies internally on
        pickle. Therefore instances are only compared on the fields that are not ignored.
        Given the following:
        ```
        class TestPO(PicklableObject):
            picle_ignore_fields = {"a"}
            def __init__(a,b):
                self.a = a
                self.b = b
        A = TestPO(a=1, b=3)
        B = TestPO(a=2, b=3)
        ```
        A will be considered equal to B (A == B is True)
    """
    pickle_ignore_fields = None

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
        # Don't pickle the fields that needs to be ignored (if any)
        if self.pickle_ignore_fields:
            for f in self.pickle_ignore_fields:
                del state[f]

        return state

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle
        """
        self.__dict__.update(state)
        # Restore the fields to None that we did not pickle
        if self.pickle_ignore_fields:
            for f in self.pickle_ignore_fields:
                setattr(self, f, None)
            self.post_setstate()

    def __eq__(self, other):
        return hash_obj(self.__getstate__()) == hash_obj(other.__getstate__())
    # endregion



