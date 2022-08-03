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
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH


@pytest.mark.serial
class TestSlurmCanceling(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.platform = Platform('SLURM_LOCAL')
        self.model_script = os.path.join(COMMON_INPUT_PATH, "python", "waiter.py")

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        # generate experiment & containing suite of 5 simulations that will wait for cancelation
        task = JSONConfiguredPythonTask(script_path=self.model_script)
        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()
        builder.add_sweep_definition(partial(param_update, param="a"), range(5))
        ts.add_builder(builder)
        self.experiment = Experiment.from_template(ts, name=self.case_name)
        self.experiment.tags = {"idmtools": "slurm_platform_test"}
        self.suite = Suite(name='Idm Suite')
        self.suite.update_tags({'name': 'testing_suite', 'idmtools': '123'})
        self.platform.create_items([self.suite])
        # add experiment to suite
        self.suite.add_experiment(self.experiment)

    def test_canceling_a_full_experiment(self):
        self.platform.run_items(items=[self.experiment])
        time.sleep(5)  # simulations should now exist in slurm

        job_id = self.platform.get_slurm_job_id_for_item(item=self.experiment)
        self.assertIsNotNone(job_id)
        self.assertIsNotNone(self.experiment.uid)
        self.assertEqual(self.experiment.simulation_count, 5)

        self.platform.cancel_items(items=[self.experiment])
        self.platform.refresh_status(item=self.experiment)
        
        self.assertEqual(self.experiment.status, EntityStatus.FAILED)
        # at least one simulation should have been marked as failed/canceled . Probably all, but technically only
        # one is necessary
        self.assertTrue(len([sim for sim in self.experiment.simulations if sim.status == EntityStatus.FAILED]) >= 1)

    # Not implemented in current work scope
    def test_canceling_a_single_simulation(self):
        pass

    # Not implemented in current work scope
    def test_canceling_a_full_suite(self):
        pass


if __name__ == '__main__':
    unittest.main()

