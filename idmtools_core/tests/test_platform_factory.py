from dataclasses import fields
from idmtools.config import IdmConfigParser
from idmtools.core import platform_factory
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence


class TestPlatformFactory(ITestWithPersistence):
    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()

    def tearDown(self):
        super().tearDown()

    def test_get_block(self):
        entries = IdmConfigParser.get_block('COMPS2')
        self.assertEqual(entries['endpoint'], 'https://comps2.idmod.org')

    def test_block_not_exits(self):
        with self.assertRaises(Exception):
            platform = platform_factory.create_from_block('NOTEXISTS')  # noqa:F841

    def test_bad_type(self):
        with self.assertRaises(Exception):
            platform = platform_factory.create_from_block('BADTYPE')  # noqa:F841

    def test_create_from_block(self):
        p1 = platform_factory.create_from_block('LOCAL')
        self.assertEqual(p1.__class__.__name__, 'LocalPlatform')

        p2 = platform_factory.create_from_block('COMPS2')
        self.assertEqual(p2.__class__.__name__, 'COMPSPlatform')

        p3 = platform_factory.create_from_block('TEST')
        self.assertEqual(p3.__class__.__name__, 'TestPlatform')

    def test_platform_factory(self):
        platform1 = platform_factory.create('idmtools.platforms.COMPSPlatform')
        self.assertEqual(platform1.__class__.__name__, 'COMPSPlatform')

        platform2 = platform_factory.create('idmtools.platforms.LocalPlatform')
        self.assertEqual(platform2.__class__.__name__, 'LocalPlatform')

        platform3 = platform_factory.create('tests.utils.TestPlatform')
        self.assertEqual(platform3.__class__.__name__, 'TestPlatform')

    def test_COMPSPlatform(self):
        platform = platform_factory.create_from_block('COMPS2')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform)}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys}

        platform2 = platform_factory.create(platform.__class__.__module__, **kwargs)
        self.assertEqual(platform, platform2)

    def test_LocalPlatform(self):
        platform = platform_factory.create_from_block('LOCAL')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform)}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys}

        platform2 = platform_factory.create(platform.__class__.__module__, **kwargs)
        self.assertEqual(platform, platform2)

    def test_TestPlatform(self):
        platform = platform_factory.create_from_block('TEST')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform)}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys}

        platform2 = platform_factory.create(platform.__class__.__module__, **kwargs)
        self.assertEqual(platform, platform2)
