import allure
import os
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_models.templated_script_task import get_script_wrapper_windows_task
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@pytest.mark.comps
@pytest.mark.wrapper
@pytest.mark.smoke
@allure.story("COMPS")
@allure.story("Templated Script")
@allure.suite("idmtools_platform_comps")
class TestWrapperTask(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.platform = Platform('COMPS2')

    def test_wrapper_task(self):
        # Define out command
        cmd = 'python -c "import os; print(os.environ)"'
        task = CommandTask(cmd)

        # Define out template for out bat file
        template = """
        set PYTHONPATH=%CWD%\\Assets\\l
        echo Running %*
        %*
        """

        # wrap the script
        wrapper_task = get_script_wrapper_windows_task(task, template_content=template)
        experiment = Experiment.from_task(wrapper_task, self.case_name)
        experiment.run(platform=self.platform, wait_until_done=True)

        self.assertTrue(experiment.succeeded)


