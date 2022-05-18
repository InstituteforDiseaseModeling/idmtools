import os

import pytest

from idmtools.core import EntityStatus
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform('SLURM_LOCAL')

    def test_direct_sweep_one_parameter_local(self):
        sp = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        experiment = Experiment.from_task(name=self.case_name, task=JSONConfiguredPythonTask(script_path=sp))
        experiment.tags = {"idmtools": "slurm_platform_test"}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = SimulationBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        experiment.builder = builder
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        self.platform.create_items([suite])
        # add experiment to suite
        suite.add_experiment(experiment)
        experiment.run(wait_till_done=True)
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in experiment.simulations]))
        # validation
        self.assertEqual(experiment.simulation_count, 5)
        self.assertIsNotNone(experiment.uid)
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in experiment.simulations]))
        self.assertTrue(experiment.succeeded)
