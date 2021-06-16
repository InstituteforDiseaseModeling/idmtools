"""
CacheEnabled definition. CacheEnabled enables diskcache wrapping on an item.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import shutil
import tempfile
import time
from contextlib import suppress
from dataclasses import dataclass, field
from multiprocessing import current_process, cpu_count
from logging import getLogger, DEBUG
from diskcache import Cache, DEFAULT_SETTINGS, FanoutCache
from typing import Union, Optional

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
    _cache: Union[Cache, FanoutCache] = field(default=None, init=False, compare=False,
                                              metadata={"pickle_ignore": True})
    _cache_directory: str = field(default=None, init=False, compare=False)

    def __del__(self):
        """
        Deletes object. On Deletion, we destroy the cache.

        Returns:
            None
        """
        self.cleanup_cache()

    def initialize_cache(self, shards: Optional[int] = None, eviction_policy=None):
        """
        Initialize cache.

        Args:
            shards (Optional[int], optional): How many shards. It is best to set this when multi-procressing Defaults to None.
            eviction_policy ([type], optional): See Diskcache docs. Defaults to None.
        """
        logger.debug(f"Initializing the cache with {shards or 0} shards and {eviction_policy or 'none'} policy.")
        if self._cache:
            logger.warning("CacheEnabled class is calling `initialize_cache()` with a cache already initialized: "
                           "deleting the cache and recreating a new one.")
            self.cleanup_cache()

        # Create the cache directory if does not exist
        if not self._cache_directory or not os.path.exists(self._cache_directory):
            self._cache_directory = tempfile.mkdtemp()
            logger.debug(f"Cache created in {self._cache_directory}")
        else:
            logger.debug(f"Cache retrieved in {self._cache_directory}")

        # Create different cache depending on the options
        if shards:
            # set default timeout to grow with cpu count. In high thread environments, user hit timeouts
            default_timeout = max(0.1, cpu_count() * 0.0125)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Setting cache timeout to {default_timeout}")
            self._cache = FanoutCache(self._cache_directory, shards=shards, timeout=default_timeout,
                                      eviction_policy=eviction_policy)
        else:
            self._cache = Cache(self._cache_directory)

    def cleanup_cache(self):
        """
        Cleanup our cache.

        Returns:
            None
        """
        # Only delete and close the cache if the owner thread ends
        # Avoid deleting and closing when a child thread ends
        with suppress(AttributeError):
            if current_process().name != 'MainProcess':
                return

        if self._cache is not None:
            self._cache.close()
            del self._cache

            if self._cache_directory and os.path.exists(self._cache_directory):
                retries = 0
                while retries < 3:
                    try:
                        shutil.rmtree(self._cache_directory)
                        time.sleep(0.15)
                        break
                    except IOError:
                        # we don't use logger here because it could be destroyed
                        print(f"Could not delete cache {self._cache_directory}")
                        retries += 1

    @property
    def cache(self) -> Union[Cache, FanoutCache]:
        """
        Allows fetches of cache and ensures it is initialized.

        Returns:
            Cache
        """
        if self._cache is None:
            self.initialize_cache()

        return self._cache
