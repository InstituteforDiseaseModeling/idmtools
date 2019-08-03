from unittest import TestCase

from idmtools.core.SystemInformation import get_system_information, SystemInformation, get_packages_list


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
            self.assertIn('==', package)
            parts = package.split("==")
            self.assertIs(len(parts), 2)
