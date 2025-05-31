import os
import unittest
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import FileSimulation


class TestFlattenItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        case_name = os.path.basename(__file__) + "--" + cls.__name__
        job_directory = "DEST"
        cls.platform = Platform("Container", job_directory=job_directory)

        builder = SimulationBuilder()
        # Sweep parameter "a"
        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(5))

        task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        task.python_path = "python3"
        tags = {"string_tag": "test", "number_tag": 123}
        ts = TemplatedSimulations(base_task=task)
        ts.add_builder(builder)
        experiment = Experiment.from_template(ts, name=case_name, tags=tags)
        experiment.assets.add_directory(assets_directory=os.path.join("inputs", "Assets"))
        experiment.run(True, platform=cls.platform)
        cls.exp_id = experiment.uid
        cls.experiment = experiment

    def test_flatten_item_suite_true_true(self):
        suite_id = self.experiment.suite.id
        exp = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_suite_true_false(self):
        suite_id = self.experiment.suite.id
        exp = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_suite_false_false(self):
        suite_id = self.experiment.suite.id
        exp = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_suite_false_true(self):
        suite_id = self.experiment.suite.id
        exp = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, FileSimulation) for item in sims))

    def test_flatten_item_exp_true_true(self):
        exp = self.experiment.get_platform_object()
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_exp_true_false(self):
        exp = self.experiment.get_platform_object()
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, FileSimulation) for item in sims))

    def test_flatten_item_exp_false_false(self):
        exp = self.platform.get_item(self.exp_id, ItemType.EXPERIMENT, raw=False)
        sims = self.platform.flatten_item(exp, raw=False)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_exp_false_true(self):
        exp = self.platform.get_item(self.exp_id, ItemType.EXPERIMENT, raw=False)
        sims = self.platform.flatten_item(exp, raw=True)
        self.assertEqual(len(sims), 15)
        self.assertTrue(all(isinstance(item, FileSimulation) for item in sims))

    def test_flatten_item_sim_true_true(self):
        sim = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=True)
        sims = self.platform.flatten_item(sim, raw=True)
        self.assertTrue(len(sims), 1)
        self.assertTrue(all(isinstance(item, FileSimulation) for item in sims))

    def test_flatten_item_sim_true_false(self):
        sim = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=True)
        sims = self.platform.flatten_item(sim, raw=False)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_sim_false_false(self):
        sim = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=False)
        sims = self.platform.flatten_item(sim, raw=False)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, Simulation) for item in sims))

    def test_flatten_item_sim_false_true(self):
        sim = self.platform.get_item(self.experiment.simulations[0].id, item_type=ItemType.SIMULATION, raw=False)
        sims = self.platform.flatten_item(sim, raw=True)
        self.assertEqual(len(sims), 1)
        self.assertTrue(all(isinstance(item, FileSimulation) for item in sims))


