import json
import os
import unittest
from functools import partial

from idmtools.assets import Asset, AssetCollection
from idmtools.core import DuplicatedAssetError, FilterMode
from idmtools.utils.filters.asset_filters import asset_in_directory, file_name_is
from tests import INPUT_PATH


class TestAssets(unittest.TestCase):

    def setUp(self) -> None:
        self.base_path = os.path.abspath(os.path.join(INPUT_PATH, "assets", "collections"))

    def test_hashing(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        b = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        self.assertEqual(a, b)

        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        self.assertEqual(a, b)

    def test_assets_collection_from_dir(self):
        assets_to_find = [
            Asset(absolute_path=os.path.join(self.base_path, "d.txt")),
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "b.txt")),
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        ac = AssetCollection.from_directory(assets_directory=self.base_path)

        self.assertSetEqual(set(ac.assets), set(assets_to_find))

    def test_assets_collection_duplicate(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        ac = AssetCollection()
        ac.add_asset(a)
        with self.assertRaises(DuplicatedAssetError):
            ac.add_asset(a)

    def test_assets_collection_filtering_basic(self):
        # Test basic file name filtering
        ac = AssetCollection()
        assets_to_find = [
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        filter_name = partial(file_name_is, filenames=["a.txt", "c.txt"])
        ac.add_directory(assets_directory=self.base_path, filters=[filter_name])
        self.assertSetEqual(set(ac.assets), set(assets_to_find))

        # Test basic directory filtering
        ac = AssetCollection()
        assets_to_find = [
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        filter_dir = partial(asset_in_directory, directories=["2"])
        ac.add_directory(assets_directory=self.base_path, filters=[filter_dir])
        self.assertSetEqual(set(ac.assets), set(assets_to_find))

    def test_assets_collection_filtering_mode(self):
        # Test OR
        ac = AssetCollection()
        assets_to_find = [
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        filter_name = partial(file_name_is, filenames=["a.txt", "c.txt"])
        filter_dir = partial(asset_in_directory, directories=["2"])
        ac.add_directory(assets_directory=self.base_path, filters=[filter_name, filter_dir])
        self.assertSetEqual(set(ac.assets), set(assets_to_find))

        ac = AssetCollection()
        assets_to_find = [
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        ac.add_directory(assets_directory=self.base_path, filters=[filter_name, filter_dir],
                         filters_mode=FilterMode.AND)
        self.assertSetEqual(set(ac.assets), set(assets_to_find))

    def test_empty_collection(self):
        ac = AssetCollection()
        self.assertEqual(ac.count, 0)
        self.assertIsNone(ac.uid)

        ac.add_asset(Asset(filename="test", content="blah"))
        ac.uid = 3
        self.assertEqual(ac.uid, 3)


if __name__ == '__main__':
    unittest.main()
