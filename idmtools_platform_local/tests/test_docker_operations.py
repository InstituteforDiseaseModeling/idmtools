import http.server
import io
import os
import socket
import socketserver
import subprocess
import unittest.mock

import pytest

from idmtools_platform_local.docker.docker_operations import DockerOperations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform, linux_only


def check_port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


@pytest.mark.docker
class TestDockerOperations(unittest.TestCase):

    def test_create_redis_starts(self):
        dm = DockerOperations(**get_test_local_env_overrides())
        dm.cleanup(True)
        dm.get_redis()
        check_port_is_open(6379)
        dm.stop_services()

    def test_create_db_starts(self):
        """
        This test is mostly scaffolding but could be useful in future for troubleshooting
        We mock out all b
        """
        dm = DockerOperations(**get_test_local_env_overrides())
        dm.cleanup(True)
        dm.get_postgres()
        check_port_is_open(5432)
        dm.stop_services()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @restart_local_platform(silent=True)
    def test_create_stack_starts(self, std_capture):
        dm = DockerOperations(**get_test_local_env_overrides())
        dm.cleanup(True)
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
                                          "/data")
            result = dm.sync_copy(result)[0]
            self.assertTrue(result)
            result = subprocess.run(['docker', 'exec', 'idmtools_workers', 'python', '/data/hello_world.py'],
                                    stdout=subprocess.PIPE)
            self.assertEqual(0, result.returncode)
            self.assertIn('Hello World!', result.stdout.decode('utf-8'))

    def test_start_stopped_container(self):
        # create first
        dm = DockerOperations(**get_test_local_env_overrides())
        dm.cleanup(True)
        dm.create_services()

        # stop workers
        worker_container = dm.get_workers()
        worker_container.stop()

        # get container again and make sure it is started
        worker_container = dm.get_workers()
        self.assertEqual(worker_container.status, 'running')
        dm.cleanup(True)

    @linux_only
    def test_port_taken_has_coherent_error(self):

        pl = DockerOperations(workers_ui_port=10000, **get_test_local_env_overrides())
        pl.cleanup(True)

        Handler = http.server.SimpleHTTPRequestHandler

        # run a http server that should use port 10000
        with socketserver.TCPServer(("", 10000), Handler) as httpd:
            httpd.server_activate()

            with self.assertRaises(EnvironmentError) as e:
                pl.create_services()
            httpd.server_close()

    def test_error_if_try_to_run_as_root(self):
        with self.assertRaises(ValueError) as mock:
            dm = DockerOperations(run_as="0:0")
            self.assertIn('You cannot run the containers as the root user!', mock.exception.args[0])
            dm.stop_services()
