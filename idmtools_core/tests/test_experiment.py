import os
import sys
import unittest

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test.utils.test_task import TestTask


def get_new_simulations(n=None, assets=None, asset_files=None, jitter=0):
    asset_files = asset_files or []
    ts = TemplatedSimulations(base_task=TestTask(common_asset_paths=asset_files))
    # create a new sweep for new simulations
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                                 [i * i for i in range(100+jitter, 110+jitter, 3)])
    ts.add_builder(builder=builder)
    if assets is not None:
        ts.base_simulation.assets.add_assets(assets)

    new_simulations = ts if n is None else [simulation for simulation in ts.simulations()][0:n]
    return new_simulations



class TestAddingSimulationsToExistingExperiment(unittest.TestCase):

    def setUp(self):
        model_path = os.path.join("..", "..", "examples", "python_model", "inputs", "simple_python", "model.py")
        self.base_task = JSONConfiguredPythonTask(script_path=model_path, python_path=sys.executable)

    def test_adding_template_to_existing(self):
        with Platform("TestExecute", missing_ok=True, default_missing=dict(type='TestExecute')):
            builder = SimulationBuilder()
            builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5)])
            exp = Experiment.from_builder(builder, base_task=self.base_task)
            exp.run(wait_until_done=True)

            self.assertFalse(exp.assets.is_editable())
            # existing sims and status
            sims = {sim.id: sim for sim in exp.simulations}
            # add new simulations
            builder = SimulationBuilder()
            builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("Run_Number"), [i for i in range(5, 10)])
            exp.simulations.extend(TemplatedSimulations(base_task=self.base_task, builders=[builder]))
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

