import os
from importlib import reload

from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.confg_local_runner_test import reset_local_broker
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_platform_local.docker.docker_operations import DockerOperations

current_directory = os.path.dirname(os.path.realpath(__file__))


class AddAnalyzer(IAnalyzer):
    """
    Add Analyzer
    A simple base class to add analyzers.

    """

    def __init__(self):
        super().__init__(filenames=["output\\result.json"], parse=True)

    def map(self, data, item):
        number = data[self.filenames[0]]["a"]
        result = number + 100
        return result

    def reduce(self, data):
        value = sum(data.values())
        return value


class TestAnalyzeManager(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)
        reset_local_broker()
        from idmtools_platform_local.workers.brokers import setup_broker
        setup_broker()
        # ensure we start from no environment
        dm = DockerOperations()
        dm.cleanup(True)

        import idmtools_platform_local.tasks.create_experiment
        import idmtools_platform_local.tasks.create_simulation
        reload(idmtools_platform_local.tasks.create_experiment)
        reload(idmtools_platform_local.tasks.create_simulation)

        platform = Platform('Local')

        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()

        self.exp_id = pe.uid

    def test_AddAnalyzer(self):
        analyzers = [AddAnalyzer()]
        platform = Platform('Local')

        am = AnalyzeManager(configuration={}, platform=platform, ids=[(self.exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        am.analyze()
        self.assertEqual(analyzers[0].results, sum(n + 100 for n in range(0, 5)))
