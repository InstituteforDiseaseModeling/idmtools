# flake8: noqa E402
from idmtools_test.utils.confg_local_runner_test import config_local_test
local_path = config_local_test()
import io
import os
import socket
import unittest.mock

from idmtools_platform_local.docker.DockerOperations import DockerOperations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import docker_test

LDM_PATH = 'idmtools_platform_local.docker.DockerOperations.DockerOperations'


def check_port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


@docker_test
class TestDockerOperations(unittest.TestCase):

    def test_create_redis_starts(self):
        dm = DockerOperations()
        dm.get_redis()
        check_port_is_open(6379)
        dm.stop_services()

    def test_create_db_starts(self):
        """
        This test is mostly scaffolding but could be useful in future for troubleshooting
        We mock out all b
        """
        dm = DockerOperations()
        dm.get_postgres()
        check_port_is_open(5432)
        dm.stop_services()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_create_stack_starts(self, std_capture):
        dm = DockerOperations()
        dm.create_services()
        check_port_is_open(5432)
        check_port_is_open(5432)
        check_port_is_open(6379)

        with self.subTest("can_run_containers"):
            self.assertEqual(0, os.system(f'docker exec idmtools_workers docker run hello-world'))

        with self.subTest("can_copy_to_container"):
            worker_container = dm.get_workers()
            result = dm.copy_to_container(worker_container,
                                          os.path.join(COMMON_INPUT_PATH, "python", "hello_world.py"),
                                          "/tmp")
            self.assertTrue(result)
            self.assertEqual(0, os.system('docker exec idmtools_workers python /tmp/hello_world.py'))
            print(std_capture.getvalue())

        dm.stop_services()

    def test_port_taken(self):
        self.fail()



