import allure
import itertools
import os
import sys
import unittest
from unittest.mock import MagicMock
import pytest
from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core import EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test.utils.utils import captured_output

model_path = os.path.abspath(os.path.join("..", "..", "examples", "python_model", "inputs", "simple_python", "model.py"))


@pytest.mark.smoke
@pytest.mark.serial
@allure.story("Entities")
@allure.suite("idmtools_core")
class TestAddingSimulationsToExistingExperiment(unittest.TestCase):
    def setUp(self):
        self.platform = Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute'))

    def test_adding_template_to_existing(self):
        base_task = JSONConfiguredPythonTask(script_path=model_path, python_path=sys.executable)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5)])
        exp = Experiment.from_builder(builder, base_task=base_task)
        exp.run(wait_until_done=True)

        self.assertFalse(exp.assets.is_editable())
        # add new simulations
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5, 10)])
        exp.simulations.extend(TemplatedSimulations(base_task=base_task, builders=[builder]))
        count = 0
        for sim in exp.simulations:
            if sim.status is None:
                count += 1
        # verify stuff not yet ran
        self.assertTrue(count, 5)
        # previous experiments
        self.assertTrue(len(exp.simulations) - count, 5)
        exp.run(wait_until_done=True)

        self.assertTrue(exp.succeeded)
        self.assertEqual(10, len(exp.simulations))
        with captured_output() as out:
            exp.display()
            self.assertIn(f"{exp.id} - JSONConfiguredPythonTask SimulationBuilder / Sim count 10", out[0].getvalue())
            for i, sim in enumerate(exp.simulations):
                if i > 4:
                    break
                self.assertIn(f"{sim.id} | - Run_Number:{sim.tags['Run_Number']}", out[0].getvalue())

    def test_empty_experiment_template(self):
        base_task = JSONConfiguredPythonTask(script_path=model_path, python_path=sys.executable)
        builder = SimulationBuilder()
        exp = Experiment.from_builder(builder, base_task=base_task)
        with self.assertRaises(ValueError) as er:
            exp.run(wait_until_done=True)
        self.assertTrue(er.exception.args[0], 'You cannot run an empty experiment')

    def test_empty_experiment_list(self):
        exp = Experiment()
        with self.assertRaises(ValueError) as er:
            exp.run(wait_until_done=True)
        self.assertTrue(er.exception.args[0], 'You cannot run an empty experiment')

    def test_adding_manual_simulation(self):
        base_task = JSONConfiguredPythonTask(script_path=model_path, python_path=sys.executable)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5)])
        exp = Experiment.from_builder(builder, base_task=base_task)
        exp.run(wait_until_done=True)

        self.assertFalse(exp.assets.is_editable())
        # existing sims and status
        sims = {sim.id: sim for sim in exp.simulations}
        # add new simulations
        new_sim = Simulation.from_task(base_task)
        new_sim.task.set_parameter("Run_Number", 6)
        exp.simulations.append(new_sim)

        count = 0
        for sim in exp.simulations:
            if sim.status is None:
                count += 1
        # verify stuff not yet ran
        self.assertTrue(count, 1)
        # previous experiments
        self.assertTrue(len(exp.simulations) - count, 5)
        exp.run(wait_until_done=True)

        self.assertTrue(exp.succeeded)
        self.assertEqual(6, len(exp.simulations))

    def test_add_modify_common_assets_again_fail(self):
        base_task = JSONConfiguredPythonTask(script_path=model_path, python_path=sys.executable)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5)])
        exp = Experiment.from_builder(builder, base_task=base_task)
        mock_hook = MagicMock()
        exp.add_post_creation_hook(mock_hook)
        exp.run(wait_until_done=True)
        self.assertEqual(mock_hook.call_count, 1)

        self.assertFalse(exp.assets.is_editable())
        # existing sims and status
        sims = {sim.id: sim for sim in exp.simulations}
        # add new simulations
        new_sim = Simulation.from_task(base_task)
        new_sim.task.set_parameter("Run_Number", 6)
        new_sim.task.common_assets.add_asset(Asset(filename="blah", content="Blah"))
        exp.simulations.append(new_sim)

        count = 0
        for sim in exp.simulations:
            if sim.status is None:
                count += 1
        # verify stuff not yet ran
        self.assertTrue(count, 1)
        # previous experiments
        self.assertTrue(len(exp.simulations) - count, 5)
        with self.assertRaises(ValueError) as r:
            exp.run(wait_until_done=True, regather_common_assets=True)


