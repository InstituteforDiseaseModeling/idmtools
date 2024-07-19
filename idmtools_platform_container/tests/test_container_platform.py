import os
import shutil
import sys
import tempfile
import unittest
from subprocess import CalledProcessError
from unittest.mock import patch, MagicMock
import pytest
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_container.container_platform import ContainerPlatform


@pytest.mark.serial
class TestContainerPlatform(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        try:
            shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST"))
        except FileNotFoundError:
            pass

    @patch('idmtools_platform_container.utils.job_history.JobHistory.save_job')
    @patch('idmtools_platform_container.container_platform.find_running_job', return_value=None)
    @patch('idmtools_platform_container.container_platform.ContainerPlatform.check_container')
    @patch('idmtools_platform_container.container_platform.ContainerPlatform.convert_scripts_to_linux')
    @patch('idmtools_platform_container.container_platform.ContainerPlatform.submit_experiment')
    @patch('idmtools_platform_container.container_platform.logger')
    @patch('idmtools_platform_container.container_platform.user_logger')
    def test_submit_job(self, mock_user_logger, mock_logger, mock_submit_experiment, mock_convert_scripts_to_linux,
                        mock_check_container, mock_find_running_job, mock_save_job):
        # test submit_job with Experiment instance
        with self.subTest("test_submit_job_by_experiment_instance"):
            mock_check_container.return_value = '12345'  # Mocked container ID
            mock_experiment = MagicMock(spec=Experiment)
            container_platform = ContainerPlatform(job_directory="DEST")
            # call submit_job
            container_platform.submit_job(mock_experiment)
            # assert
            mock_check_container.assert_called_once()
            mock_save_job.assert_called_once_with(container_platform.job_directory, '12345', mock_experiment,
                                                  container_platform)
            mock_submit_experiment.assert_called_once_with(mock_experiment)
            mock_logger.debug.call_args_list[0].assert_called_with(f"Run experiment on container!")
            if sys.platform == "win32":
                mock_convert_scripts_to_linux.assert_called_once_with(mock_experiment)
                mock_logger.debug.call_args_list[1].assert_called_with(f"Script runs on Windows!")
            mock_logger.debug.call_args_list[2].assert_called_with(f"Submit experiment/simulations to container: 12345")

        # test submit_job with Simulation instance
        with self.subTest("test_submit_job_by_simulation_instance"):
            mock_check_container.return_value = '12345'  # Mocked container ID
            mock_simulation = MagicMock(spec=Simulation)
            container_platform = ContainerPlatform(job_directory="DEST")

            with self.assertRaises(NotImplementedError) as ex:
                container_platform.submit_job(mock_simulation)
            self.assertIn("submit_job directly for simulation is not implemented on ContainerPlatform.",
                          ex.exception.args[0])

        # test submit_job with random instance
        with self.subTest("test_submit_job_by_random_instance"):
            mock_check_container.return_value = '12345'  # Mocked container ID
            mock_item = MagicMock()
            container_platform = ContainerPlatform(job_directory="DEST")

            with self.assertRaises(NotImplementedError) as ex:
                container_platform.submit_job(mock_item)
            self.assertIn("Submit job is not implemented for ", ex.exception.args[0])

        # test submit_job with dry_run
        mock_logger.reset_mock()
        with self.subTest("test_submit_job_dry_run"):
            mock_item = MagicMock(spec=Simulation)
            mock_item.id = "test_container_id"
            container_platform = ContainerPlatform(job_directory="DEST")
            container_platform.submit_job(mock_item, dry_run=True)
            mock_user_logger.info.assert_called_with(f"\nDry run: True")

    @patch('docker.from_env')
    def test_start_container(self, mock_docker):
        # Mocking the Docker client and its methods
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.run.return_value = mock_container

        # Creating a ContainerPlatform instance
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = ContainerPlatform(job_directory=temp_dir)

            # Calling the start_container method
            container_id = platform.start_container()

            # Asserting the calls
            mock_docker.assert_called_once()
            mock_client.containers.run.assert_called_once()
            self.assertEqual(container_id, mock_container.short_id)
            expected_data_source_dir = os.path.abspath(temp_dir)
            self.assertEqual(platform.job_directory, expected_data_source_dir)
            self.assertEqual(platform.data_mount, '/home/container_data')
            self.assertEqual(platform.force_start, False)
            self.assertEqual(platform.user_mounts, None)
            self.assertEqual(platform.sym_link, False)

    @patch('docker.from_env')
    def test_start_container_custom_data_mount(self, mock_docker):
        # Mocking the Docker client and its methods
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.run.return_value = mock_container

        # Creating a ContainerPlatform instance
        platform = ContainerPlatform(job_directory="DEST", user_mounts={"src1": "dest1", "src2": "dest2"})

        # Calling the start_container method
        container_id = platform.start_container()

        # Asserting the calls
        mock_docker.assert_called_once()
        mock_client.containers.run.assert_called_once_with(
            platform.docker_image,
            command="bash",
            volumes={
                platform.job_directory: {"bind": platform.data_mount, "mode": "rw"},
                "src1": {"bind": "dest1", "mode": "rw"},
                "src2": {"bind": "dest2", "mode": "rw"}
            },
            stdin_open=True,
            tty=True,
            detach=True,
            name=None
        )
        self.assertEqual(container_id, mock_container.short_id)

    @patch('subprocess.run')
    def test_convert_scripts_to_linux(self, mock_subprocess_run):
        with self.subTest("test_convert_scripts_to_linux"):
            mock_experiment = MagicMock(spec=Experiment)
            platform = ContainerPlatform(job_directory="DEST")
            mock_subprocess_run.return_value = MagicMock()

            platform.convert_scripts_to_linux(mock_experiment)

            mock_subprocess_run.assert_called_once()
        with self.subTest("test_convert_scripts_to_linux_with_exception"):
            mock_subprocess_run.side_effect = Exception('General exception')
            mock_experiment = MagicMock(spec=Experiment)
            platform = ContainerPlatform(job_directory="DEST")

            with self.assertLogs('user', level='WARNING') as cm:
                platform.convert_scripts_to_linux(mock_experiment)
                self.assertIn('Failed to convert script to Linux:', cm.output[0])
        with self.subTest("test_convert_scripts_to_linux_with_CalledProcessError"):
            mock_subprocess_run.side_effect = CalledProcessError(1, 'command')
            mock_experiment = MagicMock(spec=Experiment)
            platform = ContainerPlatform(job_directory="DEST")

            with self.assertLogs('user', level='WARNING') as cm:
                platform.convert_scripts_to_linux(mock_experiment)
                self.assertIn('Failed to convert script:', cm.output[0])

    def test_get_mounts(self):
        container_platform = ContainerPlatform(job_directory="DEST", user_mounts={"src1": "dest1", "src2": "dest2"})
        result = container_platform.get_mounts()
        job_dir_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        expected_result = [
            {'Type': 'bind', 'Source': job_dir_abs, 'Destination': '/home/container_data', 'Mode': 'rw'},
            {'Type': 'bind', 'Source': 'src1', 'Destination': 'dest1', 'Mode': 'rw'},
            {'Type': 'bind', 'Source': 'src2', 'Destination': 'dest2', 'Mode': 'rw'}
        ]
        self.assertEqual(result, expected_result)

    def test_build_binding_volumes(self):
        container_platform = ContainerPlatform(job_directory="DEST", user_mounts={"src1": "dest1", "src2": "dest2"})
        result = container_platform.build_binding_volumes()
        job_dir_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST")
        expected_result = {
            job_dir_abs: {'bind': '/home/container_data', 'mode': 'rw'},
            'src1': {'bind': 'dest1', 'mode': 'rw'},
            'src2': {'bind': 'dest2', 'mode': 'rw'}
        }
        self.assertEqual(result, expected_result)

    def test_get_container_directory(self):
        # test get_container_directory with Experiment instance
        with self.subTest("test_experiment"):
            mock_experiment = MagicMock(spec=Experiment)
            mock_experiment.id = "experiment_id"
            mock_experiment.parent_id = "suite_id"
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")

            result = platform.get_container_directory(mock_experiment)
            expected_result = "/home/container_data/suite_id/experiment_id"
            self.assertEqual(result, expected_result)

        # test get_container_directory with Suite instance
        with self.subTest("test_suite"):
            mock_suite = MagicMock(spec=Suite)
            mock_suite.id = "suite_id"
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")

            result = platform.get_container_directory(mock_suite)
            expected_result = "/home/container_data/suite_id"
            self.assertEqual(result, expected_result)

        # test get_container_directory with Simulation instance
        with self.subTest("test_simulation"):
            mock_simulation = MagicMock(spec=Simulation)
            mock_simulation.id = "simulation_id"
            mock_experiment = MagicMock(spec=Experiment)
            mock_experiment.id = "experiment_id"
            mock_experiment.parent_id = "suite_id"
            mock_simulation.parent = mock_experiment
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")

            result = platform.get_container_directory(mock_simulation)
            expected_result = "/home/container_data/suite_id/experiment_id/simulation_id"
            self.assertEqual(result, expected_result)

    @patch('idmtools_platform_container.container_platform.find_container_by_image')
    @patch('idmtools_platform_container.container_platform.ContainerPlatform.validate_mount')
    @patch('idmtools_platform_container.container_platform.logger')
    def test_retrieve_match_containers(self, mock_logger, mock_validate_mount, mock_find_container_by_image):
        with self.subTest("test_with_matched_containers"):
            platform = ContainerPlatform(job_directory="DEST", docker_image="test_image")
            mock_find_container_by_image.return_value = {"running": ["container1", "container2"]}
            mock_validate_mount.return_value = True

            result = platform.retrieve_match_containers()

            expected_result = [("running", "container1"), ("running", "container2")]
            self.assertEqual(result, expected_result)

        # test with include stopped containers
        with self.subTest("test_with_stopped_matched_containers"):
            platform = ContainerPlatform(job_directory="DEST", docker_image="test_image", include_stopped=True)
            mock_find_container_by_image.return_value = {"running": ["container1", "container2"],
                                                         "stopped": ["container3"]}
            mock_validate_mount.return_value = True

            result = platform.retrieve_match_containers()

            expected_result = [("running", "container1"), ("running", "container2"), ("stopped", "container3")]
            self.assertEqual(result, expected_result)

        # test with no validated mounts
        with self.subTest("test_with_invalid_mounts"):
            platform = ContainerPlatform(job_directory="DEST", docker_image="test_image")
            mock_find_container_by_image.return_value = {'running': ["container"]}
            mock_validate_mount.return_value = False

            result = platform.retrieve_match_containers()
            self.assertEqual(result, [])
            mock_logger.debug.assert_called_with(
                'Found container with image test_image, but no one match platform mounts.')

        # test with empty matched containers
        with self.subTest("test_with_empty_containers"):
            platform = ContainerPlatform(job_directory="DEST", docker_image="test_image")
            mock_find_container_by_image.return_value = {}
            mock_validate_mount.return_value = True

            result = platform.retrieve_match_containers()
            self.assertEqual(result, [])
            mock_logger.debug.assert_called_with(
                'Not found container matching image test_image.')


if __name__ == '__main__':
    unittest.main()
