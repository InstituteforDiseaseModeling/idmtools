import os
import logging
from multiprocessing import cpu_count

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
        # the more the cpus, the more likely we are to encounter a scaling issue. Let's try to scale with that up to
        # one second. above one second, we are introducing to much lag in processes
        default_timeout = min(max(0.1, cpu_count() * 0.0125), 1)
        return diskcache.Cache(os.path.join(cls.cache_directory, 'disk_cache', cls.cache_name), timeout=default_timeout)

    @classmethod
    def retrieve(cls, uid):
        with cls._open_cache() as cache:
            obj = cache.get(uid, retry=True)
            return obj

    @classmethod
    def save(cls, obj):
        with cls._open_cache() as cache:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug('Saving %s to %s', obj.uid, cls.cache_name)
            cache.set(obj.uid, obj, retry=True)

        return obj.uid

    @classmethod
    def delete(cls, uid):
        with cls._open_cache() as cache:
            cache.delete(uid, retry=True)

    @classmethod
    def clear(cls):
        with cls._open_cache() as cache:
            cache.clear(retry=True)

    @classmethod
    def list(cls):
        with cls._open_cache() as cache:
            _list = list(cache)
            return _list

    @classmethod
    def length(cls):
        with cls._open_cache() as cache:
            _len = len(cache)
            return _len
