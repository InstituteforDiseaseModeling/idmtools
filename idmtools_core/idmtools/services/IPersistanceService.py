import os
import shelve
from abc import ABCMeta

current_directory = os.path.dirname(os.path.realpath(__file__))


class IPersistenceService(metaclass=ABCMeta):
    shelf_name = None

    @classmethod
    def _open_shelf(cls):
        return shelve.open(os.path.join(current_directory, cls.shelf_name))

    @classmethod
    def retrieve(cls, uid):
        shelf = cls._open_shelf()
        return shelf[uid]

    @classmethod
    def save(cls, obj):
        shelf = cls._open_shelf()
        shelf[obj.uid] = obj
