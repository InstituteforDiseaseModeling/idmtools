import allure
import os
import pytest
from dataclasses import fields
from idmtools.config import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.smoke
@pytest.mark.serial
@allure.story("Core")
@allure.suite("idmtools_core")
class TestPlatformFactory(ITestWithPersistence):
    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()
        # Because of other tests, we cannot clear this properly. The best we can do is set it here so that tests that modify it don't effect this test
        os.environ['IDMTOOLS_ERROR_NO_CONFIG'] = "1"

    def tearDown(self):
        super().tearDown()

    @allure.story("Configuration")
    def test_get_section(self):
        entries = IdmConfigParser.get_section('COMPS2')
        self.assertEqual(entries['endpoint'], 'https://comps2.idmod.org')

    def test_block_not_exits(self):
        with self.assertRaises(ValueError) as context:
            Platform('NOTEXISTS')  # noqa:F841
        self.assertEqual("Block 'NOTEXISTS' doesn't exist!", str(context.exception.args[0]))

    @allure.story("Plugins")
    def test_bad_type(self):
        with self.assertRaises(ValueError) as context:
            Platform('BADTYPE')  # noqa:F841
        self.assertTrue("Bad is an unknown Platform Type. Supported platforms are" in str(context.exception.args[0]))

    @allure.story("Plugins")
    def test_no_type(self):
        with self.assertRaises(ValueError) as context:
            Platform('NOTYPE')
        self.assertIn('When creating a Platform you must specify the type in the block.', context.exception.args[0])

    @allure.story("Configuration")
    def test_block_is_none(self):
        with self.assertRaises(ValueError) as context:
            Platform(None)
        self.assertIn('Must have a valid Block name to create a Platform!', context.exception.args[0])

    @allure.story("Configuration")
    def test_no_block(self):
        try:
            Platform()
        except Exception as ex:
            self.assertIn("__new__() missing 1 required positional argument: 'block'", ex.args[0])

    @allure.story("Configuration")
    def test_create_from_block(self):
        p = Platform('Test')
        self.assertEqual(p.__class__.__name__, 'TestPlatform')
        p.cleanup()

    def test_TestPlatform(self):
        platform = Platform('Test')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform) if f.init}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys if not key.startswith('_')}

        platform2 = Platform('Test', **kwargs)
        # same reason as above test
        platform.uid = None
        platform2.uid = None
        self.assertEqual(platform, platform2)
        platform2.cleanup()
