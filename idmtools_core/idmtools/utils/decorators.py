import inspect


def pickle_ignore_fields(ignore_fields=None):
    """
    Allows classes to define a `pickle_ignore_fields` that will then be used on the IPicklableObject
    Args:
        ignore_fields:

    Returns:

    """

    def wrapper(cls):
        fields = set(ignore_fields) or set()
        for base in inspect.getmro(cls):
            if hasattr(base, "pickle_ignore_fields") and base.pickle_ignore_fields:
                # Only work with sets
                if not isinstance(base.pickle_ignore_fields, set):
                    base.pickle_ignore_fields = set(base.pickle_ignore_fields)

                fields |= base.pickle_ignore_fields
        setattr(cls, "pickle_ignore_fields", fields)
        return cls

    return wrapper


class abstractstatic(staticmethod):
    """
    Decorator for defining a method both as static and abstract
    """
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True
