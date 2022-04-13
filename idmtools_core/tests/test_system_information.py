import allure
import subprocess
import unittest.mock
from unittest import TestCase
import pytest
from idmtools.core.system_information import get_system_information, SystemInformation
from idmtools.utils.info import get_packages_list
from idmtools_test.utils.decorators import linux_only, windows_only


@pytest.mark.smoke
@allure.story("CLI")
@allure.story("Info Command")
@allure.suite("idmtools_core")
class TestSystemInformation(TestCase):
    def test_minimal_info(self):
        """
        This is a simple object built from common functions. There is not much we can do in testing it
        other than building the object and testing the content is of expected type
        Returns:

        """
        instance = get_system_information()
        self.assertIsInstance(instance, SystemInformation)
        self.assertIsInstance(instance.user, str)
        self.assertIsInstance(get_packages_list(), list)

    def test_get_packages_works(self):
        packages = get_packages_list()
        # we should have more than one package in this environment
        self.assertGreater(len(packages), 1)
        # all the strings should be name == version
        for package in packages:
            self.assertIn(' ', package)
            parts = package.split(" ")
            self.assertIs(len(parts), 2)

    @unittest.mock.patch('idmtools.utils.info.get_packages_from_pip', side_effect=lambda: None)
    def test_get_packages_fallback(self, mock_stdout):
        packages = get_packages_list()
        self.assertGreater(len(packages), 1)

    @linux_only
    def test_user_string_matches_id(self):
        instance = get_system_information()
        id_output = subprocess.run(['id', '-u'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        group_output = subprocess.run(['id', '-g'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        self.assertEqual(instance.user_group_str, f"{id_output}:{group_output}")

    @windows_only
    def test_windows_is_user_1000(self):
        instance = get_system_information()
        self.assertEqual(instance.user_group_str, "1000:1000")
