import io
import os
import socket
import subprocess
import unittest.mock
from idmtools_platform_local.docker.DockerOperations import DockerOperations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import docker_test, restart_local_platform


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
    @restart_local_platform(silent=True)
    def test_create_stack_starts(self, std_capture):
        dm = DockerOperations()
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
            result = subprocess.run(['docker', 'exec', 'idmtools_workers', 'python', '/tmp/hello_world.py'],
                                    stdout=subprocess.PIPE)
            self.assertEqual(0, result.returncode)
            self.assertIn('Hello World!', result.stdout.decode('utf-8'))

    def test_port_taken_has_coherent_error(self):
        # create dummy port for listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10000)

        sock.bind(server_address)
        sock.listen(1)
        pl = DockerOperations(workers_ui_port=10000)
        pl.cleanup(True)
        with self.assertRaises(EnvironmentError) as e:
            pl.create_services()
            self.assertIn('Port 10000 is already taken', e.exception.args)

        sock.close()

    def test_error_if_try_to_run_as_root(self):
        with self.assertRaises(ValueError) as mock:
            dm = DockerOperations(run_as="0:0")
            self.assertIn('You cannot run the containers as the root user!', mock.exception.args[0])
            dm.stop_services()
