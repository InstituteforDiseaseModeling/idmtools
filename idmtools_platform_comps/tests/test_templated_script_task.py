import allure
import os
from unittest import TestCase
import pytest
from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_models.templated_script_task import TemplatedScriptTask, \
    get_script_wrapper_unix_task, LINUX_PYTHON_PATH_WRAPPER
from idmtools_test.utils.utils import get_case_name


@pytest.mark.tasks
@pytest.mark.smoke
@allure.story("Templated Script")
@allure.suite("idmtools_models")
class TestTemplatedScriptTask(TestCase):

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.platform = Platform('SlurmStage')

    @pytest.mark.comps
    @pytest.mark.timeout(60)
    def test_wrapper_script_execute_comps(self):
        """
        This tests The ScriptWrapperScriptTask as well as the TemplatedScriptTask

        In addition, it tests reload
        Returns:

        """
        cmd = "python3.6 --version"
        task = CommandTask(cmd)
        task.common_assets.add_asset(
            Asset(relative_path=os.path.join("site-packages", "test-package"), filename="__init__.py", content="a=\'123\'"))
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                content = asset.content.decode('utf-8').replace("\\\\", "\\")
                if asset.filename in ["stdout.txt"]:
                    # check for echo
                    self.assertIn('Running', content)
                    # don't check full version in case comps updates system
                    self.assertIn('Python 3.6', content)

    @pytest.mark.comps
    def test_wrapper_script_python_execute_site_packages_comps(self):
        """
        This tests The ScriptWrapperScriptTask as well as the TemplatedScriptTask

        In addition, it tests reload
        Returns:

        """
        cmd = "python3.6 -c \"import test_package as tp;print(tp.a)\""
        task = CommandTask(cmd)
        task.common_assets.add_asset(Asset(relative_path=os.path.join("site-packages", "test_package"), filename="__init__.py", content="a=\'123\'"))
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                content = asset.content.decode('utf-8').replace("\\\\", "\\")
                if asset.filename in ["stdout.txt"]:
                    # check for echo
                    self.assertIn('Running', content)
                    # don't check full version in case comps updates system
                    self.assertIn('123', content)

    @pytest.mark.comps
    def test_wrapper_script_python_execute_assets_comps(self):
        """
        This tests The ScriptWrapperScriptTask as well as the TemplatedScriptTask

        In addition, it tests reload
        Returns:

        """
        cmd = "python3.6 -c \"import test_package as tp;print(tp.a)\""
        task = CommandTask(cmd)
        task.common_assets.add_asset(Asset(filename="test_package.py", content="a=\'123\'"))
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = self.platform._simulations.all_files(sim)
            for asset in assets:
                content = asset.content.decode('utf-8').replace("\\\\", "\\")
                if asset.filename in ["stdout.txt"]:
                    # check for echo
                    self.assertIn('Running', content)
                    # don't check full version in case comps updates system
                    self.assertIn('123', content)



