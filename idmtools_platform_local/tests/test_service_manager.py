import http.server
import io
import os
import socket
import socketserver
import subprocess
import unittest.mock

import docker
import pytest
from idmtools_platform_local.infrastructure.docker_io import DockerIO
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform, linux_only, skip_api_host


def check_port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


@pytest.mark.docker
@pytest.mark.local_platform_internals
@pytest.mark.serial
class TestServiceManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = docker.from_env()

    def test_create_redis_starts(self):
        sm = DockerServiceManager(self.client, **get_test_local_env_overrides())
        sm.cleanup(True)
        sm.get_network()
        sm.get('redis')
        check_port_is_open(6379)
        sm.stop_services()

    def test_create_redis_custom_port(self):
        config = get_test_local_env_overrides()
        config['redis_port'] = 6399
        sm = DockerServiceManager(self.client, **config)
        sm.cleanup(True)
        sm.get_network()
        sm.get('redis')
        check_port_is_open(6399)
        sm.stop_services()

    @pytest.mark.timeout(60)
    def test_create_db_starts(self):
        """
        This test is mostly scaffolding but could be useful in future for troubleshooting
        We mock out all b
        """
        sm = DockerServiceManager(self.client, **get_test_local_env_overrides())
        sm.cleanup(True)
        sm.get_network()
        sm.get('postgres')
        check_port_is_open(5432)
        sm.stop_services()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @restart_local_platform(silent=True)
    @pytest.mark.timeout(60)
    @pytest.mark.long
    def test_create_stack_starts(self, std_capture):
        sm = DockerServiceManager(self.client, **get_test_local_env_overrides())
        do = DockerIO()
        sm.cleanup(True)
        sm.create_services()

        with self.subTest("can_run_containers"):
            self.assertEqual(0, os.system(f'docker exec idmtools_workers docker run hello-world'))

        with self.subTest("can_copy_to_container"):
            worker_container = sm.get('workers')

            result = do.copy_to_container(worker_container,
                                          file=os.path.join(COMMON_INPUT_PATH, "python", "hello_world.py"),
                                          destination_path="/data")
            result = do.sync_copy(result)[0]
            self.assertTrue(result)
            result = subprocess.run(['docker', 'exec', 'idmtools_workers', 'python', '/data/hello_world.py'],
                                    stdout=subprocess.PIPE)
            self.assertEqual(0, result.returncode)
            self.assertIn('Hello World!', result.stdout.decode('utf-8'))

    @pytest.mark.timeout(60)
    @pytest.mark.long
    def test_start_stopped_container(self):
        sm = DockerServiceManager(self.client, **get_test_local_env_overrides())
        sm.cleanup(True)
        sm.create_services()

        # stop workers
        worker_container = sm._services['workers']
        worker_container.stop()

        # get container again and make sure it is started
        worker_container = sm.get('workers')

        self.assertEqual(worker_container.status, 'running')
        sm.cleanup(True)

    # skip this test in docker in docker tests since the port binding is actually on the true host
    @linux_only
    @skip_api_host
    @pytest.mark.timeout(60)
    def test_port_taken_has_coherent_error(self):
        pl = DockerServiceManager(self.client, workers_ui_port=10000, **get_test_local_env_overrides())
        pl.cleanup(True)

        Handler = http.server.SimpleHTTPRequestHandler

        # run a http server that should use port 10000
        with socketserver.TCPServer(("", 10000), Handler) as httpd:
            httpd.server_activate()

            with self.assertRaises(EnvironmentError):
                pl.create_services()
            httpd.server_close()
        pl.cleanup()

    def test_error_if_try_to_run_as_root(self):
        with self.assertRaises(ValueError) as mock:
            dm = DockerServiceManager(self.client, run_as="0:0", **get_test_local_env_overrides())
            dm.create_services()
            self.assertIn('You cannot run the containers as the root user!', mock.exception.args[0])
            dm.stop_services()
