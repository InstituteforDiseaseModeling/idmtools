import os
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from idmtools.assets import AssetCollection, Asset
from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import tempfile
import sys

from idmtools_platform_container.container_operations.docker_operations import stop_container

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))
from utils import find_containers_by_prefix, is_valid_container_name_with_prefix, get_container_name_by_id, \
    get_container_status_by_id


class TestPlatformExperiment(unittest.TestCase):
    def test_container_platform_integration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform("Container", job_directory=temp_dir)
            command = "Assets/run.sh"
            task = CommandTask(command=command)
            ac = AssetCollection()
            model_asset = Asset(absolute_path=os.path.join("inputs", "run.sh"))
            ac.add_asset(model_asset)
            # create experiment from task
            experiment = Experiment.from_task(task, name="run_pip_list", assets=ac)
            experiment.run(wait_until_done=True)
            exp_dir = platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
            suite_dir = platform.get_directory_by_id(experiment.parent_id, ItemType.SUITE)
            # Check if the expected files exist under suite dir
            self.assertTrue(os.path.exists(exp_dir))
            expected_files = ["metadata.json"]
            expected_files_in_suite_dir = [os.path.join(suite_dir, filename) for filename in expected_files]
            for file in expected_files_in_suite_dir:
                with self.subTest(file=file):
                    self.assertTrue(Path(file).is_file(), f"The file {file} should exist.")

            # Check if the expected files exist under experiment dir
            expected_files = ("metadata.json", "run_simulation.sh", "batch.sh", "stdout.txt", "stderr.txt")
            expected_files_in_exp_dir = [os.path.join(exp_dir, filename) for filename in expected_files]
            for file in expected_files_in_exp_dir:
                with self.subTest(file=file):
                    self.assertTrue(Path(file).is_file(), f"The file {file} should exist.")
            sim_dir = platform.get_directory_by_id(experiment.simulations[0].id, ItemType.SIMULATION)
            self.assertTrue(Path(f"{sim_dir}").is_dir())
            self.assertTrue(Path(f"{exp_dir}/Assets").is_dir())

            # Check if the expected files exist under simulation dir
            expected_sim_files = ("metadata.json", "_run.sh", "job_status.txt", "stdout.txt", "stderr.txt")
            expected_files_in_sim_dir = [os.path.join(sim_dir, filename) for filename in expected_sim_files]
            for file in expected_files_in_sim_dir:
                with self.subTest(file=file):
                    self.assertTrue(Path(file).is_file(), f"The file {file} should exist.")
            sim_assets_dir = Path(f"{sim_dir}/Assets")
            self.assertTrue(sim_assets_dir.is_dir() and not os.path.islink(sim_assets_dir))
            # Check if the stdout.txt file contains pip list results
            with open(f"{sim_dir}/stdout.txt", "r") as file:
                content = file.read()
                self.assertIn("emod-api", content)
                self.assertIn("Package             Version", content)
            with open(f"{sim_dir}/_run.sh", "r") as file:
                content = file.read()
                # Check if the _run.sh script contains the command "Assets/run.sh"
                self.assertIn("Assets/run.sh", content)

            # clean up
            stop_container(platform.container_id, remove=True)

    def test_container_platform_with_custom_docker_image(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            docker_image = "nginx:latest"
            Platform("Container", job_directory=temp_dir, docker_image=docker_image)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_nginx")
            experiment.run(wait_until_done=True)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            # check container exist
            matched_containers = find_containers_by_prefix("", image_name=docker_image)
            for mc in matched_containers:
                stop_container(mc, remove=True)

    @pytest.mark.serial
    @patch('idmtools_platform_container.container_operations.docker_operations.check_local_image')
    @patch('idmtools_platform_container.container_operations.docker_operations.logger')
    @patch('idmtools_platform_container.container_operations.docker_operations.user_logger')
    def test_platform_with_no_local_image(self, mock_user_logger, mock_logger, mock_check_local_image):
        with tempfile.TemporaryDirectory() as temp_dir:
            # mock that the image does not exist in local, so it should be pulled from artifactory
            mock_check_local_image.return_value = False

            platform = Platform("Container", job_directory=temp_dir, debug=True)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True, platform=platform)

            expected_user_log_messages = [f"Image {platform.docker_image} does not exist, pull the image first.",
                                          f"Pulling image {platform.docker_image} ..."]
            for i, call in enumerate(mock_user_logger.info.call_args_list):
                message = call[0][0]
                self.assertIn(expected_user_log_messages[i], message)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            # clean up
            stop_container(platform.container_id, remove=True)

    def test_platform_with_container_prefix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            container_prefix = "idmtools"
            # check container exist, if does, delete first
            matched_containers = find_containers_by_prefix(container_prefix)
            for mc in matched_containers:
                stop_container(mc, remove=True)

            platform = Platform("Container", job_directory=temp_dir, container_prefix=container_prefix)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True, platform=platform)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            # check container exist
            new_matched_containers = find_containers_by_prefix(container_prefix)
            self.assertEqual(len(new_matched_containers), 1)
            self.assertTrue(is_valid_container_name_with_prefix(new_matched_containers[0], container_prefix))

            # clean up
            for mc in new_matched_containers:
                stop_container(mc, remove=True)

    def test_platform_with_reuse_container_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # first create experiment with new_container=True
            platform1 = Platform("Container", job_directory=temp_dir, new_container=True)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            # reuse the previous container with new_container=False
            platform2 = Platform("Container", job_directory=temp_dir, new_container=False)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True, plaform=platform2)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            # verify that platform1's container and platform2's container are the same
            self.assertEqual(platform1.container_id, platform2.container_id)
            # clean up
            stop_container(platform2.container_id, remove=True)

    def test_platform_with_force_start(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # first create experiment with new_container=True
            platform1 = Platform("Container", job_directory=temp_dir, new_container=True)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            container_name1 = get_container_name_by_id(platform1.container_id)
            # reuse the previous container with force_start=True
            platform2 = Platform("Container", job_directory=temp_dir, force_start=True)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True, platform=platform2)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            self.assertNotEqual(platform1.container_id, platform2.container_id)
            container_name2 = get_container_name_by_id(platform2.container_id)
            self.assertNotEqual(container_name1, container_name2)
            # verify that platform1's container is stopped and removed
            self.assertEqual(get_container_status_by_id(platform1.container_id), None)
            # verify that platform2's container is running
            self.assertEqual(get_container_status_by_id(platform2.container_id), "running")
            # clean up, new container 2 should be deleted
            stop_container(platform2.container_id, remove=True)

    def test_platform_with_symlink_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # first create experiment with sym_link=True
            platform = Platform("Container", job_directory=temp_dir, sym_link=True)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            exp_assets_path = Path(platform.get_directory(experiment), 'Assets')
            sim_assets_path = Path(platform.get_directory(experiment.simulations[0]), 'Assets')
            # Make sure experiment and simulations Assets dirs are not symlink
            self.assertEqual(os.path.islink(exp_assets_path), False)
            self.assertEqual(os.path.islink(sim_assets_path), False)
            # clean up
            stop_container(platform.container_id, remove=True)

    @patch('idmtools_platform_container.container_platform.user_logger')
    def test_platform_with_dryrun_true(self, mock_user_logger):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform("Container", job_directory=temp_dir)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=False, dry_run=True)
            self.assertEqual(experiment.status, EntityStatus.CREATED)
            mock_user_logger.info.assert_called_with(f"\nDry run: True")
            # clean up - dry run should not create container, so nothing to stop and remove
            with self.assertRaises(TypeError) as ex:
                stop_container(platform.container_id, remove=True)
            self.assertEqual(ex.exception.args[0], "Invalid container object.")

    def test_platform_with_retries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            retries = 2
            platform = Platform("Container", job_directory=temp_dir, retries=retries)
            command = "ls -lat"
            task = CommandTask(command=command)
            experiment = Experiment.from_task(task, name="run_command")
            experiment.run(wait_until_done=True)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            with open(os.path.join(temp_dir, experiment.parent_id, experiment.id, experiment.simulations[0].id,
                                   "_run.sh"), "r") as file:
                content = file.read()
                self.assertIn(f'until [ "$n" -ge {retries} ]', content)
            # clean up
            stop_container(platform.container_id, remove=True)

    def test_extra_packages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir, new_container=True, extra_packages=['astor'])
            command = "python Assets/model.py"
            task = CommandTask(command=command)

            model_asset = Asset(absolute_path=os.path.join("inputs", "model.py"))
            common_assets = AssetCollection()
            common_assets.add_asset(model_asset)
            experiment = Experiment.from_task(task, name="run_platform_extra_packages", assets=common_assets)
            experiment.run(wait_until_done=True, platform=platform)
            self.assertEqual(experiment.status, EntityStatus.SUCCEEDED)
            sim_dir = platform.get_directory_by_id(experiment.simulations[0].id, ItemType.SIMULATION)
            self.assertTrue(os.path.exists(Path(f"{sim_dir}/ast_dump.txt")), f"The ast_dump.txt file should exist.")
            # clean up
            stop_container(platform.container_id, remove=True)

    def test_required_extra_packages_not_install(self):
        # test run model file without install required package 'astor'
        with tempfile.TemporaryDirectory() as temp_dir:
            platform = Platform('CONTAINER', job_directory=temp_dir, new_container=True, extra_packages=[])
            command = "python Assets/model.py"
            task = CommandTask(command=command)
            model_asset = Asset(absolute_path=os.path.join("inputs", "model.py"))
            common_assets = AssetCollection()
            common_assets.add_asset(model_asset)
            experiment = Experiment.from_task(task, name="run_platform_extra_packages", assets=common_assets)
            experiment.run(wait_until_done=True, platform=platform)
            self.assertEqual(experiment.status, EntityStatus.FAILED)
            # clean up
            stop_container(platform.container_id, remove=True)

    # def test_delete_container_by_image_prefix(self):
    #     delete_containers_by_image_prefix("docker-production-public.packages.idmod.org/idmtools/container-test")