#
# class TestAddingSimulationsToExistingExperiment(unittest.TestCase):
#
#     def setUp(self):
#         self.experiment = Experiment.from_task(TestTask())
#
#         # no need to actually run the simulations, just mark them done
#         self.experiment.simulations.items.set_status(status=EntityStatus.SUCCEEDED)
#
#     def test_adding_non_builder_simulations_should_work(self) -> None:
#         # initial pre-existing sim has no assets
#         expected = [{'simulations': self.experiment.simulations.items, 'asset_collection': AssetCollection(assets=[])}]
#
#         file = '/a/b/c.csv'
#         new_simulations = get_new_simulations(asset_files=[file], n=1)
#
#         # create a copy of the simulations to add for verification purposes
#         simulations_to_add = [copy.copy(sim) for sim in new_simulations]
#
#         self.experiment.simulations.extend(new_simulations)
#
#         # set up the expected result
#         new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
#         expected.append({'simulations': simulations_to_add, 'asset_collection': new_asset_collection})
#
#         for simulation_set in expected:
#             self.verify_simulations(experiment=self.experiment, simulations=simulation_set['simulations'],
#                                     expected_asset_collection=simulation_set['asset_collection'])
#
#     def test_adding_TemplatedSimulations_should_work(self) -> None:
#         # initial pre-existing sim has no assets
#         expected = [{'simulations': self.experiment.simulations.items, 'asset_collection': AssetCollection(assets=[])}]
#
#         file = '/a/b/c.csv'
#         new_simulations = get_new_simulations(asset_files=[file])
#
#         # create a copy of the simulations to add for verification purposes
#         simulations_to_add = [simulation for simulation in new_simulations.simulations()]
#
#         self.experiment.extend(simulations=new_simulations)
#
#         # set up the expected result
#         new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
#         expected.append({'simulations': simulations_to_add, 'asset_collection': new_asset_collection})
#
#         # dummy add to trigger asset-gathering of most recently added simulations, which normally occurs
#         # when sims are run.
#         self.experiment.extend(simulations=[])
#
#         for simulation_set in expected:
#             self.verify_simulations(experiment=self.experiment, simulations=simulation_set['simulations'],
#                                     expected_asset_collection=simulation_set['asset_collection'])
#
#     def test_adding_simulations_repeatedly_before_running_should_work(self) -> None:
#         files = ['/a/b/c.csv', '/a/b/c/d.csv']
#         jitter = 0
#
#         # initial pre-existing sim has no assets
#         expected = [{'simulations': self.experiment.simulations.items, 'asset_collection': AssetCollection(assets=[])}]
#
#         for file in files:
#             for simulation in self.experiment.simulations.items:
#                 simulation.uid = simulation.uid  # terrible, ugly hack to get around hashing changes altering the uid
#
#             new_simulations = get_new_simulations(asset_files=[file], jitter=jitter)
#
#             # add the new simulations and keep track of the existing and total simulation lists
#
#             # create a copy of the simulations to add for verification purposes
#             simulations_to_add = [simulation for simulation in new_simulations.simulations()]
#
#             self.experiment.extend(simulations=new_simulations)
#
#             # set up the expected result
#             new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
#             expected.append({'simulations': simulations_to_add, 'asset_collection': new_asset_collection})
#
#
#             updated_simulations = [simulation for simulation in self.experiment.simulations.items]
#             print('uids after adding new batch:\n%s' % '\n'.join([s.uid for s in updated_simulations]))
#
#             jitter += 10
#
#         # dummy add to trigger asset-gathering of most recently added simulations, which normally occurs
#         # when sims are run.
#         self.experiment.extend(simulations=[])
#         print('')
#
#         for simulation_set in expected:
#             self.verify_simulations(experiment=self.experiment, simulations=simulation_set['simulations'],
#                                     expected_asset_collection=simulation_set['asset_collection'])
#
#     def verify_simulations(self, experiment, simulations, expected_asset_collection):
#         # ensures the specified simulations exist in the experiment, have the same status, and the expected assets
#         for simulation in simulations:
#             # first find the matching sim in the experiment
#             in_experiment_simulation = [sim for sim in experiment.simulations.items if sim.uid == simulation.uid]
#             self.assertEqual(1, len(in_experiment_simulation))
#             in_experiment_simulation = in_experiment_simulation[0]
#
#             # now ensure it is the same, except assets
#             self.assertEqual(in_experiment_simulation.status, simulation.status)
#
#             # now ensure assets are correct
#             self.assertTrue(in_experiment_simulation.assets is not None)
#             self.assertEqual(in_experiment_simulation.assets, expected_asset_collection)
#
#
# class TestExperimentStatus(unittest.TestCase):
#
#     def setUp(self):
#         self.experiment = Experiment(simulations=get_new_simulations(n=5))
#
#         # # no need to actually run the simulations, just mark them done
#         # self.experiment.simulations.items.set_status(status=EntityStatus.SUCCEEDED)
#
#     def set_simulation_statuses_and_check_experiment_status(self, statuses, expected_status):
#         self.assertTrue(len(self.experiment.simulations), sum(statuses.values()))
#         status_list = itertools.chain(*[count*[status] for status, count in statuses.items()])
#         for simulation in self.experiment.simulations:
#             simulation.status = next(status_list)
#         self.assertEqual(expected_status, self.experiment.status, f'Expected {expected_status}, was {self.experiment.status}, sim statuses: {statuses}')
#
#     def test_status_is_correct(self) -> None:
#         #
#         # single sim status cases
#         #
#
#         # no simulations in exp
#
#         # all sims are CREATED
#         expected = EntityStatus.CREATED
#         statuses = {EntityStatus.CREATED: 5}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # all sims are RUNNING
#         expected = EntityStatus.RUNNING
#         statuses = {EntityStatus.RUNNING: 5}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # all sims are SUCCEEDED
#         expected = EntityStatus.SUCCEEDED
#         statuses = {EntityStatus.SUCCEEDED: 5}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # all sims are FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.FAILED: 5}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # all sims are None
#         expected = None
#         statuses = {None: 5}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#
#         #
#         # 2-way sim status mixes
#         #
#
#         # some CREATED, RUNNING
#         expected = EntityStatus.RUNNING
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, SUCCEEDED
#         expected = EntityStatus.CREATED
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.FAILED: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, None
#         expected = EntityStatus.CREATED  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, None: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some RUNNING, SUCCEEDED
#         expected = EntityStatus.RUNNING
#         statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some RUNNING, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.RUNNING: 1, EntityStatus.FAILED: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some RUNNING, None
#         expected = EntityStatus.RUNNING  # should only exist during commissioning process
#         statuses = {EntityStatus.RUNNING: 1, None: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some SUCCEEDED, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some SUCCEEDED, None
#         expected = EntityStatus.CREATED
#         statuses = {EntityStatus.SUCCEEDED: 1, None: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some FAILED, None
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.FAILED: 1, None: 4}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         #
#         # 3-way sim status mixes
#         #
#
#         # some CREATED, RUNNING, SUCCEEDED
#         expected = EntityStatus.RUNNING
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, EntityStatus.SUCCEEDED: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, RUNNING, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, EntityStatus.FAILED: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, RUNNING, None
#         expected = EntityStatus.RUNNING  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some CREATED, SUCCEEDED, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 2, EntityStatus.FAILED: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, SUCCEEDED, None
#         expected = EntityStatus.CREATED  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 2, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some CREATED, FAILED, None
#         expected = EntityStatus.FAILED  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.FAILED: 2, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some RUNNING, SUCCEEDED, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 2, EntityStatus.FAILED: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some RUNNING, SUCCEEDED, None
#         expected = EntityStatus.RUNNING  # should only exist during commissioning process
#         statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 2, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some RUNNING, FAILED, None
#         expected = EntityStatus.FAILED  # should only exist during commissioning process
#         statuses = {EntityStatus.RUNNING: 1, EntityStatus.FAILED: 2, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # ---
#
#         # some SUCCEEDED, FAILED, None
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 2, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         #
#         # 4-way sim status mixes
#         #
#
#         # some CREATED, RUNNING, SUCCEEDED, FAILED
#         expected = EntityStatus.FAILED
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, RUNNING, SUCCEEDED, None
#         expected = EntityStatus.RUNNING  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, RUNNING, FAILED, None
#         expected = EntityStatus.FAILED  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.FAILED: 1, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some CREATED, SUCCEEDED, FAILED, None
#         expected = EntityStatus.FAILED  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         # some RUNNING, SUCCEEDED, FAILED, None
#         expected = EntityStatus.FAILED  # should only exist during commissioning process
#         statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1, None: 2}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
#
#         #
#         # 5-way sim status mix
#         #
#
#         # some CREATED, RUNNING, SUCCEEDED, FAILED, None
#         expected = EntityStatus.FAILED  # should only exist during commissioning process
#         statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1,
#                     None: 1}
#         self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
