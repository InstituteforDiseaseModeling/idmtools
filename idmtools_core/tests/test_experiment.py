import itertools
import unittest

from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SimulationBuilder
from idmtools.core.enums import EntityStatus
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
        ts.base_simulation.assets = assets

    new_simulations = ts if n is None else [simulation for simulation in ts.simulations()][0:n]
    return new_simulations


class TestAddingSimulationsToExistingExperiment(unittest.TestCase):

    def setUp(self):
        self.experiment = Experiment.from_task(TestTask())

        # no need to actually run the simulations, just mark them done
        self.experiment.simulations.items.set_status(status=EntityStatus.SUCCEEDED)

    def test_adding_non_builder_simulations_should_work(self) -> None:
        # new_simulations = get_new_simulations(n=1)
        #
        # # add the new simulation and keep track of the existing and total simulation lists
        # existing_simulations = [simulation for simulation in self.experiment.simulations.items]
        # self.experiment.add_new_simulations(simulations=new_simulations)
        # self.verify_added_simulations(experiment=self.experiment, existing_simulations=existing_simulations,
        #                               simulations_to_add=new_simulations)

        # initial pre-existing sim has no assets
        expected = [{'simulations': self.experiment.simulations.items, 'asset_collection': AssetCollection(assets=[])}]

        file = '/a/b/c.csv'
        new_simulations = get_new_simulations(asset_files=[file], n=1)

        # create a copy of the simulations to add for verification purposes
        simulations_to_add = [simulation for simulation in new_simulations.simulations()]

        self.experiment.add_new_simulations(simulations=new_simulations)

        # set up the expected result
        new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
        expected.append({'simulations': simulations_to_add, 'asset_collection': new_asset_collection})

        # dummy add to trigger asset-gathering of most recently added simulations, which normally occurs
        # when sims are run.
        self.experiment.add_new_simulations(simulations=[])

        for simulation_set in expected:
            self.verify_simulations(experiment=self.experiment, simulations=simulation_set['simulations'],
                                    expected_asset_collection=simulation_set['asset_collection'])

    def test_adding_TemplatedSimulations_should_work(self) -> None:
        # initial pre-existing sim has no assets
        expected = [{'simulations': self.experiment.simulations.items, 'asset_collection': AssetCollection(assets=[])}]

        file = '/a/b/c.csv'
        new_simulations = get_new_simulations(asset_files=[file])

        # create a copy of the simulations to add for verification purposes
        simulations_to_add = [simulation for simulation in new_simulations.simulations()]

        self.experiment.add_new_simulations(simulations=new_simulations)

        # set up the expected result
        new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
        expected.append({'simulations': simulations_to_add, 'asset_collection': new_asset_collection})

        # dummy add to trigger asset-gathering of most recently added simulations, which normally occurs
        # when sims are run.
        self.experiment.add_new_simulations(simulations=[])

        for simulation_set in expected:
            self.verify_simulations(experiment=self.experiment, simulations=simulation_set['simulations'],
                                    expected_asset_collection=simulation_set['asset_collection'])


    def test_adding_simulations_repeatedly_before_running_should_work(self) -> None:
        # JULY NOTE
        # TODO: simulations_to_add is static uids are static on each pass.
        #  The uid of the original simulation CHANGES in the second pass.
        #  The asset file for the pass-1 added sims changes from c.csv to d.csv in the second pass (where it should not change)
        files = ['/a/b/c.csv', '/a/b/c/d.csv']
        jitter = 0

        # initial pre-existing sim has no assets
        expected = [{'simulations': self.experiment.simulations.items, 'asset_collection': AssetCollection(assets=[])}]

        for file in files:
            for simulation in self.experiment.simulations.items:
                simulation.uid = simulation.uid  # terrible, ugly hack to get around hashing changes altering the uid
            print('----------------------------')
            print('ADDING SIMS WITH FILE %s' % file)
            # TODO: wire in use of TestTask.common_asset_paths to get gather_common_assets() to work properly for test

            # ck4, 7/27 changing this line to the following one
            # new_simulations = get_new_simulations(assets=new_asset_collection, jitter=jitter) #asset_files=[file])  # assets=new_asset_collection, asset_files=[file])
            new_simulations = get_new_simulations(asset_files=[file], jitter=jitter) #asset_files=[file])  # assets=new_asset_collection, asset_files=[file])
            # new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
            # new_simulations = get_new_simulations(assets=new_asset_collection)

            # add the new simulations and keep track of the existing and total simulation lists
            existing_simulations = [simulation for simulation in self.experiment.simulations.items]
            print('1. preexisting uids before adding new batch:\n%s' % '\n'.join([s.uid for s in existing_simulations]))
            # existing_simulations = [simulation for simulation in self.experiment.simulations.items]
            # print('preexisting uids before adding new batch:\n%s' % '\n'.join([s.uid for s in existing_simulations]))

            # create a copy of the simulations to add for verification purposes
            simulations_to_add = [simulation for simulation in new_simulations.simulations()]

            existing_simulations = [simulation for simulation in self.experiment.simulations.items]
            print('2. preexisting uids before adding new batch:\n%s' % '\n'.join([s.uid for s in existing_simulations]))
            # exit()

            self.experiment.add_new_simulations(simulations=new_simulations)

            # set up the expected result
            new_asset_collection = AssetCollection(assets=[Asset(absolute_path=file)])
            expected.append({'simulations': simulations_to_add, 'asset_collection': new_asset_collection})


            updated_simulations = [simulation for simulation in self.experiment.simulations.items]
            print('uids after adding new batch:\n%s' % '\n'.join([s.uid for s in updated_simulations]))


            # self.verify_added_simulations(self.experiment, existing_simulations, simulations_to_add,
            #                               new_asset_collection=new_asset_collection)
            jitter += 10

        # dummy add to trigger asset-gathering of most recently added simulations, which normally occurs
        # when sims are run.
        self.experiment.add_new_simulations(simulations=[])
        print('')

        for simulation_set in expected:
            self.verify_simulations(experiment=self.experiment, simulations=simulation_set['simulations'],
                                    expected_asset_collection=simulation_set['asset_collection'])


                                    # existing_simulations, simulations_to_add,
                                    #           new_asset_collection=new_asset_collection)

        # seems to work by manual inspection now, but need to update verify_added_simulations(). WHY do REAL sims/tasks NOT need the extra hand-holding conditional for asset setting in Experiment.add_new_simulations ???

    def verify_simulations(self, experiment, simulations, expected_asset_collection):
        # ensures the specified simulations exist in the experiment, have the same status, and the expected assets
        for simulation in simulations:
            # first find the matching sim in the experiment
            in_experiment_simulation = [sim for sim in experiment.simulations.items if sim.uid == simulation.uid]
            self.assertEqual(1, len(in_experiment_simulation))
            in_experiment_simulation = in_experiment_simulation[0]

            # now ensure it is the same, except assets
            self.assertEqual(in_experiment_simulation.status, simulation.status)

            # now ensure assets are correct
            self.assertTrue(in_experiment_simulation.assets is not None)
            self.assertEqual(in_experiment_simulation.assets, expected_asset_collection)

        #
        # # using experiment.simulations.items in here because each iteration over the experiment.simulations object
        # # (a ParentIterator) causes all uids to be set to new values...
        # all_simulations = [simulation for simulation in experiment.simulations.items]
        # existing_uids = [simulation.uid for simulation in existing_simulations]
        # added_simulations = [simulation for simulation in all_simulations if simulation.uid not in existing_uids]
        #
        # print('-')
        # print('Experiment has:\n%d simulations\n%d preexisting\n%d just added' %
        #       (len(all_simulations), len(existing_simulations), len(added_simulations)))
        #
        # # verify that the correct number of simulations were added
        # self.assertEqual(len(existing_simulations) + len(simulations_to_add), len(all_simulations))
        # self.assertEqual(len(simulations_to_add), len(added_simulations))  # 4, 8 on second pass. Correct? No. I think it should be 4, 4
        # # print('-')
        # # print('Preexisting simulations: %s' % '\n'.join([s.uid for s in existing_simulations]))
        # # print('-')
        # # print('Newly added sims: %s' % '\n'.join([s.uid for s in added_simulations]))
        # # print('-')
        # # print('To-add sims: %s' % '\n'.join([s.uid for s in simulations_to_add]))
        #
        # # verify existing simulations have unchanged status and new simulations are ready to be created by a platform
        # # also check that simulation assets are correct for existing sims, and new sims (if requested)
        # for simulation in experiment.simulations.items:
        #     if simulation.uid in existing_uids:
        #
        #         print('-')
        #         print('Comparing status and assets for preexisting simulation uid: %s' % simulation.uid)
        #
        #         existing_simulation = [s for s in existing_simulations if s.uid == simulation.uid][0]
        #         self.assertEqual(existing_simulation.status, simulation.status)
        #         self.assertIsNotNone(existing_simulation.assets)
        #         if existing_simulation.assets != simulation.assets:
        #             print('-')
        #             print("sim: %s\nExisting assets:\n%s\nTest assets:\n%s" %
        #                   (existing_simulation.uid, existing_simulation.assets.assets, simulation.assets.assets))
        #         self.assertEqual(existing_simulation.assets, simulation.assets)
        #
        #         print('-')
        #         print("sim: %s\nAssets match:\n%s" % (existing_simulation.uid, existing_simulation.assets.assets))
        #
        #     else:
        #         self.assertEqual(None, simulation.status)
        #         if new_asset_collection is not None:
        #             self.assertIsNotNone(simulation.assets)
        #             self.assertEqual(new_asset_collection, simulation.assets)
        #
        # # verify assets? TODO



    # def verify_added_simulations(self, experiment, existing_simulations, simulations_to_add, new_asset_collection=None):
    #     # using experiment.simulations.items in here because each iteration over the experiment.simulations object
    #     # (a ParentIterator) causes all uids to be set to new values...
    #     all_simulations = [simulation for simulation in experiment.simulations.items]
    #     existing_uids = [simulation.uid for simulation in existing_simulations]
    #     added_simulations = [simulation for simulation in all_simulations if simulation.uid not in existing_uids]
    #
    #     print('-')
    #     print('Experiment has:\n%d simulations\n%d preexisting\n%d just added' %
    #           (len(all_simulations), len(existing_simulations), len(added_simulations)))
    #
    #     # verify that the correct number of simulations were added
    #     self.assertEqual(len(existing_simulations) + len(simulations_to_add), len(all_simulations))
    #     self.assertEqual(len(simulations_to_add), len(added_simulations))  # 4, 8 on second pass. Correct? No. I think it should be 4, 4
    #     # print('-')
    #     # print('Preexisting simulations: %s' % '\n'.join([s.uid for s in existing_simulations]))
    #     # print('-')
    #     # print('Newly added sims: %s' % '\n'.join([s.uid for s in added_simulations]))
    #     # print('-')
    #     # print('To-add sims: %s' % '\n'.join([s.uid for s in simulations_to_add]))
    #
    #     # verify existing simulations have unchanged status and new simulations are ready to be created by a platform
    #     # also check that simulation assets are correct for existing sims, and new sims (if requested)
    #     for simulation in experiment.simulations.items:
    #         if simulation.uid in existing_uids:
    #
    #             print('-')
    #             print('Comparing status and assets for preexisting simulation uid: %s' % simulation.uid)
    #
    #             existing_simulation = [s for s in existing_simulations if s.uid == simulation.uid][0]
    #             self.assertEqual(existing_simulation.status, simulation.status)
    #             self.assertIsNotNone(existing_simulation.assets)
    #             if existing_simulation.assets != simulation.assets:
    #                 print('-')
    #                 print("sim: %s\nExisting assets:\n%s\nTest assets:\n%s" %
    #                       (existing_simulation.uid, existing_simulation.assets.assets, simulation.assets.assets))
    #             self.assertEqual(existing_simulation.assets, simulation.assets)
    #
    #             print('-')
    #             print("sim: %s\nAssets match:\n%s" % (existing_simulation.uid, existing_simulation.assets.assets))
    #
    #         else:
    #             self.assertEqual(None, simulation.status)
    #             if new_asset_collection is not None:
    #                 self.assertIsNotNone(simulation.assets)
    #                 self.assertEqual(new_asset_collection, simulation.assets)
    #
    #     # verify assets? TODO


