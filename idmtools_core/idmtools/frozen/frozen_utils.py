from enum import Enum
from idmtools.frozen.frozen_dict import ImDict
from idmtools.frozen.frozen_list import ImList
from idmtools.frozen.frozen_set import ImSet
from idmtools.frozen.frozen_tuple import ImTuple
from idmtools.frozen.ifrozen import IFrozen


def get_frozen_item(obj):
    """
    Args:
        obj: object to be frozen

    Returns: the transformed object
    """

    class FrozenDict(ImDict):
        def __init__(self):
            super().__init__()
            for key, value in obj.items():
                self.data[key] = frozen_transform(value)

            # In case inherited from dict with customer fields
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    setattr(self, key, frozen_transform(value))

            self._frozen = True

    class FrozenList(ImList):
        def __init__(self):
            super().__init__()
            for value in obj:
                self.data.append(frozen_transform(value))

            # In case inherited from list with customer fields
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    setattr(self, key, frozen_transform(value))

            self._frozen = True

    class FrozenSet(ImSet):
        def __init__(self):
            super().__init__()
            for value in obj:
                self.add(frozen_transform(value))

            # In case inherited from set with customer fields
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    setattr(self, key, frozen_transform(value))

            self._frozen = True

    class FrozenTuple(ImTuple):
        def __new__(cls):
            o = ImTuple(obj)

            # In case inherited from tuple with customer fields
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    setattr(o, key, frozen_transform(value))

            return ImTuple(obj)

    class FrozenObject(IFrozen, obj.__class__):
        __metaclass__ = obj.__class__

        def __init__(self):
            for key, value in obj.__dict__.items():
                setattr(self, key, frozen_transform(value))

    if isinstance(obj, dict):
        return FrozenDict()

    if isinstance(obj, list):
        return FrozenList()

    if isinstance(obj, (set, frozenset)):
        return FrozenSet()

    if isinstance(obj, tuple):
        return FrozenTuple()

    return FrozenObject()


def is_builtins_single_object(obj):
    # Handle special cases
    if isinstance(obj, (Enum, range)):
        return True

    return type(obj).__module__ == 'builtins' and not is_builtins_collection(obj)


def is_builtins_collection(obj):
    from collections.abc import Collection
    return isinstance(obj, Collection) and not isinstance(obj, (str, bytes, bytearray))  # range, generator, etc,...


def is_user_defined_object(obj):
    return type(obj).__module__ != 'builtins'


def frozen_transform(obj=None):

    if isinstance(obj, IFrozen):
        obj.freeze()
        return obj

    if is_builtins_single_object(obj):
        return obj

    if isinstance(obj, dict):
        imdict = get_frozen_item(obj)
        return imdict

    if isinstance(obj, list):
        imlist = get_frozen_item(obj)
        return imlist

    if isinstance(obj, (set, frozenset)):
        imset = get_frozen_item(obj)
        return imset

    if isinstance(obj, tuple):
        imtuple = get_frozen_item(obj)
        return imtuple

    if not hasattr(obj, '__dict__'):  # say, iterator, zip, file, function, method, etc
        return obj

    obj_new = get_frozen_item(obj)
    obj_new._frozen = True

    return obj_new
