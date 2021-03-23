import allure
import os
import time
from functools import partial

import pytest

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.common_experiments import wait_on_experiment_and_check_all_sim_status
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import ensure_local_platform_running
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))
param_a = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")


class AddAnalyzer(IAnalyzer):
    """
    Add Analyzer
    A simple base class to add analyzers.

    """

    def __init__(self):
        super().__init__(filenames=["output\\result.json"], parse=True)

    def map(self, data, item):
        print(f"Data: {str(data[self.filenames[0]])}")
        number = data[self.filenames[0]]["a"]
        print(f"Number: {number}")
        result = number + 100
        print(f"Result: {result}")
        return result

    def reduce(self, data):
        print(f'Sum: {str(data.values())}')
        value = sum(data.values())
        return value


@pytest.mark.analysis
@pytest.mark.docker
@pytest.mark.serial
@allure.story("LocalPlatform")
@allure.story("Analyzers")
@allure.suite("idmtools_platform_local")
class TestAnalyzersLocal(ITestWithPersistence):

    @classmethod
    def setUpClass(cls) -> None:
        cls.platform = Platform('Local', **get_test_local_env_overrides())

        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a, range(0, 5))
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        tags = {"string_tag": "test", "number_tag": 123}
        ts = TemplatedSimulations(base_task=task)
        ts.add_builder(builder)
        e = Experiment.from_template(ts, name=os.path.basename(__file__) + "--" + cls.__name__, tags=tags)

        wait_on_experiment_and_check_all_sim_status(cls, e, cls.platform)
        time.sleep(2)
        print('experiment done')

        cls.exp_id = e.uid

    @pytest.mark.timeout(180)
    @pytest.mark.long
    def test_AddAnalyzer(self):
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        analyzers = [AddAnalyzer()]

        am = AnalyzeManager(configuration={}, platform=self.platform,
                            ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()
        print(analyzers[0].results)
        self.assertEqual(analyzers[0].results, sum(n + 100 for n in range(0, 5)))
