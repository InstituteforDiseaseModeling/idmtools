import os
import tempfile
from random import random
from unittest import TestCase

import gc

from idmtools.core import CacheEnabled


class TestCacheEnabled(TestCase):
    def test_cache_works(self):
        c = CacheEnabled()
        val = random()
        c.cache.set('testing', val)
        self.assertEqual(c.cache.get('testing'), val)

    def test_using_temp_folder(self):
        c = CacheEnabled()
        # touch property
        c.cache
        self.assertIn(tempfile.gettempdir(), c._cache_directory)

    def test_is_cleaned_up(self):
        c = CacheEnabled()
        # touch property
        c.cache
        path = c._cache_directory
        del c
        gc.collect()
        self.assertTrue(not os.path.exists(path))
