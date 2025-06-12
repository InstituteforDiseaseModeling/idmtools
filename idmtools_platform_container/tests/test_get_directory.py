import allure
import os
import unittest
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import FileSimulation, FileSuite
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@allure.story("Python")
@allure.suite("idmtools_platform_container")
class TestGetDirectory(ITestWithPersistence):

    def _run_create_test_experiments(self):
        """
        create suite and experiment with 5 simulations. 2 succeed ones and 3 failed ones
        :return: ExperimentManager
        """
        def param_update(simulation, param, value):
            return simulation.task.set_parameter(param, value)
        setA = partial(param_update, param="Run_Number")

        task = JSONConfiguredPythonTask(
            script_path=os.path.join(COMMON_INPUT_PATH, "python_experiments", "model.py"))
        ts = TemplatedSimulations(base_task=task)
        # We can define common metadata like tags across all the simulations using the base_simulation object
        ts.base_simulation.tags['tag1'] = 1

        # Since we have our templated simulation object now, let's define our sweeps
        # To do that we need to use a builder
        builder = SimulationBuilder()
        builder.add_sweep_definition(setA, range(5))
        ts.add_builder(builder)
        experiment = Experiment(name="test_filter_simulations.py--test_experiment", simulations=ts)
        suite = Suite(name='test_filter_simulations.py--test suite')
        suite.update_tags({'name': 'test', 'fetch': 123})
        self.platform.create_items([suite])
        suite.add_experiment(experiment)
        experiment.run(wait_until_done=True)
        # suite_id = 'd35b322e-4238-f011-930f-f0921c167860'
        # suite = self.platform.get_item(suite_id, item_type=ItemType.SUITE)
        return suite

    @classmethod
    def setUpClass(cls):
        cls.platform = Platform('Container', job_directory="DEST")
        cls.suite = cls._run_create_test_experiments(cls)
        cls.experiment = cls.suite.experiments[0]

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)

    def test_get_directory_with_suite(self):
        suite: Suite = self.experiment.parent
        file_suite: FileSuite = suite.get_platform_object()
        # verify get_directory for server suite (file_suite)
        self.assertEqual(self.platform.get_directory(file_suite), file_suite.get_directory())
        # verify get_directory for local suite (idmtools suite)
        self.assertEqual(self.platform.get_directory(suite), suite.get_directory())

        self.assertEqual(self.platform.get_directory(suite), self.platform.get_directory(file_suite))

    def test_get_directory_with_exp(self):
        file_experiment = self.platform.get_item(self.experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        # verify get_directory for server experiment (file_experiment)
        self.assertEqual(self.platform.get_directory(file_experiment), file_experiment.get_directory())
        # verify get_directory for local experiment (idmtools experiment)
        self.assertEqual(self.platform.get_directory(self.experiment), self.experiment.get_directory())
        self.assertEqual(self.platform.get_directory(self.experiment), self.platform.get_directory(file_experiment))

    def test_get_directory_with_sim(self):
        file_sim: FileSimulation = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=True)
        # verify get_directory for server sim (file_sim)
        self.assertEqual(file_sim.get_directory(), self.platform.get_directory(file_sim))
        idmtools_sim: FileSimulation = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION)
        # verify get_directory for local sim (idmtools sim)
        self.assertEqual(idmtools_sim.get_directory(), self.platform.get_directory(idmtools_sim))
        self.assertEqual(self.platform.get_directory(file_sim), self.platform.get_directory(idmtools_sim))


if __name__ == '__main__':
    unittest.main()
