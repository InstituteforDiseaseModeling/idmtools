from pathlib import Path
import shutil
import tempfile
import unittest
from uuid import uuid4

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.suite import Suite
from idmtools_platform_slurm.platform_operations.json_metadata_operations import JSONMetadataOperations


class JSONMetadataOperationsTest(unittest.TestCase):

    @staticmethod
    def _initialize_data(self):
        # create 1 suite, 2 experiments, 3 simulations for general usage. Meta is default one for each item
        suite = Suite(_uid=uuid4())
        exp1 = Experiment(_uid=uuid4())
        exp1.suite = suite
        exp2 = Experiment(_uid=uuid4())
        exp2.suite = suite
        simulation1 = Simulation(_uid=uuid4())
        simulation2 = Simulation(_uid=uuid4())
        simulation3 = Simulation(_uid=uuid4())
        simulation1.experiment = exp1
        simulation2.experiment = exp1
        simulation3.experiment = exp2
        self.op.dump(simulation1)
        self.op.dump(simulation2)
        self.op.dump(simulation3)
        self.op.dump(exp1)
        self.op.dump(exp2)
        self.op.dump(suite)
        suites = [suite]
        experiments = [exp1, exp2]
        simulations = [simulation1, simulation2, simulation3]
        return suites, experiments, simulations

    def setUp(self):
        self.metadata_root = Path(tempfile.mkdtemp())
        self.platform = Platform('SLURM_LOCAL', job_directory=self.metadata_root)
        self.op = JSONMetadataOperations(self.platform)

    def tearDown(self):
        shutil.rmtree(self.metadata_root)

    # test get meta for simulation
    def test_get_for_simulation_meta(self):
        _, experiments, simulations = self._initialize_data(self)
        sim = simulations[2]  # test simulation3 and experiment2
        metadata = self.op.get(item=sim)
        expected_meta = {'platform_id': None, 'status': None, 'tags': {}, 'item_type': 'Simulation', 'name': None,
                         'assets': [], 'task': None}
        expected_meta.update({"parent_id": experiments[1].id})
        expected_meta.update({"_uid": sim.id})
        self.assertEqual(expected_meta, metadata)

    # test get meta for experiment
    def test_get_for_experiment_meta(self):
        suites, experiments, _ = self._initialize_data(self)
        exp = experiments[1]
        metadata = self.op.get(item=exp)
        expected_meta = {'platform_id': None, 'status': None, 'tags': {}, 'item_type': 'Experiment', 'name': None,
                         'assets': [], 'suite_id': None, 'task_type': 'idmtools.entities.command_task.CommandTask',
                         'platform_requirements': None, 'frozen': False, 'gather_common_assets_from_task': True,
                         'simulations': []}
        expected_meta.update({"parent_id": suites[0].id})
        expected_meta.update({"_uid": exp.id})
        self.assertEqual(expected_meta, metadata)

    # test get meta for suite
    def test_get_for_suite_meta(self):
        suites, experiments, _ = self._initialize_data(self)
        suite = suites[0]
        metadata = self.op.get(item=suite)
        expected_suite_meta = {'platform_id': None, 'parent_id': None, 'status': None, 'tags': {}, 'item_type': 'Suite',
                               'name': None, 'description': None}
        exp_meta_dict1 = {'platform_id': None, 'status': None, 'tags': {}, 'item_type': 'Experiment', 'name': None,
                          'assets': [], 'suite_id': None, 'task_type': 'idmtools.entities.command_task.CommandTask',
                          'platform_requirements': None, 'frozen': False, 'gather_common_assets_from_task': True,
                          'simulations': []}
        exp_meta_dict2 = exp_meta_dict1.copy()
        exp_meta_dict1.update({"parent_id": suites[0].id})
        exp_meta_dict1.update({"_uid": experiments[0].id})
        exp_meta_dict2.update({"parent_id": suites[0].id})
        exp_meta_dict2.update({"_uid": experiments[1].id})
        expected_suite_meta.update({"parent_id": None})
        expected_suite_meta.update({"_uid": suite.id})
        expected_suite_meta.update({"experiments": [exp_meta_dict1, exp_meta_dict2]})
        self.assertDictEqual(expected_suite_meta, metadata)

    # test load with no meta_data file
    def test_errors_for_no_existent_metadata_file(self):
        sim = Simulation()
        sim.uid = 'totally-brand-new'
        exp = Experiment()
        exp.uid = 'very-shiny-new'
        sim.experiment = exp
        suite = Suite()
        suite.uid = 'is-it-new-or-knew'
        exp.suite = suite

        # ensure there is no meta_data file with path since we did not save to files
        matches = list(self.metadata_root.glob(f"**/{sim.uid}"))
        self.assertEqual(0, len(matches))
        matches = list(self.metadata_root.glob(f"**/{exp.uid}"))
        self.assertEqual(0, len(matches))
        matches = list(self.metadata_root.glob(f"**/{suite.uid}"))
        self.assertEqual(0, len(matches))

        # check exception if we load meta_data from file
        with self.assertRaises(FileNotFoundError) as ex:
            self.op.load(item=sim)
        self.assertEqual("No such file or directory", ex.exception.args[1])
        with self.assertRaises(FileNotFoundError) as ex:
            self.op.load(item=exp)
        self.assertEqual("No such file or directory", ex.exception.args[1])
        with self.assertRaises(FileNotFoundError) as ex:
            self.op.load(item=exp)
        self.assertEqual("No such file or directory", ex.exception.args[1])

    # test override metadata
    def test_update_replace_existing_metadata(self):
        _, _, simulations = self._initialize_data(self)
        sim = simulations[0]
        new_metadata = {'meta': {'a': 11, 'b': 33, 'tags': {'plant': 'pumpkin1'}}}
        self.op.update(item=sim, metadata=new_metadata)  # replace to this new metadata
        metadata = self.op.load(item=sim)
        self.assertEqual(new_metadata, metadata)

    # test update with replace=False metadata, this case is only update/add certain key/values in meta
    def test_update_replace_false_existing_metadata(self):
        _, _, simulations = self._initialize_data(self)
        sim = simulations[0]
        metadata = self.op.load(item=sim)
        new_metadata = {'a': 11, 'c': 33}  # only add these 2 new fields to meta
        self.op.update(item=sim, metadata=new_metadata, replace=False)  # override
        metadata.update(new_metadata)
        expected_updated_meta = metadata
        new_metadata = self.op.load(item=sim)
        self.assertDictEqual(new_metadata, expected_updated_meta)

    # test clear method for simulation
    def test_clear_for_simulations(self):
        _, _, simulations = self._initialize_data(self)
        sim = simulations[0]
        self.op.clear(item=sim)
        metadata = self.op.load(item=sim)
        self.assertEqual({}, metadata)

    # test clear method for experiment
    def test_clear_for_experiments(self):
        _, experiments, _ = self._initialize_data(self)
        exp = experiments[0]
        self.op.clear(item=exp)
        metadata = self.op.load(item=exp)
        self.assertEqual({}, metadata)

    # test clear method for suite
    def test_clear_for_suites(self):
        suites, _, _ = self._initialize_data(self)
        suite = suites[0]
        existing_metadata = self.op.load(item=suite)
        self.op.clear(item=suite)
        metadata = self.op.load(item=suite)
        self.assertEqual({}, metadata)

    def test_clear_errors_for_previously_non_existant_id(self):
        sim = Simulation()
        sim.uid = 'mars-university'
        exp = Experiment()
        exp.uid = 'blah'
        sim.experiment = exp
        suite = Suite()
        suite.uid = 'also-blah'
        exp.suite = suite
        fake_item = "abc"

        # ensure the sim does not exist
        matches = list(self.metadata_root.glob(f"**/{sim.uid}"))
        self.assertEqual(0, len(matches))
        with self.assertRaises(RuntimeError) as ex:
            self.op.clear(item=fake_item)
        self.assertEqual("Clear method supports Suite/Experiment/Simulation only.", ex.exception.args[0])

    def test_filter_for_simulation(self):
        _, _, simulations = self._initialize_data(self)
        properties = {'_uid': simulations[0].id}
        meta_list = []
        for sim in simulations:
            meta_list.append(self.op.load(sim))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                            property_filter=properties)
        # make sure matched meta_data is the one with simulations[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], simulations[0].id)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 1)

    def test_filter_for_simulations(self):
        _, _, simulations = self._initialize_data(self)
        meta_list = []
        for sim in simulations:
            meta_list.append(self.op.load(sim))
        # we do not support following line, we can only do filter multiple times with same key
        # properties = {'_uid': simulations[0].id, '_uid': simulations[1].id}
        properties = {'_uid': simulations[0].id}
        filtered_meta_list0 = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                             property_filter=properties)
        properties = {'_uid': simulations[1].id}
        filtered_meta_list1 = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                             property_filter=properties)
        filtered_meta_list = filtered_meta_list0 + filtered_meta_list1
        # make sure matched meta_data is the one with simulations[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], simulations[0].id)
        self.assertEqual(filtered_meta_list[1]['_uid'], simulations[1].id)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 2)

    def test_filter_for_experiments(self):
        _, experiments, _ = self._initialize_data(self)
        properties = {'_uid': experiments[0].id}
        meta_list = []
        for exp in experiments:
            meta_list.append(self.op.load(exp))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.EXPERIMENT,
                                            property_filter=properties)
        # make sure matched meta_data is the one with experiments[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], experiments[0].id)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 1)

    def test_filter_for_suites(self):
        suites, _, _ = self._initialize_data(self)
        properties = {'_uid': suites[0].id}
        meta_list = []
        for suite in suites:
            meta_list.append(self.op.load(suite))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SUITE, property_filter=properties)
        # make sure matched meta_data is the one with suites[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], suites[0].id)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 1)

    def test_filter_with_tags(self):
        _, _, simulations = self._initialize_data(self)
        # let's add tag to simulations[0] first
        self.op.update(simulations[0], metadata={'tags': {'mytag': 123, "test_tag": "abc"}}, replace=False)
        properties = {'_uid': simulations[0].id}
        tags = {'mytag': 123}  # only filter one of tags
        meta_list = []
        for exp in simulations:
            meta_list.append(self.op.load(exp))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                            property_filter=properties, tag_filter=tags)
        # make sure matched meta_data is the one with suites[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], simulations[0].id)
        # make sure matched meta_data contains tags we added
        self.assertEqual(filtered_meta_list[0]['tags'], {'mytag': 123, "test_tag": "abc"})
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 1)

    def test_filter_when_there_are_no_matches_but_the_metadata_key_exists(self):
        _, _, simulations = self._initialize_data(self)
        properties = {'_uid': "sim0"}
        meta_list = []
        for sim in simulations:
            meta_list.append(self.op.load(sim))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                            property_filter=properties)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 0)

    def test_filter_by_existing_tags_key_only(self):
        _, _, simulations = self._initialize_data(self)
        # let's add tag to simulations[0] first
        self.op.update(simulations[0], metadata={'tags': {'mytag': 123}}, replace=False)
        tags = {'mytag': None}
        meta_list = []
        for exp in simulations:
            meta_list.append(self.op.load(exp))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION, tag_filter=tags)
        # make sure matched meta_data is the one with suites[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], simulations[0].id)
        # make sure matched meta_data contains tags we added
        self.assertEqual(filtered_meta_list[0]['tags'], {'mytag': 123})
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 1)

    def test_filter_with_newly_update_properties(self):
        _, _, simulations = self._initialize_data(self)
        # let's add properties to simulations[0] first
        self.op.update(simulations[0], metadata={'a': 'test'}, replace=False)
        properties = {'a': 'test'}
        meta_list = []
        for exp in simulations:
            meta_list.append(self.op.load(exp))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                            property_filter=properties)
        # make sure matched meta_data is the one with suites[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], simulations[0].id)
        # make sure matched meta_data contains tags we added
        self.assertEqual(filtered_meta_list[0]['a'], 'test')
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 1)

    def test_filter_with_non_existant_metadata_key_value(self):
        _, _, simulations = self._initialize_data(self)
        properties = {'some_key': 123}
        meta_list = []
        for sim in simulations:
            meta_list.append(self.op.load(sim))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                            property_filter=properties)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 0)

    def test_filter_with_non_existant_metadata_key_only(self):
        _, _, simulations = self._initialize_data(self)
        properties = {'some_key': None}
        meta_list = []
        for sim in simulations:
            meta_list.append(self.op.load(sim))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION,
                                            property_filter=properties)
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 0)

    def test_filter_by_key_with_none_value(self):
        _, _, simulations = self._initialize_data(self)
        # let's add tag to simulations[0] first
        self.op.update(simulations[0], metadata={'tags': {'mytag': None}}, replace=False)
        self.op.update(simulations[1], metadata={'tags': {'mytag': None}}, replace=False)
        self.op.update(simulations[2], metadata={'tags': {'mytag': 123}}, replace=False)
        tags = {'mytag': None}
        meta_list = []
        for exp in simulations:
            meta_list.append(self.op.load(exp))
        filtered_meta_list = self.op.filter(meta_items=meta_list, item_type=ItemType.SIMULATION, tag_filter=tags,
                                            ignore_none=False)
        # make sure matched meta_data is the one with suites[0].id
        self.assertEqual(filtered_meta_list[0]['_uid'], simulations[0].id)
        # make sure matched meta_data is the one with suites[0].id
        self.assertEqual(filtered_meta_list[1]['_uid'], simulations[1].id)
        # make sure matched meta_data contains tags we added
        self.assertEqual(filtered_meta_list[0]['tags'], {'mytag': None})
        self.assertEqual(filtered_meta_list[1]['tags'], {'mytag': None})
        # make sure only one matched meta_data
        self.assertEqual(len(filtered_meta_list), 2)
