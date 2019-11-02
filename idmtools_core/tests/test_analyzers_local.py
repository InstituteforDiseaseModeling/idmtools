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


@pytest.mark.analysis
@pytest.mark.docker
class TestAnalyzeManager(ITestWithPersistence):

    @classmethod
    def setUpClass(cls) -> None:
        cls.platform = Platform('Local')
        # cleanup first
        cls.platform._docker_operations.cleanup(True, tear_down_broker=True)
        cls.platform.setup_broker()
        cls.platform._docker_operations.create_services()

        pe = PythonExperiment(name=os.path.basename(__file__) + "--"  + cls.__name__,
                              model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=cls.platform)
        em.run()
        print('Waiting on experiment to finish')
        em.wait_till_done()
        print('experiment done')

        cls.exp_id = pe.uid
        
    @classmethod
    def tearDownClass(cls) -> None:
        cls.platform._docker_operations.cleanup()

    @pytest.mark.timeout(60)
    def test_AddAnalyzer(self):
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        analyzers = [AddAnalyzer()]

        am = AnalyzeManager(configuration={}, platform=self.platform,
                            ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()
        print(analyzers[0].results)
        self.assertEqual(analyzers[0].results, sum(n + 100 for n in range(0, 5)))
