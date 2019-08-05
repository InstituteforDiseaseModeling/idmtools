from dataclasses import fields
from idmtools.config import IdmConfigParser
from idmtools.core import PlatformFactory
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test.utils.decorators import docker_test, comps_test


class TestPlatformFactory(ITestWithPersistence):
    def setUp(self):
        super().setUp()
        IdmConfigParser.clear_instance()

    def tearDown(self):
        super().tearDown()

    @comps_test
    def test_get_block(self):
        entries = IdmConfigParser.get_block('COMPS2')
        self.assertEqual(entries['endpoint'], 'https://comps2.idmod.org')

    def test_block_not_exits(self):
        with self.assertRaises(Exception):
            platform = PlatformFactory.create_from_block('NOTEXISTS')  # noqa:F841

    def test_bad_type(self):
        with self.assertRaises(Exception):
            platform = PlatformFactory.create_from_block('BADTYPE')  # noqa:F841

    @docker_test
    def test_create_from_block(self):
        p1 = PlatformFactory.create_from_block('Local')
        self.assertEqual(p1.__class__.__name__, 'LocalPlatform')

        p2 = PlatformFactory.create_from_block('COMPS2')
        self.assertEqual(p2.__class__.__name__, 'COMPSPlatform')

        p3 = PlatformFactory.create_from_block('Test')
        self.assertEqual(p3.__class__.__name__, 'TestPlatform')

    @docker_test
    def test_platform_factory(self):
        platform1 = PlatformFactory.create('COMPS')
        self.assertEqual(platform1.__class__.__name__, 'COMPSPlatform')

        platform2 = PlatformFactory.create('Local')
        self.assertEqual(platform2.__class__.__name__, 'LocalPlatform')

        platform3 = PlatformFactory.create('Test')
        self.assertEqual(platform3.__class__.__name__, 'TestPlatform')

    @comps_test
    def test_COMPSPlatform(self):
        platform = PlatformFactory.create_from_block('COMPS2')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform)}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys}

        platform2 = PlatformFactory.create('COMPS', **kwargs)
        self.assertEqual(platform, platform2)

    @docker_test
    def test_LocalPlatform(self):
        platform = PlatformFactory.create_from_block('Local')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform)}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys}

        platform2 = PlatformFactory.create('Local', **kwargs)
        self.assertEqual(platform, platform2)

    def test_TestPlatform(self):
        platform = PlatformFactory.create_from_block('Test')
        members = platform.__dict__

        field_name = {f.name for f in fields(platform)}
        keys = field_name.intersection(members.keys())
        kwargs = {key: members[key] for key in keys}

        platform2 = PlatformFactory.create('Test', **kwargs)
        self.assertEqual(platform, platform2)
