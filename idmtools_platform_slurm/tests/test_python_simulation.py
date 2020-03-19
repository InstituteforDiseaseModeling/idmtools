import os
import pytest
from operator import itemgetter
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools.core.platform_factory import Platform
from idmtools.core import ItemType
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform('SLURM')

    @pytest.mark.skip
    def test_direct_sweep_one_parameter_local(self):
        name = self.case_name
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        ts = TemplatedSimulations(base_task=task)

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))

        experiment = Experiment(name=self.case_name, simulations=ts)
        experiment.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        self.platform.run_items()
        self.platform.wait_till_done(experiment)
        # validation
        self.assertEqual(self.case_name, name)
        self.assertEqual(experiment.simulation_count, 5)
        self.assertIsNotNone(experiment.uid)
        comps_exp = self.platform.get_item(item_id=experiment.uid, item_type=ItemType.EXPERIMENT)
        sims = self.platform.get_children_by_object(comps_exp)
        self.assertEqual(len(sims), 5)
        self.assertTrue(experiment.succeeded)

        # validate tags
        tags = []
        for simulation in sims:
            self.assertEqual(simulation.experiment.uid, experiment.uid)
            tags.append(simulation.tags)
        expected_tags = [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)
