from pathlib import PurePath

import allure
import json
import os
import unittest
from functools import partial
import pytest
from tqdm import tqdm
from idmtools.assets import Asset, AssetCollection
from idmtools.assets.errors import DuplicatedAssetError
from idmtools.core import FilterMode
from idmtools.utils.filters.asset_filters import asset_in_directory, file_name_is
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import run_in_temp_dir


@pytest.mark.assets
@pytest.mark.smoke
@allure.story("Entities")
@allure.story("Assets")
@allure.suite("idmtools_core")
class TestAssets(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "assets", "collections"))

    def test_hashing(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        b = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        self.assertEqual(a, b)

        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        self.assertEqual(a, b)

    def test_creat_asset_absolute_path(self):
        a = Asset(absolute_path=os.path.join(self.base_path, "d.txt"))
        self.assertEqual(a.content, b"")
        self.assertEqual(a.filename, "d.txt")
        self.assertEqual(a.relative_path, "")

    def test_creat_asset_absolute_path_and_relative_path(self):
        a = Asset(relative_path='2', absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        self.assertEqual(a.content, b"")
        self.assertEqual(a.filename, "a.txt")
        self.assertEqual(a.relative_path, "2")

    def test_create_asset_absolute_path_and_content_fails(self):
        with self.assertRaises(ValueError) as e:
            a = Asset(absolute_path=os.path.join(self.base_path, "d.txt"), content="blah")
        self.assertEqual(e.exception.args[0], "Absolute Path and Content are mutually exclusive. Please provide only one of the options")

    def test_creat_asset_content_filename(self):
        a = Asset(filename='test', content="blah")
        self.assertEqual(a.content, "blah")
        self.assertEqual(a.filename, "test")
        self.assertEqual(a.relative_path, "")

    def test_creat_asset_only_content(self):
        with self.assertRaises(ValueError) as ex:
            a = Asset(content="blah")

    def test_creat_asset_no_parameters(self):
        with self.assertRaises(ValueError) as context:
            a = Asset()  # noqa F841
        self.assertTrue('Impossible to create the asset without either absolute path, filename and content, or filename and checksum!' in str(
            context.exception.args[0]))

    def test_assets_is_iterable(self):
        ac = AssetCollection.from_directory(assets_directory=self.base_path)
        items = []
        for item in ac:
            items.append(item)

        for item in items:
            self.assertIn(item, ac.assets)

    def test_assets_collection_from_dir(self):
        assets_to_find = [
            Asset(absolute_path=os.path.join(self.base_path, "d.txt")),
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "b.txt")),
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        ac = AssetCollection.from_directory(assets_directory=self.base_path)
        AssetCollection.tags = {"idmtools": "idmtools-automation", "string_tag": "testACtag", "number_tag": 123,
                                "KeyOnly": None}
        print(AssetCollection.uid)

        self.assertSetEqual(set(ac.assets), set(assets_to_find), set(AssetCollection.tags))

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
        filter_dir = partial(asset_in_directory, directories=["2"], base_path=self.base_path)
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
        filter_dir = partial(asset_in_directory, directories=["2"], base_path=self.base_path)
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

    def test_bad_asset_path_empty_file(self):
        ac = AssetCollection()
        self.assertEqual(ac.count, 0)
        self.assertIsNone(ac.uid)

        with self.assertRaises(ValueError) as context:
            ac.add_asset(Asset())
        self.assertTrue('Impossible to create the asset without either absolute path, filename and content, or filename and checksum!' in str(
            context.exception.args[0]))

    def test_assets_collection_from_dir_flatten(self):
        assets_to_find = [
            Asset(absolute_path=os.path.join(self.base_path, "d.txt")),
            Asset(relative_path='', absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path='', absolute_path=os.path.join(self.base_path, "1", "b.txt")),
            Asset(relative_path='', absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        ac = AssetCollection.from_directory(assets_directory=self.base_path, flatten=True)

        self.assertSetEqual(set(ac.assets), set(assets_to_find))

    def test_assets_collection_from_dir_flatten_forced_relative_path(self):
        assets_to_find = [
            Asset(relative_path='assets_dir', absolute_path=os.path.join(self.base_path, "d.txt")),
            Asset(relative_path='assets_dir', absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path='assets_dir', absolute_path=os.path.join(self.base_path, "1", "b.txt")),
            Asset(relative_path='assets_dir', absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]
        ac = AssetCollection.from_directory(assets_directory=self.base_path, flatten=True, relative_path="assets_dir")

        self.assertSetEqual(set(ac.assets), set(assets_to_find))

    def test_asset_collection(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))

        ac1 = AssetCollection([a])
        ac2 = AssetCollection()

        self.assertEqual(len(ac1.assets), 1)
        self.assertEqual(len(ac2.assets), 0)

        self.assertNotEqual(ac1, ac2)
        self.assertNotEqual(ac1.assets, ac2.assets)

    def test_duplicates_filtered_from_list(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        b = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))

        ac1 = AssetCollection([a, b])
        self.assertEqual(1, len(ac1.assets))

    def test_duplicates_filtered_from_list_with_relative_paths(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        b = Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "1", "a.txt"))

        ac1 = AssetCollection([a, b])
        self.assertEqual(2, len(ac1.assets))

    def test_duplicates_filtered_from_list_with_checksum(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        b = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')

        ac1 = AssetCollection([a, b])
        self.assertEqual(1, len(ac1.assets))

    def test_fail_checksum_add_with_local_file(self):
        a = Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt"))
        b = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')

        ac1 = AssetCollection([a])
        with self.assertRaises(DuplicatedAssetError):
            ac1.add_asset(b)

    def test_fail_checksum_add_with_checksums_only(self):
        a = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        b = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')

        ac1 = AssetCollection([a])
        with self.assertRaises(DuplicatedAssetError):
            ac1.add_asset(b)

    def test_checksum_add_ok_with_different_filenames(self):
        a = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        b = Asset(relative_path="1", filename="b.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')

        ac1 = AssetCollection([a])
        ac1.add_asset(b)
        self.assertEqual(2, len(ac1.assets))

    def test_file_not_exists(self):
        with self.assertRaises(FileNotFoundError) as ex:
            a = Asset(filename="abc")

    def test_checksum_str(self):
        a = Asset(filename="blah", content="A test tring")
        result = a.calculate_checksum()
        self.assertEqual(result, '644e28386b702cbd6d2938d1af5eaa3c')

    def test_change_contents(self):
        a = Asset(filename="blah", content="A test tring")
        checksum_a = a.calculate_checksum()
        a.content = "Lala"
        checksum_b = a.calculate_checksum()
        self.assertNotEqual(checksum_a, checksum_b)

    def test_checksum_dict(self):
        a = Asset(filename="blah", content={'a': 'b'})
        checksum_a = a.calculate_checksum()
        self.assertEqual(checksum_a, '11cc97cf2d9c08aa403d131333b3d298')

    def test_checksum_empty_dict(self):
        a = Asset(filename="blah", content={})
        checksum_a = a.calculate_checksum()
        self.assertEqual(checksum_a, '99914b932bd37a50b983c5e7c90ae93b')

    def test_dict_and_byte_contents(self):
        a = Asset(filename="blah", content={"a": "v1", "b": 123})
        checksom_a = a.calculate_checksum()
        b = Asset(filename="blah", content=b"{'a': 'v1', 'b': 123}")
        checksom_b = b.calculate_checksum()
        self.assertEqual(checksom_a, checksom_b)

    def test_compare_assets(self):
        # compare different paths, same checksums
        a = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        b = Asset(relative_path="1", filename="b.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')

        self.assertNotEqual(a, b)

        # compare same paths, different checksums
        a = Asset(relative_path="1", filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        b = Asset(relative_path="1", filename="a.txt", checksum='e41d8cd98f00b204e9800998ecf8427e')
        self.assertEqual(a, b)

        # compare different paths, same checksums
        a = Asset(filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        b = Asset(filename="b.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        self.assertNotEqual(a, b)

        # compare same paths, different checksums
        a = Asset(filename="a.txt", checksum='d41d8cd98f00b204e9800998ecf8427e')
        b = Asset(filename="a.txt", checksum='e41d8cd98f00b204e9800998ecf8427e')
        self.assertEqual(a, b)
        # Deep compare should be false
        self.assertFalse(a.deep_equals(b))

        # same content with different path
        a = Asset(relative_path="1", filename="a.txt", content='hello')
        b = Asset(relative_path="1", filename="b.txt", content='hello')
        self.assertNotEqual(a, b)

        # different content with same path
        a = Asset(relative_path="1", filename="a.txt", content='hello')
        b = Asset(relative_path="1", filename="a.txt", content='world')
        self.assertEqual(a, b)
        self.assertFalse(a.deep_equals(b))

        # content vs file
        a = Asset(relative_path="1", filename="a.txt", content='hello')
        b = Asset(relative_path="1", filename="a.txt", absolute_path=os.path.join(COMMON_INPUT_PATH, 'files', 'hello.txt'))
        self.assertEqual(a, b)
        self.assertTrue(a.deep_equals(b))

    def test_asset_directory_fails(self):
        with self.assertRaises(ValueError) as ex:
            a = Asset(os.path.abspath(os.path.dirname(__file__)))
        self.assertEqual(ex.exception.args[0], "Asset cannot be a directory!")

    @pytest.mark.performance
    @pytest.mark.timeout(15)
    def test_large_asset_merge_speed(self):
        assets1 = AssetCollection()
        assets2 = AssetCollection()

        for i in tqdm(range(3000)):
            assets1.add_asset(Asset(content=f"{i}", filename=f"{i}"))

        for i in tqdm(range(3001, 6000)):
            assets2.add_asset(Asset(content=f"{i}", filename=f"{i}"))
        assets1.add_assets(assets2)

    @run_in_temp_dir
    def test_ignore_git(self):
        # make test data
        bd = PurePath("test_directory")
        gd = bd.joinpath(".git")
        os.makedirs(gd, exist_ok=True)

        with open(bd.joinpath("test1.txt"), "w") as fout:
            fout.write("1")

        with open(gd.joinpath("test2.txt"), "w") as fout:
            fout.write("2")

        ac = AssetCollection()
        ac.add_directory(bd)

        self.assertEqual(len(ac), 1)

        ac = AssetCollection()
        ac.add_directory(bd, no_ignore=True)
        self.assertEqual(len(ac), 2)

        
if __name__ == '__main__':
    unittest.main()
