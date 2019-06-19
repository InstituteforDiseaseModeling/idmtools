import os
import logging
import diskcache
from abc import ABCMeta

logger = logging.getLogger(__name__)


class IPersistenceService(metaclass=ABCMeta):
    cache_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    cache_name = None

    @classmethod
    def _open_cache(cls):
        cache_directory = os.path.join(cls.cache_directory, 'disk_cache', cls.cache_name)
        os.makedirs(cache_directory, exist_ok=True)
        return diskcache.Cache(os.path.join(cls.cache_directory, 'disk_cache', cls.cache_name), timeout=-1)

    @classmethod
    def retrieve(cls, uid):
        cache = cls._open_cache()
        obj = cache.get(uid)
        cache.close()
        return obj

    @classmethod
    def save(cls, obj):
        cache = cls._open_cache()
        if logger.isEnabledFor(logging.DEBUG):
            logging.debug('Saving {} to {}', obj.uid, cls.cache_name)
        cache.set(obj.uid, obj)
        cache.close()
        return obj.uid

