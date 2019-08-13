import os
import shutil
import tempfile
from dataclasses import dataclass, field
from logging import getLogger

from diskcache import Cache, DEFAULT_SETTINGS

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
    _cache: 'Cache' = field(default=None, init=False, compare=False)
    _cache_directory: 'str' = field(default=None, init=False, compare=False)

    def __del__(self):
        if self._cache:
            self._cache.close()
        del self._cache

        if self._cache_directory and os.path.exists(self._cache_directory):
            try:
                shutil.rmtree(self._cache_directory)
            except IOError as e:
                logger.exception(e)

    @property
    def cache(self):
        if not self._cache:
            if not self._cache_directory:
                self._cache_directory = tempfile.mkdtemp()

            self._cache = Cache(self._cache_directory)
        return self._cache
