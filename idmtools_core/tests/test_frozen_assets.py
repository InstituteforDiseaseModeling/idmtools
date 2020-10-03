import allure
import os
import unittest
import pytest
from idmtools.frozen.frozen_utils import frozen_transform
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")
DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")


@pytest.mark.smoke
@allure.story("Assets")
@allure.suite("idmtools_core")
class TestFrozenAssets(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        self.base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "assets", "collections"))

    def test_frozen_transform_assets(self):
        from idmtools.assets import Asset
        from idmtools.assets import AssetCollection

        assets_to_find = [
            Asset(absolute_path=os.path.join(self.base_path, "d.txt")),
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "a.txt")),
            Asset(relative_path="1", absolute_path=os.path.join(self.base_path, "1", "b.txt")),
            Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ]

        ac = AssetCollection.from_directory(assets_directory=self.base_path)
        ac.tags = {"idmtools": "idmtools-automation", "string_tag": "testACtag", "number_tag": 123,
                   "KeyOnly": None}
        print(ac.uid)
        self.assertSetEqual(set(ac.assets), set(assets_to_find), set(ac.tags))

        # Test: Asset can be modified before frozen
        a = ac.assets[0]
        a.filename = 'new_value.txt'
        a.absolute_path = 'new_value.txt'
        self.assertEqual(a.filename, 'new_value.txt')
        self.assertEqual(a.absolute_path, 'new_value.txt')
        self.assertTrue(isinstance(a, Asset))

        # Frozen asset
        ac.assets[0] = frozen_transform(a)

        # Test: other asset can be modified
        a2 = ac.assets[1]
        a2.filename = 'modified.txt'
        a2.absolute_path = 'modified.txt'
        a2._relative_path = os.getcwd()
        a2._content = 'modified'
        self.assertEqual(a2.filename, 'modified.txt')
        self.assertEqual(a2.absolute_path, 'modified.txt')
        self.assertEqual(a2._relative_path, os.getcwd())
        self.assertEqual(a2._content, 'modified')

        # Get the frozen asset
        a_frozen = ac.assets[0]

        # Test: user can still access the frozen asset
        print(a_frozen.filename)
        print(a_frozen.absolute_path)
        print(a_frozen._relative_path)
        print(a_frozen._content)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            a_frozen.filename = 'a_modified_again.txt'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            a_frozen.absolute_path = 'new.txt'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            a_frozen._relative_path = os.getcwd()
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            a_frozen._content = 'Hello World'
        self.assertIn('Frozen', context.exception.args[0])

    def test_frozen_assets_inherit(self):
        from idmtools_test.utils.test_asset import Asset
        from idmtools_test.utils.test_asset_collection import AssetCollection

        ac = AssetCollection.from_directory(assets_directory=self.base_path)
        ac.tags = {"idmtools": "idmtools-automation", "string_tag": "testACtag", "number_tag": 123,
                   "KeyOnly": None}
        print(ac.uid)

        # Test: Asset can be modified before frozen
        a = ac.assets[0]
        a.filename = 'new_value.txt'
        a.absolute_path = 'new_value.txt'
        self.assertEqual(a.filename, 'new_value.txt')
        self.assertEqual(a.absolute_path, 'new_value.txt')
        self.assertTrue(isinstance(a, Asset))

        # Now freeze the asset
        a.freeze()

        # Test: other asset can be modified
        a2 = ac.assets[1]
        a2.filename = 'modified.txt'
        a2.absolute_path = 'modified.txt'
        a2._relative_path = os.getcwd()
        a2._content = 'modified'
        self.assertEqual(a2.filename, 'modified.txt')
        self.assertEqual(a2.absolute_path, 'modified.txt')
        self.assertEqual(a2._relative_path, os.getcwd())
        self.assertEqual(a2._content, 'modified')

        # get the frozen asset
        a = ac.assets[0]
        self.assertTrue(isinstance(a, Asset))

        # Test: user can still access the frozen asset
        print(a.filename)
        print(a.absolute_path)
        print(a._relative_path)
        print(a._content)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            a.filename = 'a_modified_again.txt'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            a.absolute_path = 'new.txt'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            a._relative_path = os.getcwd()
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            a._content = 'Hello World'
        self.assertIn('Frozen', context.exception.args[0])

    def test_frozen_asset_collection_both_inherit(self):
        from idmtools_test.utils.test_asset_collection import AssetCollection
        from idmtools_test.utils.test_asset import Asset

        ac = AssetCollection()
        a = Asset(absolute_path=os.path.join(self.base_path, "d.txt"))
        a2 = Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ac.add_asset(a)
        ac.add_asset(a2)
        ac.tags = {"idmtools": "idmtools-automation", "number_tag": 123}
        print(ac.uid)
        self.assertEqual(len(ac.assets), 2)

        ac.freeze()
        ac_frozen = ac
        self.assertEqual(len(ac_frozen.assets), 2)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            ac_frozen.tags = {}
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags["number_tag"] = 111
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags.update({"number_tag": 123})
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            del ac_frozen.assets[0]
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[0].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[1].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

    def test_frozen_asset_collection_only_inherit(self):
        from idmtools_test.utils.test_asset_collection import AssetCollection
        from idmtools.assets import Asset

        ac = AssetCollection()
        a = Asset(absolute_path=os.path.join(self.base_path, "d.txt"))
        a2 = Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ac.add_asset(a)
        ac.add_asset(a2)
        ac.tags = {"idmtools": "idmtools-automation", "number_tag": 123}
        print(ac.uid)
        self.assertEqual(len(ac.assets), 2)

        # Freeze asset collection
        ac.freeze()
        ac_frozen = ac
        self.assertEqual(len(ac_frozen.assets), 2)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            ac_frozen.tags = {}
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags["number_tag"] = 111
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags.update({"number_tag": 123})
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            del ac_frozen.assets[0]
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[0].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[1].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

    def test_frozen_asset_collection(self):
        from idmtools.assets import AssetCollection
        from idmtools_test.utils.test_asset import Asset

        ac = AssetCollection()
        a = Asset(absolute_path=os.path.join(self.base_path, "d.txt"))
        a2 = Asset(relative_path="2", absolute_path=os.path.join(self.base_path, "2", "c.txt"))
        ac.add_asset(a)
        ac.add_asset(a2)
        ac.tags = {"idmtools": "idmtools-automation", "number_tag": 123}
        print(ac.uid)
        self.assertEqual(len(ac.assets), 2)

        # Freeze asset collection
        ac_frozen = frozen_transform(ac)
        self.assertEqual(len(ac_frozen.assets), 2)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            ac_frozen.tags = {}
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags["number_tag"] = 111
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags.update({"number_tag": 123})
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            del ac_frozen.assets[0]
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[0].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[1].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

    def test_frozen_asset_collection_inherit(self):
        from idmtools_test.utils.test_asset_collection import AssetCollection

        ac = AssetCollection.from_directory(assets_directory=self.base_path)
        ac.tags = {"idmtools": "idmtools-automation", "number_tag": 123}
        print(ac.uid)
        self.assertEqual(len(ac.assets), 4)

        # Freeze asset collection
        ac.freeze()
        ac_frozen = ac
        self.assertEqual(len(ac_frozen.assets), 4)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            ac_frozen.tags = {}
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags["number_tag"] = 111
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags.update({"number_tag": 123})
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            del ac_frozen.assets[0]
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[0].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[1].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

    def test_frozen_transform_asset_collection(self):
        from idmtools.assets import AssetCollection

        ac = AssetCollection.from_directory(assets_directory=self.base_path)
        ac.tags = {"idmtools": "idmtools-automation", "number_tag": 123}
        print(ac.uid)
        self.assertEqual(len(ac.assets), 4)

        # Freeze asset collection
        ac_frozen = frozen_transform(ac)
        self.assertEqual(len(ac_frozen.assets), 4)

        # Test: user can still access the frozen asset
        self.assertEqual(ac_frozen.tags, ac.tags)

        # Test: the frozen asset (the first one) can't be modified
        with self.assertRaises(Exception) as context:
            ac_frozen.tags = {}
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags["number_tag"] = 111
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.tags.update({"number_tag": 123})
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            del ac_frozen.assets[0]
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[0].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])

        with self.assertRaises(Exception) as context:
            ac_frozen.assets[1].filename = 'modified'
        self.assertIn('Frozen', context.exception.args[0])


if __name__ == '__main__':
    unittest.main()
