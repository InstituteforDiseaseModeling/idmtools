import os
import diskcache
from abc import ABCMeta


class IPersistenceService(metaclass=ABCMeta):
    cache_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    shelf_name = None

    @classmethod
    def _open_cache(cls):
        cache_directory=os.path.join(cls.cache_directory, 'disk_cache', cls.shelf_name)
        os.makedirs(cache_directory, exist_ok=True)
        return diskcache.Cache(os.path.join(cls.cache_directory, 'disk_cache', cls.shelf_name))

    @classmethod
    def retrieve(cls, uid):
        shelf = cls._open_cache()
        obj = shelf[str(uid)]
        shelf.close()
        return obj

    @classmethod
    def save(cls, obj):
        shelf = cls._open_cache()
        shelf[str(obj.uid)] = obj
        shelf.close()
        return obj.uid

