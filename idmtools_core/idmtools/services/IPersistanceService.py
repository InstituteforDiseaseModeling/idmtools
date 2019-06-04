import os
import shelve
from abc import ABCMeta


class IPersistenceService(metaclass=ABCMeta):
    shelve_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    shelf_name = None

    @classmethod
    def _open_shelf(cls):
        os.makedirs(cls.shelve_directory, exist_ok=True)
        return shelve.open(os.path.join(cls.shelve_directory, cls.shelf_name))

    @classmethod
    def retrieve(cls, uid):
        shelf = cls._open_shelf()
        obj = shelf[str(uid)]
        shelf.close()
        return obj

    @classmethod
    def save(cls, obj):
        shelf = cls._open_shelf()
        shelf[str(obj.uid)] = obj
        shelf.close()
        return obj.uid