@pytest.mark.smoke
class TestExperimentStatus(unittest.TestCase):

    def setUp(self):
        model_path = os.path.join("..", "..", "examples", "python_model", "inputs", "simple_python", "model.py")
        self.base_task = JSONConfiguredPythonTask(script_path=model_path, python_path=sys.executable)
        builder = SimulationBuilder()
        builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5)])
        self.experiment = Experiment.from_builder(builder, base_task=self.base_task)
        self.experiment.simulations = list(self.experiment.simulations)

        # # no need to actually run the simulations, just mark them done
        # self.experiment.simulations.items.set_status(status=EntityStatus.SUCCEEDED)

    def set_simulation_statuses_and_check_experiment_status(self, statuses, expected_status):
        self.assertTrue(len(self.experiment.simulations), sum(statuses.values()))
        status_list = itertools.chain(*[count * [status] for status, count in statuses.items()])
        for simulation in self.experiment.simulations:
            simulation.status = next(status_list)
        self.assertEqual(expected_status, self.experiment.status,
                         f'Expected {expected_status}, was {self.experiment.status}, sim statuses: {statuses}')

    def test_status_is_correct(self) -> None:
        #
        # single sim status cases
        #

        # no simulations in exp

        # all sims are CREATED
        expected = EntityStatus.CREATED
        statuses = {EntityStatus.CREATED: 5}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # all sims are RUNNING
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.RUNNING: 5}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # all sims are SUCCEEDED
        expected = EntityStatus.SUCCEEDED
        statuses = {EntityStatus.SUCCEEDED: 5}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # all sims are FAILED
        expected = EntityStatus.FAILED
        statuses = {EntityStatus.FAILED: 5}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # all sims are None
        expected = None
        statuses = {None: 5}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        #
        # 2-way sim status mixes
        #

        # some CREATED, RUNNING
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, SUCCEEDED
        # Since this a transition state we don't identify, the closer status is running. Platforms need to sometimes check status if they have to do extra here
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, FAILED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.FAILED: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, None
        expected = EntityStatus.CREATED  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, None: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some RUNNING, SUCCEEDED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some RUNNING, FAILED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.RUNNING: 1, EntityStatus.FAILED: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some RUNNING, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.RUNNING: 1, None: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some SUCCEEDED, FAILED
        expected = EntityStatus.FAILED
        statuses = {EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some SUCCEEDED, None
        expected = EntityStatus.CREATED
        statuses = {EntityStatus.SUCCEEDED: 1, None: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some FAILED, None
        expected = EntityStatus.CREATED
        statuses = {EntityStatus.FAILED: 1, None: 4}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        #
        # 3-way sim status mixes
        #

        # some CREATED, RUNNING, SUCCEEDED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, EntityStatus.SUCCEEDED: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, RUNNING, FAILED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, EntityStatus.FAILED: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, RUNNING, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some CREATED, SUCCEEDED, FAILED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 2, EntityStatus.FAILED: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, SUCCEEDED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 2, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some CREATED, FAILED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.FAILED: 2, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some RUNNING, SUCCEEDED, FAILED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 2, EntityStatus.FAILED: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some RUNNING, SUCCEEDED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 2, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some RUNNING, FAILED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.RUNNING: 1, EntityStatus.FAILED: 2, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # ---

        # some SUCCEEDED, FAILED, None
        expected = EntityStatus.CREATED
        statuses = {EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 2, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        #
        # 4-way sim status mixes
        #

        # some CREATED, RUNNING, SUCCEEDED, FAILED
        expected = EntityStatus.RUNNING
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, RUNNING, SUCCEEDED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, RUNNING, FAILED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.FAILED: 1, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some CREATED, SUCCEEDED, FAILED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        # some RUNNING, SUCCEEDED, FAILED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1, None: 2}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)

        #
        # 5-way sim status mix
        #

        # some CREATED, RUNNING, SUCCEEDED, FAILED, None
        expected = EntityStatus.RUNNING  # should only exist during commissioning process
        statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1,
                    None: 1}
        self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
