import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from subprocess import CalledProcessError
from docker.models.containers import Container
from unittest.mock import patch, MagicMock
import pytest

from idmtools import IdmConfigParser
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_container.container_platform import ContainerPlatform


@pytest.mark.serial
class TestContainerPlatform(unittest.TestCase):
    def setUp(self):
        IdmConfigParser.clear_instance()
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     try:
    #         shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEST"))
    #     except FileNotFoundError:
    #         pass

    @patch('idmtools_platform_container.utils.job_history.JobHistory.save_job')
    @patch('idmtools_platform_container.container_platform.find_running_job', return_value=None)
    @patch.object(ContainerPlatform, 'check_container')
    @patch.object(ContainerPlatform, 'convert_scripts_to_linux')
    @patch.object(ContainerPlatform,'submit_experiment')
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
            mock_logger.debug.call_args_list[1].assert_called_with(f"Submit experiment/simulations to container: 12345")

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
        # mock_docker.assert_called_once()
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

    @patch('idmtools_platform_container.container_platform.user_logger.warning')
    @patch('subprocess.run')  # Mock subprocess.run
    @patch.object(ContainerPlatform, 'get_container_directory')
    @patch.object(ContainerPlatform, '__post_init__', lambda x: None)
    def test_convert_scripts_to_linux(self, mock_get_container_directory, mock_run, mock_logger_warning):
        with self.subTest("test_convert_scripts_to_linux_success"):
            mock_get_container_directory.return_value = "/mocked/directory"
            platform = ContainerPlatform(job_directory="DEST")
            experiment = MagicMock()  # Mock the Experiment object

            platform.convert_scripts_to_linux(experiment)

            # Verify subprocess.run was called correctly
            mock_run.assert_called_once_with(
                ["docker", "exec", platform.container_id, "bash", "-c",
                 "cd /mocked/directory;sed -i 's/\\r//g' batch.sh;sed -i 's/\\r//g' run_simulation.sh"],
                stdout=subprocess.PIPE
            )
        with self.subTest("test_convert_scripts_to_linux_with_exception"):
            mock_run.side_effect = Exception('General exception')
            mock_experiment = MagicMock(spec=Experiment)
            platform = ContainerPlatform(job_directory="DEST")
            platform.convert_scripts_to_linux(mock_experiment)
            mock_logger_warning.assert_called_with("Failed to convert script to Linux: General exception")
            # self.assertTrue('Failed to convert script to Linux: General exception', mock_logger.method_calls[0].args[0])
        with self.subTest("test_convert_scripts_to_linux_with_CalledProcessError"):
            mock_run.side_effect = CalledProcessError(1, 'command')
            mock_experiment = MagicMock(spec=Experiment)
            platform = ContainerPlatform(job_directory="DEST")
            platform.convert_scripts_to_linux(mock_experiment)
            mock_logger_warning.assert_called_with(
                "Failed to convert script: Command 'command' returned non-zero exit status 1.")

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
            exp1 = Experiment(name='Test1')
            suite1= Suite(name='Suite1')
            exp1.parent = suite1
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")
            result = platform.get_container_directory(exp1)
            if sys.platform == "win32":
                expected_result = f"/home/container_data/{suite1.name.lower()}_{suite1.id}/{exp1.name.lower()}_{exp1.id}"
            else:
                expected_result = f"/home/container_data/{suite1.name}_{suite1.id}/{exp1.name}_{exp1.id}"
            self.assertEqual(expected_result, result)

        # test get_container_directory with Suite instance
        with self.subTest("test_suite"):
            suite1= Suite(name='Suite1')
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")
            result = platform.get_container_directory(suite1)
            expected_result = f"/home/container_data/{suite1.name.lower()}_{suite1.id}"
            self.assertEqual(expected_result, result.lower())

        # test get_container_directory with Simulation instance
        with self.subTest("test_simulation"):
            exp1 = Experiment(name='Test1')
            sim1 = Simulation(name='Simulation1')
            sim1.parent = exp1
            suite1 = Suite(name='Suite1')
            exp1.parent = suite1
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")
            result = platform.get_container_directory(sim1)
            expected_result = f"/home/container_data/{suite1.name.lower()}_{suite1.id}/{exp1.name.lower()}_{exp1.id}/{sim1.id}"
            self.assertEqual(expected_result, result.lower())

        # test get_container_directory with Simulation instance
        with self.subTest("test_simulation_with_sim_name"):
            parser = IdmConfigParser()
            config_ini = 'idmtools_container_sim_dir.ini'
            parser._load_config_file(dir_path=os.path.dirname(os.path.realpath(__file__)), file_name=config_ini)
            parser.ensure_init(file_name=config_ini, force=True)
            exp1 = Experiment(name='Test1')
            sim1 = Simulation(name='Simulation1')
            sim1.parent = exp1
            suite1 = Suite(name='Suite1')
            exp1.parent = suite1
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")
            result = platform.get_container_directory(sim1)
            expected_result = f"/home/container_data/{suite1.name.lower()}_{suite1.id}/{exp1.name.lower()}_{exp1.id}/{sim1.name.lower()}_{sim1.id}"
            self.assertEqual(expected_result, result.lower())

        # test get_container_directory with Simulation instance
        with self.subTest("test_exp_without_name"):
            parser = IdmConfigParser()
            config_ini = 'idmtools_container_exp_dir.ini'
            parser._load_config_file(dir_path=os.path.dirname(os.path.realpath(__file__)), file_name=config_ini)
            parser.ensure_init(file_name=config_ini, force=True)
            name_directory = IdmConfigParser.get_option(None, "name_directory")
            exp1 = Experiment(name='Test1')
            sim1 = Simulation(name='Simulation1')
            sim1.parent = exp1
            suite1 = Suite(name='Suite1')
            exp1.parent = suite1
            platform = ContainerPlatform(job_directory="DEST", data_mount="/home/container_data")
            result = platform.get_container_directory(sim1)
            expected_result = f"/home/container_data/{suite1.id}/{exp1.id}/{sim1.id}"
            self.assertEqual(expected_result, result.lower())

    @patch('idmtools_platform_container.container_platform.find_container_by_image')
    @patch.object(ContainerPlatform, 'validate_mount')
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

    @patch('idmtools_platform_container.container_platform.get_container')
    @patch('idmtools_platform_container.container_platform.user_logger')
    @patch('idmtools_platform_container.container_platform.restart_container')
    @patch.object(ContainerPlatform, 'validate_mount')
    def test_validate_container(self, mock_validate_mount, mock_restart_container, mock_logger, mock_get_container):
        with self.subTest("test_valid_container_seccess"):
            # Setup
            mock_container = MagicMock()
            mock_container.status = 'running'
            mock_container.short_id = '12345'
            mock_validate_mount.return_value = True
            mock_get_container.return_value = mock_container
            platform = ContainerPlatform(job_directory="DEST")
            result = platform.validate_container('12345')
            self.assertEqual(result, '12345')
            mock_restart_container.assert_not_called()

        with self.subTest("test_invalid_container"):
            mock_get_container.return_value = None
            platform = ContainerPlatform(job_directory="DEST")
            with self.assertRaises(SystemExit):
                platform.validate_container('12345')
            mock_logger.warning.assert_called_with("Container 12345 is not found.")
        with self.subTest("test_invalid_container_status"):
            mock_container = MagicMock()
            mock_container.status = 'stopped'
            mock_get_container.return_value = mock_container
            platform = ContainerPlatform(job_directory="DEST")
            with self.assertRaises(SystemExit):
                platform.validate_container('54321')
            mock_logger.warning.assert_called_with(
                "Container 54321 is in stopped status, but we only support status: ['exited', 'running', 'paused'].")
        with self.subTest("test_not_include_stopped_container"):
            mock_container = MagicMock()
            mock_container.status = 'exited'
            mock_get_container.return_value = mock_container
            platform = ContainerPlatform(job_directory="DEST", include_stopped=False)
            with self.assertRaises(SystemExit):
                platform.validate_container('123456')
            mock_logger.warning.assert_called_with(
                "Container 123456 is not running.")
        with self.subTest("test_invalid_mount_container"):
            mock_container = MagicMock()
            mock_container.status = 'running'
            mock_container.short_id = '1111'
            mock_validate_mount.return_value = False
            mock_get_container.return_value = mock_container
            platform = ContainerPlatform(job_directory="DEST", include_stopped=False)
            with self.assertRaises(SystemExit):
                platform.validate_container('1111')
            mock_logger.warning.assert_called_with(
                "Container 1111 does not match the platform mounts.")

    @patch('idmtools_platform_container.container_platform.is_docker_installed')
    @patch('idmtools_platform_container.container_platform.is_docker_daemon_running')
    @patch.object(ContainerPlatform, 'validate_container')
    @patch('idmtools_platform_container.container_platform.user_logger')
    def test_container_platform_post_init(self, mock_user_logger, mock_validate_container, mock_docker_daemon_running, mock_docker_installed):
        with self.subTest("test_init_with_docker_installed_and_running"):
            mock_docker_daemon_running.return_value = True
            mock_docker_installed.return_value = True
            platform = ContainerPlatform(job_directory="DEST")
            self.assertIsNotNone(platform)
        with self.subTest("test_init_fails_without_docker_installed"):
            mock_docker_installed.return_value = False
            with self.assertRaises(SystemExit):
                ContainerPlatform(job_directory="DEST")
                mock_user_logger.error.assert_called_with("Docker is not installed.")
        with self.subTest("test_init_fails_with_docker_daemon_not_running"):
            mock_docker_installed.return_value = True
            mock_docker_daemon_running.return_value = False
            with self.assertRaises(SystemExit):
                ContainerPlatform(job_directory="DEST")
                mock_user_logger.error.assert_called_with("Docker daemon is not running.")
        with self.subTest("test_init_with_container_id"):
            mock_docker_daemon_running.return_value = True
            mock_docker_installed.return_value = True
            mock_container = MagicMock(spec=Container)
            mock_container.short_id = '12345'
            mock_container.id = "1234567890"
            mock_validate_container.return_value = mock_container.short_id
            # test with container long id
            platform = ContainerPlatform(job_directory="DEST", container_id=mock_container.id)
            self.assertTrue(platform.container_id, '12345')
            # test with container short id
            platform = ContainerPlatform(job_directory="DEST", container_id=mock_container.short_id)
            self.assertTrue(platform.container_id, '12345')
            # test with assign container to platform
            platform = ContainerPlatform(job_directory="DEST")
            platform.container_id = mock_container.short_id
            self.assertTrue(platform.container_id, '12345')

    @patch('idmtools_platform_container.container_platform.get_container')
    @patch('idmtools_platform_container.container_platform.logger.warning')
    def test_validate_mount(self, mock_logger_warning, mock_get_container):
        with self.subTest("test_container_found_and_mounts_match"):
            mock_container = MagicMock()
            mock_get_container.return_value = mock_container
            platform = ContainerPlatform(job_directory="DEST")
            with patch('idmtools_platform_container.container_platform.compare_mounts', return_value=True):
                result = platform.validate_mount('12345')
                self.assertTrue(result)
                mock_logger_warning.assert_not_called()
        with self.subTest("test_container_not_found"):
            mock_get_container.return_value = None
            platform = ContainerPlatform(job_directory="DEST")
            result = platform.validate_mount('12345')
            self.assertFalse(result)
            mock_logger_warning.assert_called_with("Container 12345 is not found.")
        with self.subTest("test_container_found_but_mounts_do_not_match"):
            mock_container = MagicMock()
            mock_container.attrs = {'Mounts': []}
            mock_get_container.return_value = mock_container
            platform = ContainerPlatform(job_directory="DEST")
            result = platform.validate_mount('12345')
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
