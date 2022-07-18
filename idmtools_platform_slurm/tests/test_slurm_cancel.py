import os
import time
import unittest
from functools import partial
from typing import Any, Dict

import pytest

from idmtools.core import EntityStatus
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.serial
class TestSlurmCanceling(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform('SLURM_LOCAL')
        self.model_script = os.path.join(COMMON_INPUT_PATH, "python", "waiter.py")

        self.experiment = Experiment.from_task(name=self.case_name,
                                               task=JSONConfiguredPythonTask(script_path=self.model_script))
        self.experiment.tags = {"idmtools": "slurm_platform_test"}

        # def param_a_update(simulation: Simulation, value: dict):
        #     simulation.set_parameter("a", value)
        #     return {"a": value}

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder = SimulationBuilder()
        builder.add_sweep_definition(partial(param_update, param="a"), range(5))

        # Sweep parameter "a"
        # builder.add_sweep_definition(param_a_update, range(0, 5))
        self.experiment.builder = builder
        self.suite = Suite(name='Idm Suite')
        self.suite.update_tags({'name': 'testing_suite', 'idmtools': '123'})
        self.platform.create_items([self.suite])
        # add experiment to suite
        self.suite.add_experiment(self.experiment)

    def test_canceling_a_full_experiment(self):
        print('RUNNING TEST')
        self.experiment.run(wait_till_done=False)  # why does this not work? TODO, and why are there two ways to run?
        self.platform.run_items(items=[self.experiment])
        time.sleep(10)  # simulations should now exist in slurm

        self.assertIsNotNone(self.experiment.slurm_job_id)
        self.platform.cancel_items(items=[self.experiment])

        self.assertEqual(self.experiment.status, EntityStatus.FAILED)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in self.experiment.simulations]))

        # validation
        self.assertEqual(self.experiment.simulation_count, 5)
        self.assertIsNotNone(self.experiment.uid)
        self.assertTrue(self.experiment.failed)

    def test_canceling_a_single_simulation(self):
        pass

    def test_canceling_a_full_suite(self):
        pass

if __name__ == '__main__':
    unittest.main()

