import os
import subprocess
import unittest
from docker.models.containers import Container
from unittest.mock import patch, MagicMock

import docker
from docker.errors import NotFound, APIError

from idmtools_platform_container.container_operations.docker_operations import stop_container, stop_all_containers, \
    validate_container_running, \
    get_container, pull_docker_image, is_docker_daemon_running, check_local_image, find_container_by_image, \
    is_docker_installed, compare_mounts, compare_container_mount


class TestDockerOperations(unittest.TestCase):

    @patch('idmtools_platform_container.container_operations.docker_operations.is_docker_installed')
    @patch('idmtools_platform_container.container_operations.docker_operations.is_docker_daemon_running')
    @patch('idmtools_platform_container.container_operations.docker_operations.check_local_image')
    @patch('idmtools_platform_container.container_operations.docker_operations.pull_docker_image')
    @patch('idmtools_platform_container.container_operations.docker_operations.stop_all_containers')
    @patch('idmtools_platform_container.container_operations.docker_operations.get_container')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_validate_container_running(self, mock_logger, mock_get_container, mock_stop_all_containers,
                                        mock_pull_docker_image, mock_check_local_image, mock_is_docker_daemon_running,
                                        mock_is_docker_installed):
        with(self.subTest("test_with_running_container")):
            platform = MagicMock()
            platform.docker_image = 'test_image'
            platform.force_start = False
            platform.new_container = False
            platform.include_stopped = False
            mock_is_docker_installed.return_value = True
            mock_is_docker_daemon_running.return_value = True
            mock_check_local_image.return_value = True
            mock_pull_docker_image.return_value = True
            mock_get_container.return_value = 'new_container_id'
            platform.retrieve_match_containers.return_value = [('running', mock_get_container)]
            # Calling ensure_docker_daemon_running function
            result = validate_container_running(platform)
            self.assertEqual(result, mock_get_container.short_id)

        with(self.subTest("test_with_stopped_container")):
            platform = MagicMock()
            platform.docker_image = 'test_image'
            platform.force_start = False
            platform.new_container = False
            platform.include_stopped = False
            mock_is_docker_installed.return_value = True
            mock_is_docker_daemon_running.return_value = True
            mock_check_local_image.return_value = True
            mock_pull_docker_image.return_value = True
            mock_get_container.return_value = 'new_container_id'
            platform.retrieve_match_containers.return_value = [('exited', mock_get_container)]
            # Calling ensure_docker_daemon_running function
            result = validate_container_running(platform)
            self.assertEqual(result, mock_get_container.short_id)

        with(self.subTest("test_with_no_container_start_new_container")):
            platform = MagicMock()
            platform.docker_image = 'test_image'
            platform.force_start = False
            platform.new_container = False
            platform.include_stopped = False
            platform.retrieve_match_containers.return_value = []
            mock_is_docker_installed.return_value = True
            mock_is_docker_daemon_running.return_value = True
            mock_check_local_image.return_value = True
            mock_pull_docker_image.return_value = True
            mock_get_container.return_value = 'new_container_id'
            platform.start_container.return_value = 'new_start_container_id'
            # Calling ensure_docker_daemon_running function
            result = validate_container_running(platform)
            self.assertEqual(result, 'new_start_container_id')

        with(self.subTest("test_with_running_container_force_start")):
            platform = MagicMock()
            platform.docker_image = 'test_image'
            platform.force_start = True
            platform.new_container = False
            platform.include_stopped = False
            mock_is_docker_installed.return_value = True
            mock_is_docker_daemon_running.return_value = True
            mock_check_local_image.return_value = True
            mock_pull_docker_image.return_value = True
            mock_get_container.return_value = 'new_container_id'
            platform.retrieve_match_containers.return_value = [('running', mock_get_container)]
            platform.start_container.return_value = 'new_start_container_short_id'
            # Calling ensure_docker_daemon_running function
            result = validate_container_running(platform)
            self.assertEqual(result, 'new_start_container_short_id')

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.user_logger')
    def test_get_container(self, mock_user_logger, mock_docker):
        # Test get_container exists
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container

        # Calling get_container function
        with self.subTest("test_with_container_id_exists"):
            result = get_container('test_container_id')
            mock_client.containers.get.assert_called_once_with('test_container_id')
            self.assertEqual(result, mock_container)

        # Test get_container does not exist
        mock_user_logger.reset_mock()
        with self.subTest("test_with_container_id_no_exists"):
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_container = MagicMock()
            mock_client.containers.get.return_value = mock_container
            mock_client.containers.get.side_effect = NotFound('Not found')

            # Calling get_container function
            result = get_container('test_container_id')
            self.assertEqual(mock_client.containers.get.call_count, 1)
            self.assertIsNone(result)
            mock_user_logger.debug.assert_called_with(f"Container with ID test_container_id not found.")

        # Test get_container api error
        mock_user_logger.reset_mock()
        with self.subTest("test_with_container_api_error"):
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_container = MagicMock()
            mock_client.containers.get.return_value = mock_container
            mock_client.containers.get.side_effect = APIError('API error')

            # Calling get_container function
            result = get_container('test_container_id')

            self.assertEqual(mock_client.containers.get.call_count, 1)
            self.assertIsNone(result)
            mock_user_logger.debug.assert_called_with(
                f"Error retrieving container with ID test_container_id: {mock_client.containers.get.side_effect}")

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_find_container_by_image(self, mock_logger, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        with self.subTest("test_running_status"):
            mock_container = MagicMock()
            mock_container.status = 'running'
            mock_container.image.tags = ['test_image']
            mock_client.containers.list.return_value = [mock_container]

            # Calling find_container_by_image function
            result = find_container_by_image('test_image')
            self.assertEqual(result, {mock_container.status: [mock_container]})
            mock_logger.debug.assert_called_with(
                f"Image test_image found in container ({mock_container.status}): {str(result['running'][0].short_id)}")

        # Test find_container_by_image function with include_stopped_containers as True
        mock_logger.reset_mock()
        with self.subTest("test_with_include_stopped_containers_as_True"):
            # Create mock_container with status as 'exited'
            mock_container = MagicMock()
            mock_container.status = 'exited'
            mock_container.image.tags = ['test_image']
            # Create another mock_container with status as 'running'
            mock_container1 = MagicMock()
            mock_container1.status = 'running'
            mock_container1.image.tags = ['test_image']
            mock_client.containers.list.return_value = [mock_container, mock_container1]
            result = find_container_by_image('test_image', include_stopped=True)
            self.assertEqual(result['exited'][0], mock_container)
            self.assertEqual(result['running'][0], mock_container1)

        # test find_container_by_image function with include_stopped_containers as True but invalid status
        mock_logger.reset_mock()
        with self.subTest("test_with_include_stopped_containers_as_True_and_invalid_status"):
            # Create mock_container with status as 'exited'
            mock_container = MagicMock()
            mock_container.status = 'exited_invalid'
            mock_container.image.tags = ['test_image']

            mock_client.containers.list.return_value = [mock_container]
            result = find_container_by_image('test_image', include_stopped=True)
            self.assertEqual(result, {})

    @patch('subprocess.run')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_docker_installed(self, mock_logger, mock_subprocess):
        mock_result = MagicMock()
        with self.subTest("test_with_docker_installed"):
            mock_result.returncode = 0
            mock_result.stdout = 'Docker version 20.10.7, build f0df350'
            mock_subprocess.return_value = mock_result

            # Calling is_docker_installed function
            result = is_docker_installed()

            self.assertTrue(result)
            mock_subprocess.assert_called_with(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True)
            mock_logger.debug.assert_called_with(f"Docker is installed: {mock_result.stdout.strip()}")

        # Test is_docker_installed function with not installed
        mock_logger.reset_mock()
        with self.subTest("test_with_docker_not_installed"):
            mock_result.returncode = -1
            mock_result.stderr = 'Docker is not installed'
            mock_subprocess.return_value = mock_result

            result = is_docker_installed()

            self.assertFalse(result)
            mock_logger.debug.assert_called_with(f"Docker is not installed. Error: {mock_result.stderr.strip()}")

        # Test is_docker_installed function with not installed
        mock_logger.reset_mock()
        with self.subTest("test_with_docker_exception"):
            mock_subprocess.side_effect = FileNotFoundError

            result = is_docker_installed()

            self.assertFalse(result)
            mock_logger.debug.assert_called_with("Docker is not installed or not found in PATH.")

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_is_docker_daemon_running(self, mock_logger, mock_docker):
        # Test is_docker_daemon_running function
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        # Test docker daemon is running
        with self.subTest("test_with_docker_daemon_running"):
            result = is_docker_daemon_running()
            mock_docker.assert_called_once()
            mock_client.ping.assert_called_once()
            self.assertTrue(result)
            mock_logger.debug.assert_called_with("Docker daemon is running.")

        # Test docker daemon running with exception
        mock_logger.reset_mock()
        with self.subTest("test_with_docker_daemon_exception"):
            mock_client.ping.side_effect = docker.errors.DockerException('Error')
            mock_docker.return_value = mock_client
            result = is_docker_daemon_running()
            self.assertEqual(mock_docker.call_count, 2)
            self.assertEqual(mock_client.ping.call_count, 2)
            self.assertFalse(result)
            mock_logger.debug.assert_called_with("Error checking Docker daemon:", mock_client.ping.side_effect)

        # Test docker daemon running with APIError
        mock_logger.reset_mock()
        with self.subTest("test_with_docker_daemon_api_error"):
            mock_client.ping.side_effect = docker.errors.APIError('Error')
            mock_docker.return_value = mock_client
            result = is_docker_daemon_running()
            self.assertEqual(mock_docker.call_count, 3)
            self.assertEqual(mock_client.ping.call_count, 3)
            self.assertFalse(result)
            mock_logger.debug.assert_called_with("Docker daemon is not running:", mock_client.ping.side_effect)

    @patch('docker.from_env')
    def test_check_local_image(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_image = MagicMock()
        mock_image.tags = ['test_image']
        mock_client.images.list.return_value = [mock_image]

        # Test with local image found
        with self.subTest("test_with_local_image_found"):
            result = check_local_image('test_image')
            self.assertTrue(result)

        # test local image not found
        with self.subTest("test_with_local_image_not_found"):
            result = check_local_image('non_existent_image')
            self.assertFalse(result)

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    @patch('idmtools_platform_container.container_operations.docker_operations.user_logger')
    def test_pull_docker_image(self, mock_user_logger, mock_logger, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        # Test pull docker image success
        with self.subTest("test_with_pull_image_success"):
            result = pull_docker_image('test_image')
            self.assertTrue(result)
            mock_client.images.pull.assert_called_with('test_image:latest')
            mock_user_logger.info.assert_called_with(f"Pulling image test_image:latest ...")
            mock_logger.debug.assert_called_with(f"Successfully pulled test_image:latest")

        # Test pull docker image success with image tage
        mock_user_logger.reset_mock()
        mock_logger.reset_mock()
        with self.subTest("test_with_pull_image_success"):
            result = pull_docker_image('test_image:1.0.1')
            self.assertTrue(result)
            mock_client.images.pull.assert_called_with('test_image:1.0.1')
            mock_user_logger.info.assert_called_with(f"Pulling image test_image:1.0.1 ...")
            mock_logger.debug.assert_called_with(f"Successfully pulled test_image:1.0.1")

        # Test pull docker image failure
        mock_user_logger.reset_mock()
        mock_logger.reset_mock()
        with self.subTest("test_with_pull_image_failure"):
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_client.images.pull.side_effect = docker.errors.APIError('Error pulling image')
            result = pull_docker_image('test_image')
            self.assertFalse(result)
            mock_client.images.pull.assert_called_with('test_image:latest')
            mock_user_logger.info.assert_called_with(f"Pulling image test_image:latest ...")
            mock_logger.debug.assert_called_with(
                f"Error pulling test_image:latest: {mock_client.images.pull.side_effect}")

    def test_compare_mount(self):
        # Test_compare_mounts_same
        with self.subTest("test_compare_mounts_same"):
            mounts1 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source2', 'Destination': '/destination2'}]
            mounts2 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source2', 'Destination': '/destination2'}]
            result = compare_mounts(mounts1, mounts2)
            self.assertTrue(result)

        # Test_compare_mounts_not same
        with self.subTest("test_compare_mounts_not_same"):
            mounts1 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source2', 'Destination': '/destination2'}]
            mounts2 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source3', 'Destination': '/destination3'}]
            result = compare_mounts(mounts1, mounts2)
            self.assertFalse(result)

    @patch(
        'idmtools_platform_container.container_operations.docker_operations.get_container')
    def test_compare_container_mount(self, mock_get_container):
        # Test_compare_container_mount_same
        with self.subTest("test_compare_container_mounts_same"):
            mounts1 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source2', 'Destination': '/destination2'}]
            mounts2 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source2', 'Destination': '/destination2'}]
            mock_container1 = MagicMock()
            mock_container1.attrs = {'Mounts': mounts1}
            mock_container2 = MagicMock()
            mock_container2.attrs = {'Mounts': mounts2}
            mock_get_container.side_effect = [mock_container1, mock_container2]
            result = compare_container_mount(mock_container1, mock_container2)
            self.assertTrue(result)

        # Test_compare_mounts_not same
        with self.subTest("test_compare_container_mounts_not_same"):
            mounts1 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source2', 'Destination': '/destination2'}]
            mounts2 = [{'Type': 'bind', 'Mode': 'rw', 'Source': '/source1', 'Destination': '/destination1'},
                       {'Type': 'bind', 'Mode': 'rw', 'Source': '/source3', 'Destination': '/destination3'}]
            mock_container1 = MagicMock()
            mock_container1.attrs = {'Mounts': mounts1}
            mock_container2 = MagicMock()
            mock_container2.attrs = {'Mounts': mounts2}
            mock_get_container.side_effect = [mock_container1, mock_container2]
            result = compare_container_mount(mock_container1, mock_container2)
            self.assertFalse(result)

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.get_container')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_stop_container(self, mock_logger, mock_get_container, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_logger.reset_mock()
        # test stop with container object
        with self.subTest("test_stop_container_by_container_instance"):
            mock_container = MagicMock(spec=Container)
            # Calling stop_container function
            stop_container(mock_container)
            mock_container.stop.assert_called_once()
            mock_container.remove.assert_called_once()
            mock_logger.debug.call_args_list[0].assert_called_with(f"Container {mock_container} has been stopped.")
            mock_logger.debug.call_args_list[1].assert_called_with(f"Container {mock_container} has been removed.")

        # test stop_container with container id
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_container_id"):
            mock_container = MagicMock(spec=Container)
            mock_container.id = 'test_container_id'
            mock_get_container.return_value = mock_container

            # Calling stop_container function
            stop_container(mock_container.id)
            mock_container.stop.assert_called_once()
            mock_container.remove.assert_called_once()
            mock_logger.debug.call_args_list[0].assert_called_with(f"Container {mock_container} has been stopped.")
            mock_logger.debug.call_args_list[1].assert_called_with(f"Container {mock_container} has been removed.")

        # test stop_container with invalid container
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_invalid_container"):
            mock_container = MagicMock()
            # Calling stop_container function
            with self.assertRaises(TypeError) as ex:
                stop_container(mock_container)
            self.assertIn("Invalid container object.", ex.exception.args[0])
            self.assertEqual(mock_container.stop.call_count, 0)  # not call stop
            self.assertEqual(mock_container.remove.call_count, 0)  # not call remove

        # test stop_container with non-exist container_id
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_container_id_and_not_found"):
            mock_get_container.side_effect = NotFound(
                'Container not found')  # raise NotFound exception in get_container

            # Calling stop_container function
            stop_container("test_container_id")
            mock_logger.debug.assert_called_with(f"Container test_container_id not found.")
            self.assertEqual(mock_container.stop.call_count, 0)  # not call stop
            self.assertEqual(mock_container.remove.call_count, 0)  # not call remove

        # test stop_container with NotFound exception
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_non-exist_container"):
            mock_container = MagicMock(spec=Container)
            mock_container.short_id = 'test_container_123'
            mock_container.stop.side_effect = MagicMock(side_effect=NotFound('Container not found'))
            # Calling stop_container function
            stop_container(mock_container)
            mock_logger.debug.assert_called_with(f"Container {mock_container} not found.")
            mock_container.stop.assert_called_once()
            self.assertEqual(mock_container.remove.call_count, 0)  # not call remove

        # test stop_container with APIError exception
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_non-exist_container"):
            mock_container = MagicMock(spec=Container)
            mock_container.short_id = 'test_container_123'
            mock_container.stop.side_effect = MagicMock(side_effect=APIError('DockerAPIError'))
            # Calling stop_container function
            stop_container(mock_container)
            mock_logger.debug.assert_called_with(f"Error stopping container {mock_container}: DockerAPIError")
            mock_container.stop.assert_called_once()
            self.assertEqual(mock_container.remove.call_count, 0)  # not call remove

        # test stop_container with remove=False
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_container_instance_remove_false"):
            mock_container = MagicMock(spec=Container)
            # Calling stop_container function
            stop_container(mock_container, remove=False)
            mock_container.stop.assert_called_once()
            self.assertEqual(mock_container.remove.call_count, 0)  # not call remove
            mock_logger.debug.assert_called_with(f"Container {mock_container} has been stopped.")

    @patch('docker.from_env')
    def test_stop_all_containers(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        with self.subTest("test_stop_all_container_by_container_objects"):
            mock_container1 = MagicMock(spec=Container)
            mock_container2 = MagicMock(spec=Container)

            # Calling stop_all_containers function
            stop_all_containers([mock_container1, mock_container2])

            # Assert
            mock_container1.stop.assert_called_once()
            mock_container1.remove.assert_called_once()
            mock_container2.stop.assert_called_once()
            mock_container2.remove.assert_called_once()
        with self.subTest("test_stop_all_container_by_remove_false"):
            mock_container1 = MagicMock(spec=Container)
            mock_container2 = MagicMock(spec=Container)

            # Calling stop_all_containers function
            stop_all_containers([mock_container1, mock_container2], remove=False)

            # Assert
            mock_container1.stop.assert_called_once()
            mock_container2.stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
