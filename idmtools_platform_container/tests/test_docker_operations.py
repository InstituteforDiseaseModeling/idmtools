import platform
import subprocess
import unittest
from pathlib import Path
from docker.models.containers import Container
from unittest.mock import patch, MagicMock
import docker
from docker.errors import NotFound, APIError
from idmtools_platform_container.container_operations.docker_operations import stop_container, stop_all_containers, \
    validate_container_running, \
    get_container, pull_docker_image, is_docker_daemon_running, check_local_image, find_container_by_image, \
    is_docker_installed, compare_mounts, compare_container_mount, sort_containers_by_start, get_containers, \
    get_working_containers, list_running_jobs, Job, find_running_job
from idmtools_platform_container.container_platform import ContainerPlatform
from idmtools_platform_container.utils.general import normalize_path, is_valid_uuid


class TestDockerOperations(unittest.TestCase):

    @patch('idmtools_platform_container.container_operations.docker_operations.is_docker_installed')
    @patch('idmtools_platform_container.container_operations.docker_operations.is_docker_daemon_running')
    @patch('idmtools_platform_container.container_operations.docker_operations.check_local_image')
    @patch('idmtools_platform_container.container_operations.docker_operations.pull_docker_image')
    @patch('idmtools_platform_container.container_operations.docker_operations.stop_all_containers')
    @patch('idmtools_platform_container.container_operations.docker_operations.sort_containers_by_start')
    @patch('idmtools_platform_container.container_platform.ContainerPlatform.retrieve_match_containers')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_validate_container_running(self, mock_logger, mock_retrieve_match_containers,
                                        mock_sort_containers_by_start, mock_stop_all_containers,
                                        mock_pull_docker_image, mock_check_local_image, mock_is_docker_daemon_running,
                                        mock_is_docker_installed):
        platform = MagicMock(spec=ContainerPlatform)
        platform.docker_image = 'test_image'
        platform.force_start = False
        platform.new_container = False
        platform.include_stopped = False
        platform.container_prefix = None
        mock_is_docker_installed.return_value = True
        mock_is_docker_daemon_running.return_value = True
        mock_check_local_image.return_value = True
        mock_pull_docker_image.return_value = True
        with (self.subTest("test_with_running_container")):
            mock_container1 = MagicMock(short_id='test_container_id1')
            mock_container2 = MagicMock(short_id='test_container_id2')
            mock_container3 = MagicMock(short_id='test_container_id3')
            mock_retrieve_match_containers.return_value = [('running', mock_container1),
                                                           ('running', mock_container2),
                                                           ('stopped', mock_container3)]
            mock_sort_containers_by_start.return_value = [mock_container2,
                                                          mock_container1]  # assume container2 is the latest
            platform.retrieve_match_containers.return_value = mock_retrieve_match_containers.return_value
            result = validate_container_running(platform)
            self.assertEqual(result, mock_container2.short_id)
            mock_logger.debug.assert_called_with(f"Pick running container {mock_container2.short_id}.")

        with (self.subTest("test_with_stopped_container")):
            mock_container1 = MagicMock(short_id='test_container_id1')
            mock_container2 = MagicMock(short_id='test_container_id2')
            mock_retrieve_match_containers.return_value = [('exited', mock_container1),
                                                           ('stopped', mock_container2)]
            mock_sort_containers_by_start.return_value = [mock_container2,
                                                          mock_container1]  # assume container2 is the latest
            platform.retrieve_match_containers.return_value = mock_retrieve_match_containers.return_value
            result = validate_container_running(platform)
            self.assertEqual(result, mock_container2.short_id)
            mock_logger.debug.assert_called_with(f"Pick and restart the stopped container {mock_container2.short_id}.")

        with (self.subTest("test_with_no_container_start_new_container")):
            platform.retrieve_match_containers.return_value = []
            mock_sort_containers_by_start.return_value = []
            platform.start_container.return_value = 'new_start_container_id'
            result = validate_container_running(platform)
            self.assertEqual(result, 'new_start_container_id')
            mock_logger.debug.call_args_list[0].assert_called_with(f"Start container: {platform.docker_image}.")
            mock_logger.debug.call_args_list[1].assert_called_with(f"New container ID: new_start_container_id.")

        with (self.subTest("test_with_running_container_force_start")):
            platform.force_start = True
            mock_container = MagicMock(short_id='test_container_id')
            platform.retrieve_match_containers.return_value = [('running', mock_container)]
            platform.start_container.return_value = 'new_container_id'
            result = validate_container_running(platform)
            self.assertEqual(result, 'new_container_id')
            mock_logger.debug.call_args_list[0].assert_called_with(f"Start container: {platform.docker_image}.")
            mock_logger.debug.call_args_list[1].assert_called_with(f"New container ID: new_container_id.")
        with (self.subTest("test_with_docker_not_installed")):
            mock_is_docker_installed.return_value = False
            with patch(
                    'idmtools_platform_container.container_operations.docker_operations.user_logger') as mock_user_logger:
                with self.assertRaises(SystemExit) as ex:
                    validate_container_running(platform)
                    mock_user_logger.error.assert_called_with("Docker is not installed.")
        mock_is_docker_installed.return_value = True  # reset to true from previous subtest
        with (self.subTest("test_with_is_docker_daemon_running")):
            with patch(
                    'idmtools_platform_container.container_operations.docker_operations.user_logger') as mock_user_logger:
                mock_is_docker_daemon_running.return_value = False
                with self.assertRaises(SystemExit) as cm:
                    validate_container_running(platform)
                mock_user_logger.error.assert_called_once_with("Docker daemon is not running.")
                self.assertEqual(cm.exception.code, -1)
        mock_is_docker_daemon_running.return_value = True  # reset to true from previous subtest
        with (self.subTest("test_with_failed_check_local_image_and_failed_pull_image")):
            with patch(
                    'idmtools_platform_container.container_operations.docker_operations.user_logger') as mock_user_logger:
                mock_check_local_image.return_value = False
                mock_pull_docker_image.return_value = False
                with self.assertRaises(SystemExit) as cm:
                    validate_container_running(platform)
                mock_user_logger.info.assert_called_once_with(
                    f"Image {platform.docker_image} does not exist, pull the image first.")
                mock_user_logger.error.assert_called_once_with(
                    f"/!\\ ERROR: Failed to pull image {platform.docker_image}.")
                self.assertEqual(cm.exception.code, -1)

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_get_container(self, mock_logger, mock_docker):
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
        mock_logger.reset_mock()
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
            mock_logger.debug.assert_called_with(f"Container with ID test_container_id not found.")

        # Test get_container api error
        mock_logger.reset_mock()
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
            mock_logger.debug.assert_called_with(
                f"Error retrieving container with ID test_container_id: {mock_client.containers.get.side_effect}")

    @patch('docker.from_env')
    def test_find_container_by_image(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        with self.subTest("test_running_status"):
            mock_container = MagicMock()
            mock_container.status = 'running'
            mock_container.attrs = {'Config': {'Image': 'test_image'}}
            mock_client.containers.list.return_value = [mock_container]

            # Calling find_container_by_image function
            result = find_container_by_image('test_image')
            self.assertDictEqual(result, {mock_container.status: [mock_container], 'stopped': []})

        # Test find_container_by_image function with include_stopped_containers as True
        with self.subTest("test_with_include_stopped_containers_as_True"):
            # Create mock_container with status as 'exited'
            mock_container = MagicMock()
            mock_container.status = 'exited'
            mock_container.attrs = {'Config': {'Image': 'test_image'}}
            # Create another mock_container with status as 'running'
            mock_container1 = MagicMock()
            mock_container1.status = 'running'
            mock_container1.image.tags = ['test_image']
            mock_client.containers.list.return_value = [mock_container, mock_container1]
            result = find_container_by_image('test_image', include_stopped=True)
            self.assertDictEqual(result, {'stopped': [mock_container], 'running': []})

        # test find_container_by_image function with include_stopped_containers as True but invalid status
        with self.subTest("test_with_include_stopped_containers_as_True_and_invalid_status"):
            # Create mock_container with status as 'exited'
            mock_container = MagicMock()
            mock_container.status = 'exited_invalid'
            mock_container.attrs = {'Config': {'Image': 'test_image'}}
            mock_client.containers.list.return_value = [mock_container]
            result = find_container_by_image('test_image', include_stopped=True)
            self.assertEqual(result, {'running': [], 'stopped': []})

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
            mock_logger.debug.assert_called_with(f"Error checking Docker daemon: {mock_client.ping.side_effect}")

        # Test docker daemon running with APIError
        mock_logger.reset_mock()
        with self.subTest("test_with_docker_daemon_api_error"):
            mock_client.ping.side_effect = docker.errors.APIError('Error')
            mock_docker.return_value = mock_client
            result = is_docker_daemon_running()
            self.assertEqual(mock_docker.call_count, 3)
            self.assertEqual(mock_client.ping.call_count, 3)
            self.assertFalse(result)
            mock_logger.debug.assert_called_with(f"Docker daemon is not running: {mock_client.ping.side_effect}")

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
        with self.subTest("test_stop_container_by_running_container_instance"):
            mock_container = MagicMock(spec=Container)
            mock_container.status = 'running'
            # Calling stop_container function
            stop_container(mock_container)
            mock_container.stop.assert_called_once()
            mock_container.remove.assert_called_once()
            mock_logger.debug.call_args_list[0].assert_called_with(f"Container {mock_container} has been stopped.")
            mock_logger.debug.call_args_list[1].assert_called_with(f"Container {mock_container} has been removed.")

        # test stop_container with container id
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_running_container_id"):
            mock_container = MagicMock(spec=Container)
            mock_container.id = 'test_container_id'
            mock_get_container.return_value = mock_container
            mock_container.status = 'running'
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
            with self.assertRaises(SystemExit) as ex:
                stop_container("test_container_id")
                mock_logger.debug.assert_called_with(f"Container with ID test_container_id not found.")
                self.assertEqual(mock_container.stop.call_count, 0)  # not call stop
                self.assertEqual(mock_container.remove.call_count, 0)  # not call remove

        # test stop_container with NotFound exception
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_non-exist_container"):
            mock_container = MagicMock(spec=Container)
            mock_container.short_id = 'test_container_123'
            mock_container.status = 'running'
            mock_container.stop.side_effect = MagicMock(side_effect=NotFound('Container not found'))
            # Calling stop_container function
            with self.assertRaises(SystemExit) as ex:
                stop_container(mock_container)
                mock_container.stop.assert_called_once()
                mock_container.remove.assert_not_called()
                mock_logger.debug.assert_called_with(f"Container {mock_container.short_id} not found.")

        # test stop_container with APIError exception
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_non-exist_container"):
            mock_container = MagicMock(spec=Container)
            mock_container.short_id = 'test_container_123'
            mock_container.stop.side_effect = MagicMock(side_effect=APIError('DockerAPIError'))
            mock_container.status = 'running'
            # Calling stop_container function
            with self.assertRaises(SystemExit) as ex:
                stop_container(mock_container)
                mock_container.stop.assert_called_once()
                mock_container.remove.assert_not_called()
                mock_logger.debug.assert_called_with(f"Error stopping container {mock_container}: DockerAPIError")

        # test stop_container with remove=False
        mock_logger.reset_mock()
        with self.subTest("test_stop_container_by_container_instance_remove_false"):
            mock_container = MagicMock(spec=Container)
            mock_container.status = 'running'
            # Calling stop_container function
            stop_container(mock_container, remove=False)
            mock_container.stop.assert_called_once()
            mock_container.remove.assert_not_called()
            mock_logger.debug.assert_called_with(f"Container {mock_container} has been stopped.")

        # test stop with stopped container
        with self.subTest("test_stop_container_by_running_container_instance"):
            mock_container = MagicMock(spec=Container)
            mock_container.status = 'exited'
            # Calling stop_container function
            stop_container(mock_container, remove=False)
            mock_container.stop.assert_not_called()
            mock_container.remove.assert_not_called()

    @patch('docker.from_env')
    @patch('idmtools_platform_container.container_operations.docker_operations.list_running_jobs')
    def test_stop_all_containers(self, mock_docker_env, mock_list_running_jobs):
        mock_client = MagicMock()
        mock_docker_env.return_value = mock_client
        with self.subTest("test_stop_all_container_by_container_objects"):
            # Create mock containers
            mock_container1 = MagicMock(spec=Container, status='running', short_id='container1_id')
            mock_container2 = MagicMock(spec=Container, status='running', short_id='container2_id')
            mock_containers = [mock_container1, mock_container2]

            # Define the side_effect function for list_running_jobs
            def side_effect(container_id):
                if container_id == 'container1_id':
                    return ['job1', 'job2']  # Jobs for container 1
                elif container_id == 'container2_id':
                    return []  # No jobs for container 2
                return None

            mock_list_running_jobs.side_effect = side_effect
            stop_all_containers(mock_containers)
            mock_container1.stop.assert_not_called()    # stop not called since jobs are running in container 1
            mock_container1.remove.assert_not_called()
            mock_container2.stop.assert_not_called()
            mock_container2.assert_not_called()
        with self.subTest("test_stop_all_container_by_keep_running_false"):
            mock_container1 = MagicMock(spec=Container, status='running', short_id='container1_id')
            mock_container2 = MagicMock(spec=Container, status='exited', short_id='container2_id')
            mock_containers = [mock_container1, mock_container2]

            def side_effect(container_id):
                if container_id == 'container1_id':
                    return ['job1', 'job2']  # Jobs for container 1
                elif container_id == 'container2_id':
                    return []  # No jobs for container 2
                return None

            mock_list_running_jobs.side_effect = side_effect
            # Calling stop_all_containers function
            stop_all_containers(mock_containers, keep_running=False)
            mock_container1.stop.assert_called_once()  # stop called since keep_running is False even if jobs are running
            mock_container2.stop.assert_not_called()

    def test_sort_containers_by_start(self):
        # Create mock containers with different 'StartedAt' times
        mock_container1 = MagicMock(spec=Container)
        mock_container1.attrs = {'State': {'StartedAt': '2024-01-01T00:00:00.000000Z'}}
        mock_container2 = MagicMock(spec=Container)
        mock_container2.attrs = {'State': {'StartedAt': '2024-01-02T00:00:00.000000Z'}}
        mock_container3 = MagicMock(spec=Container)
        mock_container3.attrs = {'State': {'StartedAt': '2024-01-03T00:00:00.000000Z'}}

        # Call sort_containers_by_start with the mock containers
        sorted_containers = sort_containers_by_start([mock_container1, mock_container2, mock_container3])

        # Check if the containers are sorted in the correct order
        self.assertEqual(sorted_containers, [mock_container3, mock_container2, mock_container1])

    def test_test_normalize_path(self):
        # Test normalize_path with string path
        with self.subTest("test_normalize_path_with_string_path"):
            path = "C:\\Users\\Test\\Documents"
            expected = "c:/users/test/documents"
            if platform.system() == 'Windows':
                self.assertEqual(normalize_path(path), expected)
            else:
                self.assertEqual(normalize_path(path).lower(), expected)

        # Test normalize_path with pathlib
        with self.subTest("test_normalize_path_with_pathlib"):
            path = Path("C:\\Users\\Test\\Documents")
            expected = "c:/users/test/documents"
            if platform.system() == 'Windows':
                self.assertEqual(normalize_path(path), expected)
            else:
                self.assertEqual(normalize_path(path).lower(), expected)

        # Test normalize_path with forward slashes
        with self.subTest("test_normalize_path_with_forward_slashes"):
            path = "C:/Users/Test/Documents"
            expected = "c:/users/test/documents"
            if platform.system() == 'Windows':
                self.assertEqual(normalize_path(path), expected)
            else:
                self.assertEqual(normalize_path(path).lower(), expected)

        # Test normalize_path with backslashes
        with self.subTest("test_normalize_path_with_backslashes"):
            path = "C:\\Users\\Test\\Documents\\"
            expected = "c:/users/test/documents"
            if platform.system() == 'Windows':
                self.assertEqual(normalize_path(path), expected)
            else:
                self.assertEqual(normalize_path(path).lower(), expected)

        # Test normalize_path with mix slashes
        with self.subTest("test_normalize_path_with_mixedslashes"):
            path = f"C:\\Users\\Test/Documents\\"
            expected = "c:/users/test/documents"
            if platform.system() == 'Windows':
                self.assertEqual(normalize_path(path), expected)
            else:
                self.assertEqual(normalize_path(path).lower(), expected)

    @patch('docker.from_env')
    def test_list_containers(self, mock_docker_env):
        mock_client = MagicMock()
        mock_docker_env.return_value = mock_client
        with self.subTest("test_list_containers_running_only"):
            mock_container_running = MagicMock()
            mock_container_running.status = 'running'
            mock_client.containers.list.return_value = [mock_container_running]
            result = get_containers(include_stopped=False)
            self.assertIn('running', result)
            self.assertEqual(len(result['running']), 1)
            self.assertNotIn('exited', result)
        with self.subTest("test_list_containers_include_stopped"):
            mock_container_running = MagicMock()
            mock_container_running.status = 'running'
            mock_container_stopped = MagicMock()
            mock_container_stopped.status = 'exited'
            mock_client.containers.list.return_value = [mock_container_running, mock_container_stopped]
            result = get_containers(include_stopped=True)
            self.assertIn('running', result)
            self.assertIn('stopped', result)
            self.assertEqual(len(result['running']), 1)
            self.assertEqual(len(result['stopped']), 1)

    @patch('idmtools_platform_container.container_operations.docker_operations.get_container')
    @patch('idmtools_platform_container.container_operations.docker_operations.JobHistory.verify_container')
    @patch('idmtools_platform_container.container_operations.docker_operations.get_containers')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    def test_get_working_containers(self, mock_logger, mock_get_containers, mock_verify_container,
                                                       mock_get_container):
        # test not given any container id and expect return running container ids with entity=False
        with self.subTest("test_get_working_containers_entity_false"):
            mock_container1 = MagicMock(short_id='container1')
            mock_container2 = MagicMock(short_id='container2')
            mock_get_containers.return_value = {'running': [mock_container1, mock_container2]}
            result = get_working_containers()  # should return container1 and container2's ids
            self.assertEqual(len(result), 2)
            self.assertIn(mock_container1.short_id, result)
            self.assertIn(mock_container2.short_id, result)
        # test not given any container id and expect return running container ids with entity=False
        with self.subTest("test_get_working_containers_only_running_containers"):
            mock_container1 = MagicMock(short_id='container1')
            mock_container2 = MagicMock(short_id='container2')
            mock_get_containers.return_value = {'stopped': [mock_container1], 'running': [mock_container2]}
            result = get_working_containers()  # should return container2's ids
            self.assertEqual(len(result), 1)
            self.assertTrue(mock_container2.short_id, result)
        # test not given any container id and expect return running container object with entity=True
        with self.subTest("test_get_working_containers_entity_true"):
            mock_container1 = MagicMock(short_id='container1')
            mock_container2 = MagicMock(short_id='container2')
            mock_get_containers.return_value = {'running': [mock_container1, mock_container2]}
            result = get_working_containers(entity=True)   # should return container object
            self.assertEqual(len(result), 2)
            self.assertIn(mock_container1, result)
            self.assertIn(mock_container2, result)
        # test given container id and container is in history and container is running
        with self.subTest("test_get_working_containers_with_id_found"):
            mock_verify_container.return_value = True
            mock_container = MagicMock(short_id='container1')
            mock_container.status = 'running'
            mock_get_container.return_value = mock_container
            result = get_working_containers(container_id='container1')  # should return container id
            self.assertEqual(len(result), 1)
            self.assertTrue([mock_container.short_id], result)
        # test given container id and container is in history but container is not running
        with self.subTest("test_get_working_containers_with_id_found_not_running"):
            mock_verify_container.return_value = True
            mock_container = MagicMock(short_id='container1')
            mock_container.status = 'exited'
            mock_get_container.return_value = mock_container
            result = get_working_containers(container_id='container1')  # should return container id
            self.assertEqual(len(result), 0)
            mock_logger.warning.assert_called_with(f"Container {mock_container.short_id} is not running.")
        # test given container id and container is in history but container is deleted
        with self.subTest("test_get_working_containers_with_id_found_not_existing_anymore"):
            mock_verify_container.return_value = True
            mock_container = MagicMock(short_id='container1')
            mock_container.status = 'exited'
            mock_get_container.return_value = None
            result = get_working_containers(container_id='container1')  # should return container id
            self.assertEqual(len(result), 0)
            mock_logger.warning.assert_called_with(f"Container {mock_container.short_id} not found.")
        # test given container id and container is in not history
        with self.subTest("test_get_working_containers_with_id_not_found"):
            mock_verify_container.return_value = False
            result = get_working_containers(container_id='container1')
            self.assertEqual(len(result), 0)
            mock_logger.error.assert_called_with(f"Container {mock_container.short_id} not found in History.")


    @patch('subprocess.run')
    @patch('idmtools_platform_container.container_operations.docker_operations.user_logger')
    def test_list_running_jobs_success(self, mock_user_logger, mock_run):
        mock_container = MagicMock(spec=Container, short_id="container_id")
        with self.subTest("test_list_running_jobs_success"):
            # Mock subprocess.run to simulate docker command output
            mock_output = "PID  PPID  PGID CMD\n1234 5678 1234 EXPERIMENT:exp_id batch.sh\n2345 6789 2345 SIMULATION:sim_id"
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
            result = list_running_jobs("123")
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], Job)
            self.assertEqual(result[0].item_id, "exp_id")
            self.assertEqual(result[1].item_id, "sim_id")
        with self.subTest("test_list_running_jobs_no_jobs"):
            # Mock subprocess.run to simulate no jobs running
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = list_running_jobs(mock_container.short_id)
            self.assertEqual(len(result), 0)    # No jobs running
        with self.subTest("test_list_running_jobs_failure"):
            # Mock subprocess.run to simulate returncode=1
            mock_run.return_value = MagicMock(returncode=1)
            result = list_running_jobs(mock_container.short_id)
            self.assertEqual(len(result), 0)
        with self.subTest("test_list_running_jobs_failure"):
            # Mock subprocess.run to simulate a failure
            mock_run.return_value = MagicMock(returncode=-1, stderr="Error")
            with self.assertRaises(SystemExit) as ex:
                result = list_running_jobs(mock_container.short_id)
                self.assertEqual(len(result), 0)
                mock_user_logger.error.assert_called_with("Command failed with return code -1")
        with self.subTest("test_list_running_jobs_with_limit"):
            # Mock subprocess.run to simulate docker command output
            mock_output = "PID  PPID  PGID CMD\n1234 5678 1234 EXPERIMENT:exp_id\n2345 6789 2345 SIMULATION:sim_id"
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
            result = list_running_jobs(mock_container.short_id, limit=1) # expected only get exp_id back
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Job)
            self.assertEqual(result[0].item_id, "exp_id")


    @patch('idmtools_platform_container.container_operations.docker_operations.JobHistory.get_job')
    @patch('idmtools_platform_container.container_operations.docker_operations.get_working_containers')
    @patch('idmtools_platform_container.container_operations.docker_operations.list_running_jobs')
    @patch('idmtools_platform_container.container_operations.docker_operations.user_logger')
    def test_find_running_job(self, mock_user_logger, mock_list_running_jobs, mock_get_working_containers,
                                                mock_get_job):
        with self.subTest("test_find_running_job_with_container_id"):
            mock_job = Job(container_id='container1', process_line='1234 5678 1234 EXPERIMENT:exp_id')
            mock_list_running_jobs.return_value = [mock_job]
            result = find_running_job(item_id='exp_id', container_id='container1')
            self.assertIsNotNone(result)
            self.assertEqual(result.item_id, 'exp_id')
        with self.subTest("test_find_running_job_without_container_id"):
            mock_get_job.return_value = {'CONTAINER': 'container1'}
            mock_job = Job(container_id='container1', process_line='1234 5678 1234 EXPERIMENT:exp_id')
            mock_list_running_jobs.return_value = [mock_job]
            result = find_running_job(item_id='exp_id')
            self.assertIsNotNone(result)
            self.assertEqual(result.item_id, 'exp_id')
        with self.subTest("test_find_running_job_with_job_id"):
            mock_container1 = MagicMock(spec=Container, short_id="container_id1")
            mock_job = Job(container_id=mock_container1.short_id, process_line='1234 5678 1234 EXPERIMENT:exp_id')
            mock_job.job_id = "123"

            def side_effect(item_id):
                if not is_valid_uuid(item_id):
                    return None
                else:
                    return dict(JOB_ID='123')
            mock_get_job.side_effect = side_effect
            mock_list_running_jobs.return_value = [mock_job]
            mock_get_working_containers.return_value = [mock_container1]
            result = find_running_job(item_id="123")
            self.assertIsNotNone(result)
            self.assertEqual(result.item_id, 'exp_id')
            self.assertEqual(result.job_id, '123')
        with self.subTest("test_find_running_job_with_job_id_match_multiple_containers"):
            mock_container1 = MagicMock(spec=Container, short_id="container_id1")
            mock_container2 = MagicMock(spec=Container, short_id="container_id2")
            mock_job = Job(container_id=mock_container1.short_id, process_line='1234 5678 1234 EXPERIMENT:exp_id')
            mock_job.job_id = "123"
            def side_effect(item_id):
                if not is_valid_uuid(item_id):
                    return None
                else:
                    return dict(JOB_ID='123')
            mock_get_job.side_effect = side_effect
            mock_list_running_jobs.return_value = [mock_job]
            mock_get_working_containers.return_value = [mock_container1, mock_container2]
            with self.assertRaises(SystemExit) as ex:
                result = find_running_job(item_id="123")
                mock_user_logger.error.assert_called_with(f"Multiple jobs found for Job ID {mock_job.job_id}, please provide the Container ID or use Entity ID instead.")


if __name__ == '__main__':
    unittest.main()
