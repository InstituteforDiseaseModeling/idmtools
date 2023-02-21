"""
IPersistenceService allows caching of items locally into a diskcache db that does not expire upon deletion.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import logging
import time
from pathlib import Path
from multiprocessing import cpu_count

import diskcache
from abc import ABCMeta

from idmtools.core import IDMTOOLS_USER_HOME

logger = logging.getLogger(__name__)


class IPersistenceService(metaclass=ABCMeta):
    """
    IPersistenceService provides a persistent cache. This is useful for network heavy operations.
    """
    cache_directory = None
    cache_name = None

    @classmethod
    def _open_cache(cls):
        """
        Open cache.

        Returns:
            None
        """
        import sqlite3
        from idmtools import IdmConfigParser
        cls.cache_directory = Path(
            IdmConfigParser.get_option(option="cache_directory", fallback=IDMTOOLS_USER_HOME.joinpath("cache")))

        # the more the cpus, the more likely we are to encounter a scaling issue. Let's try to scale with that up to
        # one second. above one second, we are introducing to much lag in processes
        default_timeout = min(max(0.25, cpu_count() * 0.025 * 2), 2)
        retries = 0
        while retries < 5:

            try:
                os.makedirs(cls.cache_directory, exist_ok=True)
                cache = diskcache.FanoutCache(os.path.join(str(cls.cache_directory), 'disk_cache', cls.cache_name),
                                              timeout=default_timeout, shards=cpu_count() * 2)
                return cache
            except (sqlite3.OperationalError, FileNotFoundError):
                retries += 1
                time.sleep(0.1)

    @classmethod
    def retrieve(cls, uid):
        """
        Retrieve item with id <uid> from cache.

        Args:
            uid: Id to fetch

        Returns:
            Item loaded from cache
        """
        with cls._open_cache() as cache:
            obj = cache.get(uid, retry=True)
            return obj

    @classmethod
    def save(cls, obj):
        """
        Save an item to our cache.

        Args:
            obj: Object to save.

        Returns:
            Object uid
        """
        with cls._open_cache() as cache:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug('Saving %s to %s', obj.uid, cls.cache_name)
            cache.set(obj.uid, obj, retry=True)

        return obj.uid

    @classmethod
    def delete(cls, uid):
        """
        Delete at item from our cache with id <uid>.

        Args:
            uid: Id to delete

        Returns:
            None
        """
        with cls._open_cache() as cache:
            cache.delete(uid, retry=True)

    @classmethod
    def clear(cls):
        """
        Clear our cache.

        Returns:
            None
        """
        with cls._open_cache() as cache:
            cache.clear(retry=True)

    @classmethod
    def list(cls):
        """
        List items in our cache.

        Returns:
            List of items in our cache
        """
        with cls._open_cache() as cache:
            _list = list(cache)
            return _list

    @classmethod
    def length(cls):
        """
        Total length of our persistence cache.

        Returns:
            Count of our cache
        """
        with cls._open_cache() as cache:
            _len = len(cache)
            return _len