class TestExperimentStatus(unittest.TestCase):

    def setUp(self):
        self.experiment = Experiment(simulations=get_new_simulations(n=5))

        # # no need to actually run the simulations, just mark them done
        # self.experiment.simulations.items.set_status(status=EntityStatus.SUCCEEDED)

    def set_simulation_statuses_and_check_experiment_status(self, statuses, expected_status):
        self.assertTrue(len(self.experiment.simulations), sum(statuses.values()))
        status_list = itertools.chain(*[count*[status] for status, count in statuses.items()])
        for simulation in self.experiment.simulations:
            simulation.status = next(status_list)
        self.assertEqual(expected_status, self.experiment.status, f'Expected {expected_status}, was {self.experiment.status}, sim statuses: {statuses}')

    # def test_status_is_correct(self) -> None:
    #     #
    #     # single sim status cases
    #     #
    #
    #     # no simulations in exp
    #
    #     # all sims are CREATED
    #     expected = EntityStatus.CREATED
    #     statuses = {EntityStatus.CREATED: 5}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # all sims are RUNNING
    #     expected = EntityStatus.RUNNING
    #     statuses = {EntityStatus.RUNNING: 5}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # all sims are SUCCEEDED
    #     expected = EntityStatus.SUCCEEDED
    #     statuses = {EntityStatus.SUCCEEDED: 5}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # all sims are FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.FAILED: 5}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # all sims are None
    #     expected = None
    #     statuses = {None: 5}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #
    #     #
    #     # 2-way sim status mixes
    #     #
    #
    #     # some CREATED, RUNNING
    #     expected = EntityStatus.RUNNING
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, SUCCEEDED
    #     expected = EntityStatus.CREATED
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.FAILED: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, None
    #     expected = EntityStatus.CREATED  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, None: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some RUNNING, SUCCEEDED
    #     expected = EntityStatus.RUNNING
    #     statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some RUNNING, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.RUNNING: 1, EntityStatus.FAILED: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some RUNNING, None
    #     expected = EntityStatus.RUNNING  # should only exist during commissioning process
    #     statuses = {EntityStatus.RUNNING: 1, None: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some SUCCEEDED, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some SUCCEEDED, None
    #     expected = EntityStatus.CREATED
    #     statuses = {EntityStatus.SUCCEEDED: 1, None: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some FAILED, None
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.FAILED: 1, None: 4}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     #
    #     # 3-way sim status mixes
    #     #
    #
    #     # some CREATED, RUNNING, SUCCEEDED
    #     expected = EntityStatus.RUNNING
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, EntityStatus.SUCCEEDED: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, RUNNING, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, EntityStatus.FAILED: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, RUNNING, None
    #     expected = EntityStatus.RUNNING  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 2, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some CREATED, SUCCEEDED, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 2, EntityStatus.FAILED: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, SUCCEEDED, None
    #     expected = EntityStatus.CREATED  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 2, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some CREATED, FAILED, None
    #     expected = EntityStatus.FAILED  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.FAILED: 2, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some RUNNING, SUCCEEDED, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 2, EntityStatus.FAILED: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some RUNNING, SUCCEEDED, None
    #     expected = EntityStatus.RUNNING  # should only exist during commissioning process
    #     statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 2, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some RUNNING, FAILED, None
    #     expected = EntityStatus.FAILED  # should only exist during commissioning process
    #     statuses = {EntityStatus.RUNNING: 1, EntityStatus.FAILED: 2, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # ---
    #
    #     # some SUCCEEDED, FAILED, None
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 2, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     #
    #     # 4-way sim status mixes
    #     #
    #
    #     # some CREATED, RUNNING, SUCCEEDED, FAILED
    #     expected = EntityStatus.FAILED
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, RUNNING, SUCCEEDED, None
    #     expected = EntityStatus.RUNNING  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, RUNNING, FAILED, None
    #     expected = EntityStatus.FAILED  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.FAILED: 1, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some CREATED, SUCCEEDED, FAILED, None
    #     expected = EntityStatus.FAILED  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     # some RUNNING, SUCCEEDED, FAILED, None
    #     expected = EntityStatus.FAILED  # should only exist during commissioning process
    #     statuses = {EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1, None: 2}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
    #
    #     #
    #     # 5-way sim status mix
    #     #
    #
    #     # some CREATED, RUNNING, SUCCEEDED, FAILED, None
    #     expected = EntityStatus.FAILED  # should only exist during commissioning process
    #     statuses = {EntityStatus.CREATED: 1, EntityStatus.RUNNING: 1, EntityStatus.SUCCEEDED: 1, EntityStatus.FAILED: 1,
    #                 None: 1}
    #     self.set_simulation_statuses_and_check_experiment_status(statuses=statuses, expected_status=expected)
