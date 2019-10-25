import os
import shutil
import tempfile
import typing
from dataclasses import dataclass, field
from logging import getLogger
from threading import get_ident
from diskcache import Cache, DEFAULT_SETTINGS, FanoutCache

if typing.TYPE_CHECKING:
    from typing import Union

MAX_CACHE_SIZE = int(2 ** 33)  # 8GB
DEFAULT_SETTINGS["size_limit"] = MAX_CACHE_SIZE
DEFAULT_SETTINGS["sqlite_mmap_size"] = 2 ** 28
DEFAULT_SETTINGS["sqlite_cache_size"] = 2 ** 15
logger = getLogger(__name__)


@dataclass(init=False, repr=False)
class CacheEnabled:
    """
    Allows a class to leverage Diskcache and expose a cache property.
    """
    _cache: 'Union[Cache, FanoutCache]' = field(default=None, init=False, compare=False)
    _cache_directory: 'str' = field(default=None, init=False, compare=False)
    _ident: 'int' = field(default=None, init=False, compare=False)

    def __del__(self):
        self.cleanup_cache()

    def initialize_cache(self, shards=None, eviction_policy=None):
        logger.debug(f"Initializing the cache with {shards or 0} shards and {eviction_policy or 'none'} policy.")
        if self._cache:
            logger.warning("CacheEnabled class is calling `initialize_cache()` with a cache already initialized: "
                           "deleting the cache and recreating a new one.")
            self.cleanup_cache()

        # Create the cache directory if does not exist
        if not self._cache_directory or not os.path.exists(self._cache_directory):
            self._cache_directory = tempfile.mkdtemp()

        # Retain which thread created the cache
        self._ident = get_ident()

        # Create different cache depending on the options
        if shards:
            self._cache = FanoutCache(self._cache_directory, shards=shards, timeout=0.050,
                                      eviction_policy=eviction_policy)
        else:
            self._cache = Cache(self._cache_directory)

        logger.debug(f"Cache created in {self._cache_directory}")

    def cleanup_cache(self):
        # Only delete and close the cache if the owner thread ends
        # Avoid deleting and closing when a child thread ends
        if self._ident != get_ident():
            return

        if self._cache is not None:
            logger.debug(f"Cleaning up the cache at {self._cache_directory}")
            self._cache.close()
            del self._cache

            if self._cache_directory and os.path.exists(self._cache_directory):
                try:
                    shutil.rmtree(self._cache_directory)
                except IOError as e:
                    logger.exception(e)

    @property
    def cache(self):
        if self._cache is None:
            self.initialize_cache()

        return self._cache
