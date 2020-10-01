import os
import sys
from unittest import TestCase
import pytest

from idmtools.assets import Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_models.templated_script_task import TemplatedScriptTask, \
    get_script_wrapper_windows_task, ScriptWrapperTask, get_script_wrapper_unix_task, LINUX_PYTHON_PATH_WRAPPER, WINDOWS_PYTHON_PATH_WRAPPER
from idmtools_test.utils.decorators import windows_only, linux_only


@pytest.mark.tasks
@pytest.mark.smoke
class TestTemplatedScriptTask(TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def get_simplate_template(self):
        """"""
        simple_template = """
    ECHO OFF
    ECHO Hello World, from {{ vars.name }}
    ECHO %PWD%
    ECHO Created from {{ env.PATH }}
    PAUSE
            """
        return simple_template

    def test_simple_template_assets(self):
        """
        Test simple template bat script using the TemplatedScriptTask
        Returns:

        """
        simple_template = self.get_simplate_template()
        for is_common in [False, True]:
            task = TemplatedScriptTask(
                script_path="example.bat",
                template=simple_template,
                variables=dict(name="Testing"),
                template_is_common=is_common
            )
            task.gather_common_assets()
            task.gather_transient_assets()
            task.pre_creation(None)

            self.assertEqual(1 if is_common else 0, task.common_assets.count)
            self.assertEqual(0 if is_common else 1, task.transient_assets.count)
            if is_common:
                asset = task.common_assets.assets[0]
            else:
                asset = task.transient_assets.assets[0]
            self.assertIn(os.environ['PATH'], asset.content)
            self.assertIn('Hello World, from Testing', asset.content)
            self.assertEqual("example.bat", asset.filename)
            if is_common:
                self.assertEqual("Assets/example.bat", str(task.command))
            else:
                self.assertEqual("example.bat", str(task.command))

    def test_wrapper_script(self):
        """
        Do a basic set of tests on inputs/outputs of the wrapper script
        Returns:

        """
        cmd = 'python -c "import os; print(os.environ)"'
        task = CommandTask(cmd)
        template = """
        set PYTHONPATH=%CWD%\\Assets\\l
        %*
        """

        wrapper_task = get_script_wrapper_windows_task(task, template_content=template)
        wrapper_task.gather_common_assets()
        wrapper_task.gather_transient_assets()
        wrapper_task.pre_creation(None)

        self.assertEqual(1, wrapper_task.common_assets.count)
        self.assertEqual(0, wrapper_task.transient_assets.count)
        asset = wrapper_task.common_assets.assets[0]
        self.assertEqual("wrapper.bat", asset.filename)

        self.assertTrue(str(wrapper_task.command).startswith("Assets\\wrapper.bat"))
        self.assertTrue(str(wrapper_task.command).endswith(cmd))

    @windows_only
    @pytest.mark.timeout(20)
    @pytest.mark.serial
    def test_wrapper_script_execute(self):
        """
        This tests The ScriptWrapperScriptTask as well as the TemplatedScriptTask

        In addition, it tests reload
        Returns:

        """
        cmd = f"\"{sys.executable}\" -c \"import os; print(os.environ)\""
        task = CommandTask(cmd)
        template = """
set PYTHONPATH=%cd%\\Assets\\;%PYTHONPATH%
echo Hello
%*
"""

        with Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute')):
            wrapper_task = get_script_wrapper_windows_task(task, template_content=template)
            experiment = Experiment.from_task(wrapper_task, name=self.case_name)
            experiment.run(wait_until_done=True)
            self.assertTrue(experiment.succeeded)

            for sim in experiment.simulations:
                assets = sim.list_static_assets()
                for asset in assets:
                    if asset.filename in ["StdOut.txt"]:
                        content = asset.content.decode('utf-8').replace("\\\\", "\\")
                        # check for echo
                        self.assertIn('Hello', content)
                        # check for python path
                        self.assertIn(f'{os.getcwd()}\\Assets\\;', content)

            with self.subTest("test_wrapper_script_execute_wrapper_reload"):
                experiment_reload = Experiment.from_id(experiment.uid, load_task=True)
                self.assertEqual(experiment.id, experiment_reload.uid)
                self.assertEqual(1, experiment_reload.simulation_count)
                self.assertEqual(experiment.simulations[0].id, experiment_reload.simulations[0].id)
                task: CommandTask = experiment_reload.simulations[0].task
                self.assertIsInstance(task, ScriptWrapperTask)
                self.assertIsInstance(task.task, CommandTask)
                self.assertEqual(1, experiment.assets.count)
                self.assertIn("wrapper.bat", str(task.command))

    @linux_only
    @pytest.mark.timeout(20)
    @pytest.mark.serial
    def test_wrapper_script_execute_linux(self):
        """
        This tests The ScriptWrapperScriptTask as well as the TemplatedScriptTask

        In addition, it tests reload
        Returns:

        """
        cmd = f"\"{sys.executable}\" -c \"import os; print(os.environ)\""
        task = CommandTask(cmd)

        with Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute')):
            wrapper_task = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
            experiment = Experiment.from_task(wrapper_task, name=self.case_name)
            experiment.run(wait_until_done=True)
            self.assertTrue(experiment.succeeded)

            for sim in experiment.simulations:
                assets = sim.list_static_assets()
                for asset in assets:
                    if asset.filename in ["StdOut.txt"]:
                        content = asset.content.decode('utf-8').replace("\\\\", "\\")
                        # check for echo
                        self.assertIn('Running', content)
                        # check for python path
                        self.assertIn(f'{os.path.join(os.getcwd(), ".test_platform", experiment.id, sim.id)}/Assets', content)

            with self.subTest("test_wrapper_script_execute_wrapper_reload"):
                experiment_reload = Experiment.from_id(experiment.uid, load_task=True)
                self.assertEqual(experiment.id, experiment_reload.uid)
                self.assertEqual(1, experiment_reload.simulation_count)
                self.assertEqual(experiment.simulations[0].id, experiment_reload.simulations[0].id)
                task: CommandTask = experiment_reload.simulations[0].task
                self.assertIsInstance(task, ScriptWrapperTask)
                self.assertIsInstance(task.task, CommandTask)
                self.assertEqual(1, experiment.assets.count)
                self.assertIn("wrapper.sh", str(task.command))

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
        pl_slurm = Platform("SLURM")
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = pl_slurm._simulations.all_files(sim)
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
        pl_slurm = Platform("SLURM")
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = pl_slurm._simulations.all_files(sim)
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
        pl_slurm = Platform("SLURM")
        wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
        wrapper_task.script_binary = "/bin/bash"
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = pl_slurm._simulations.all_files(sim)
            for asset in assets:
                content = asset.content.decode('utf-8').replace("\\\\", "\\")
                if asset.filename in ["stdout.txt"]:
                    # check for echo
                    self.assertIn('Running', content)
                    # don't check full version in case comps updates system
                    self.assertIn('123', content)

    @pytest.mark.comps
    def test_wrapper_script_python_execute_assets_windows_comps(self):
        """
        This tests The ScriptWrapperScriptTask as well as the TemplatedScriptTask

        In addition, it tests reload
        Returns:

        """
        cmd = "python -c \"import test_package as tp;print(tp.a)\""
        task = CommandTask(cmd)
        task.common_assets.add_asset(Asset(filename="test_package.py", content="a=\'123\'"))
        pl_slurm = Platform("COMPS2")
        wrapper_task: TemplatedScriptTask = get_script_wrapper_windows_task(task, template_content=WINDOWS_PYTHON_PATH_WRAPPER)
        experiment = Experiment.from_task(wrapper_task, name=self.case_name)
        experiment.run(wait_until_done=True)
        self.assertTrue(experiment.succeeded)

        for sim in experiment.simulations:
            assets = pl_slurm._simulations.all_files(sim)
            for asset in assets:
                content = asset.content.decode('utf-8').replace("\\\\", "\\")
                if asset.filename in ["stdout.txt"]:
                    # check for echo
                    self.assertIn('Running', content)
                    # don't check full version in case comps updates system
                    self.assertIn('123', content)

