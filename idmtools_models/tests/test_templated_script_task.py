import os
import sys
from unittest import TestCase
import pytest

from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_models.templated_script_task import TemplatedScriptTask, ScriptWrapperTask, \
    get_script_wrapper_windows_task
from idmtools_test.utils.decorators import windows_only


@pytest.mark.tasks
class TestTemplatedScriptTask(TestCase):
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

    @pytest.mark.smoke
    def test_simple_template_assets(self):
        simple_template = self.get_simplate_template()
        for is_common in [False, True]:
            task = TemplatedScriptTask(
                script_name="example.bat",
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

    @pytest.mark.smoke
    def test_wrapper_script(self):
        cmd = 'python -c "import os; print(os.environ)"'
        task = CommandTask(cmd)
        template = """
        PYTHONPATH=%CWD%\\Assets\\l
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

    @pytest.mark.smoke
    @windows_only
    def test_wrapper_script_execute(self):
        cmd = f"\"{sys.executable}\" -c \"import os; print(os.environ)\""
        task = CommandTask(cmd)
        template = """
                set PYTHONPATH=%cd%\\Assets\\;%PYTHONPATH%
                echo Hello
                %*
                """

        with Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute')):
            wrapper_task = get_script_wrapper_windows_task(task, template_content=template)
            experiment = Experiment.from_task(wrapper_task)
            experiment.run(wait_until_done=True)
            self.assertTrue(experiment.succeeded)

            for sim in experiment.simulations:
                assets = sim.list_static_assets()
                for asset in assets:
                    if asset.filename in ["StdOut.txt"]:
                        self.assertIn(f'{os.getcwd()}\\Assets\\;', asset.content.decode('utf-8').replace("\\\\", "\\"))


    def test_wrapper_script_reload(self):
        self.assertTrue(False)

