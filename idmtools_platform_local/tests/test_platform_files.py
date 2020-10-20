import allure
import os
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.python_task import PythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import ensure_local_platform_running
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.docker
@pytest.mark.local_platform_internals
@allure.story("LocalPlatform")
@allure.story("Outputs")
@allure.suite("idmtools_platform_local")
class TestPlatformSimulations(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    @pytest.mark.long
    @ensure_local_platform_running(silent=True, **get_test_local_env_overrides())
    @pytest.mark.serial
    def test_fetch_simulation_files(self):
        platform = Platform('Local', **get_test_local_env_overrides())

        task = PythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "realpath_verify.py"))
        pe = Experiment.from_task(task, name=self.case_name, tags={"string_tag": "test", "number_tag": 123},
                                  gather_common_assets_from_task=True)

        wait_on_experiment_and_check_all_sim_status(self, pe, platform)

        files_to_preview = ['StdOut.txt', 'Assets/realpath_verify.py']
        files = platform.get_files(pe.simulations[0], files_to_preview)
        self.assertEqual(len(files), len(files_to_preview))
        for filename in files_to_preview:
            self.assertIn(filename, files)
            if filename == "StdOut.txt":  # variable output
                self.assertEqual(files[filename].decode('utf-8').strip(), f'/data/{pe.uid}/Assets')
            else:  # default compare the content of the files
                with open(os.path.join(COMMON_INPUT_PATH, "python", "realpath_verify.py"), 'r') as rpin:
                    self.assertEqual(files[filename].decode("utf-8").replace("\r\n", "\n"), rpin.read().replace("\r\n", "\n"))
