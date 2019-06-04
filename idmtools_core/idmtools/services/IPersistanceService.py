import os
import shelve
from abc import ABCMeta


class IPersistenceService(metaclass=ABCMeta):
    shelve_directory = os.path.dirname(os.path.realpath(__file__))
    shelf_name = None

    @classmethod
    def _open_shelf(cls):
        return shelve.open(os.path.join(cls.shelve_directory, cls.shelf_name))

    @classmethod
    def retrieve(cls, uid):
        shelf = cls._open_shelf()
        obj = shelf[uid]
        shelf.close()
        return obj

    @classmethod
    def save(cls, obj):
        shelf = cls._open_shelf()
        shelf[obj.uid] = obj
        shelf.close()
        return obj.uid

