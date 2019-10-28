import os
import time
import pytest
from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))


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


class TestAnalyzeManager(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        from idmtools_platform_local.docker.docker_operations import DockerOperations
        do = DockerOperations()
        do.cleanup()
        self.platform = Platform('Local')

        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=self.platform)
        em.run()
        em.wait_till_done()
        # TODO fix timing on local platform
        time.sleep(4)

        self.exp_id = pe.uid

    @pytest.mark.docker
    def test_AddAnalyzer(self):
        analyzers = [AddAnalyzer()]

        am = AnalyzeManager(configuration={}, platform=self.platform,
                            ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()
        print(analyzers[0].results)
        self.assertEqual(analyzers[0].results, sum(n + 100 for n in range(0, 5)))
