from unittest import TestCase


#@docker_test
from idmtools_platform_local.local_docker_manager import LocalDockerManager


class TestDockerManager(TestCase):

    def test_docker_create_database(self):
        dm = LocalDockerManager()

    def test_port_taken(self):
        self.fail()