import json
from pathlib import Path
import shutil
import tempfile
import unittest

from idmtools.core import ItemType
from idmtools.core.interfaces.json_metadata_operations import JSONMetadataOperations
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.suite import Suite


class JSONMetadataOperationsTest(unittest.TestCase):

    @staticmethod
    def _initialize_data(data, root_directory):
        # create the network of sim, exp, suite objects as specified by the input (with parentage linked up)
        # create specified metadata for each of them.
        suites = []
        experiments = []
        simulations = []

        for suite_id, suite_dict in data.items():
            suite = Suite()
            suite.uid = suite_id
            suites.append(suite)

            for exp_id, exp_dict in suite_dict['experiments'].items():
                exp = Experiment()
                exp.uid = exp_id
                exp.parent = suite
                experiments.append(exp)

                for sim_id, sim_dict in exp_dict['simulations'].items():
                    sim = Simulation()
                    sim.uid = sim_id
                    sim.parent = exp
                    simulations.append(sim)

                    metadata = sim_dict['metadata']
                    path = Path(root_directory, suite_id, exp_id, sim_id, JSONMetadataOperations.METADATA_FILENAME)
                    path.parent.mkdir(parents=True)
                    with path.open('w') as f:
                        json.dump(metadata, f)

                metadata = exp_dict['metadata']
                path = Path(root_directory, suite_id, exp_id, JSONMetadataOperations.METADATA_FILENAME)
                with path.open('w') as f:
                    json.dump(metadata, f)

            metadata = suite_dict['metadata']
            path = Path(root_directory, suite_id, JSONMetadataOperations.METADATA_FILENAME)
            with path.open('w') as f:
                json.dump(metadata, f)

        return suites, experiments, simulations

    def setUp(self):
        self.suite_data = {
            'suite1': {
                'metadata': {'meta': 'data', 'data': 'meta'},
                'experiments': {
                    'exp1': {
                        'metadata': {'1': 2},
                        'simulations': {
                            'sim1': {
                                'metadata': {'a': 1, 'b': 1}
                            },
                            'sim2': {
                                'metadata': {'a': 1, 'b': 2}
                            }
                        },
                    },
                    'exp2': {
                        'metadata': {'2': 3, '3': 4},
                        'simulations': {
                            'sim3': {
                                'metadata': {'a': 1, 'b': 3}
                            },
                        },
                    }
                },
            },
            'suite2': {
                'metadata': {'type': 'executive'},
                'experiments': {
                    'exp3': {
                        'metadata': {'2': 3, '3': 4, '5': 6},
                        'simulations': {
                            'sim4': {
                                'metadata': {'a': 1.1, 'b': '1', 'c': '1'}
                            }
                        }
                    }
                }
            }
        }
        self.metadata_root = Path(tempfile.mkdtemp())
        self.suites, self.experiments, self.simulations = self._initialize_data(data=self.suite_data,
                                                                                root_directory=self.metadata_root)
        self.op = JSONMetadataOperations(metadata_directory_root=self.metadata_root)

    def tearDown(self):
        shutil.rmtree(self.metadata_root)

    #
    # get
    #

    def test_get_works_for_simulations(self):
        sim = [sim for sim in self.simulations if sim.uid == 'sim4'][0]
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual(self.suite_data['suite2']['experiments']['exp3']['simulations']['sim4']['metadata'], metadata)

    def test_get_works_for_experiments(self):
        exp = [exp for exp in self.experiments if exp.uid == 'exp2'][0]
        metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        self.assertEqual(self.suite_data['suite1']['experiments']['exp2']['metadata'], metadata)

    def test_get_works_for_suites(self):
        suite = [suite for suite in self.suites if suite.uid == 'suite1'][0]
        metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual(self.suite_data['suite1']['metadata'], metadata)

    def test_get_creates_empty_metadata_for_previously_non_existant_id(self):
        sim = Simulation()
        sim.uid = 'totally-brand-new'
        exp = Experiment()
        exp.uid = 'very-shiny-new'
        sim.parent = exp
        suite = Suite()
        suite.uid = 'is-it-new-or-knew'
        exp.parent = suite

        # ensure the full set of suite/exp/sim area truly new
        matches = list(self.metadata_root.glob(f"**/{sim.uid}"))
        self.assertEqual(0, len(matches))
        matches = list(self.metadata_root.glob(f"**/{exp.uid}"))
        self.assertEqual(0, len(matches))
        matches = list(self.metadata_root.glob(f"**/{suite.uid}"))
        self.assertEqual(0, len(matches))

        # check each item to ensure newness and return of {}, not failure
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual({}, metadata)

        matches = list(self.metadata_root.glob(f"**/{exp.uid}"))
        self.assertEqual(1, len(matches))  # got made by the sim call
        metadata = self.op.get(item=sim, item_type=ItemType.EXPERIMENT)
        self.assertEqual({}, metadata)

        matches = list(self.metadata_root.glob(f"**/{suite.uid}"))
        self.assertEqual(1, len(matches))  # got made by the sim call
        metadata = self.op.get(item=sim, item_type=ItemType.SUITE)
        self.assertEqual({}, metadata)

    #
    # set
    #

    def test_set_works_for_simulations(self):
        sim = Simulation()
        sim.uid = 'regolith-eaters'
        expected_metadata = {'tag1': 'science', 'tag2': 'microbe'}
        exp = Experiment()
        exp.uid = 'blah'
        sim.parent = exp
        suite = Suite()
        suite.uid = 'also-blah'
        exp.parent = suite

        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual({}, metadata)
        self.op.set(item=sim, item_type=ItemType.SIMULATION, metadata=expected_metadata)
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual(expected_metadata, metadata)

    def test_set_works_for_experiments(self):
        exp = Experiment()
        exp.uid = 'eos chasma national park'
        expected_metadata = {'tag1': 'plant', 'tag2': 'building'}
        suite = Suite()
        suite.uid = 'also-blah'
        exp.parent = suite

        metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        self.assertEqual({}, metadata)
        self.op.set(item=exp, item_type=ItemType.EXPERIMENT, metadata=expected_metadata)
        metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        self.assertEqual(expected_metadata, metadata)

    def test_set_works_for_suites(self):
        suite = Suite()
        suite.uid = 'beam-from-a-thorium-asteroid'
        expected_metadata = {'tag1': 'jovian', 'tag2': 'space'}

        metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual({}, metadata)
        self.op.set(item=suite, item_type=ItemType.SUITE, metadata=expected_metadata)
        metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual(expected_metadata, metadata)

    def test_set_overwrites_existing_metadata(self):
        sim = [sim for sim in self.simulations if sim.uid == 'sim3'][0]
        expected_metadata = {'is': 'this', 'right': 0}

        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual(self.suite_data['suite1']['experiments']['exp2']['simulations']['sim3']['metadata'], metadata)
        self.assertNotEqual(metadata, expected_metadata)
        self.op.set(item=sim, item_type=ItemType.SIMULATION, metadata=expected_metadata)
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual(expected_metadata, metadata)

    #
    # update
    #

    def test_update_works_for_simulations(self):
        # intentionally overwrite an existing metadata key + add new metadata and ensure proper overwrite/merge
        sim = [sim for sim in self.simulations if sim.uid == 'sim2'][0]
        existing_metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        overwritten_key = list(existing_metadata.keys())[0]
        new_metadata = {overwritten_key: 'goodbye-old-data', 'this-is': 'new'}
        expected_metadata = {**existing_metadata, **new_metadata}
        self.op.update(item=sim, item_type=ItemType.SIMULATION, metadata=new_metadata)
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual(expected_metadata, metadata)

    def test_update_works_for_experiments(self):
        # intentionally overwrite an existing metadata key + add new metadata and ensure proper overwrite/merge
        exp = [exp for exp in self.experiments if exp.uid == 'exp1'][0]
        existing_metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        overwritten_key = list(existing_metadata.keys())[0]
        new_metadata = {overwritten_key: 'terraforming-mars', 'is': 'awesome'}
        expected_metadata = {**existing_metadata, **new_metadata}
        self.op.update(item=exp, item_type=ItemType.EXPERIMENT, metadata=new_metadata)
        metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        self.assertEqual(expected_metadata, metadata)

    def test_update_works_for_suites(self):
        # intentionally overwrite an existing metadata key + add new metadata and ensure proper overwrite/merge
        suite = [suite for suite in self.suites if suite.uid == 'suite2'][0]
        existing_metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        overwritten_key = list(existing_metadata.keys())[0]
        new_metadata = {overwritten_key: 'spirit-island', 'is': 'awesome'}
        expected_metadata = {**existing_metadata, **new_metadata}
        self.op.update(item=suite, item_type=ItemType.SUITE, metadata=new_metadata)
        metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual(expected_metadata, metadata)

    def test_update_works_for_previously_non_existant_id(self):
        sim = Simulation()
        sim.uid = 'electro-catapult'
        expected_metadata = {'tag1': 'building'}
        exp = Experiment()
        exp.uid = 'blah'
        sim.parent = exp
        suite = Suite()
        suite.uid = 'also-blah'
        exp.parent = suite

        # ensure the sim does not exist
        matches = list(self.metadata_root.glob(f"**/{sim.uid}"))
        self.assertEqual(0, len(matches))

        self.op.update(item=suite, item_type=ItemType.SUITE, metadata=expected_metadata)
        metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual(expected_metadata, metadata)

    #
    # clear
    #

    def test_clear_works_for_simulations(self):
        sim = [sim for sim in self.simulations if sim.uid == 'sim2'][0]
        existing_metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual(self.suite_data['suite1']['experiments']['exp1']['simulations']['sim2']['metadata'], existing_metadata)
        self.op.clear(item=sim, item_type=ItemType.SIMULATION)
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual({}, metadata)

    def test_works_for_experiments(self):
        exp = [exp for exp in self.experiments if exp.uid == 'exp1'][0]
        existing_metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        self.assertEqual(self.suite_data['suite1']['experiments']['exp1']['metadata'], existing_metadata)
        self.op.clear(item=exp, item_type=ItemType.EXPERIMENT)
        metadata = self.op.get(item=exp, item_type=ItemType.EXPERIMENT)
        self.assertEqual({}, metadata)

    def test_works_for_suites(self):
        suite = [exp for exp in self.suites if exp.uid == 'suite2'][0]
        existing_metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual(self.suite_data['suite2']['metadata'], existing_metadata)
        self.op.clear(item=suite, item_type=ItemType.SUITE)
        metadata = self.op.get(item=suite, item_type=ItemType.SUITE)
        self.assertEqual({}, metadata)

    def test_clear_works_for_previously_non_existant_id(self):
        sim = Simulation()
        sim.uid = 'mars-university'
        exp = Experiment()
        exp.uid = 'blah'
        sim.parent = exp
        suite = Suite()
        suite.uid = 'also-blah'
        exp.parent = suite

        # ensure the sim does not exist
        matches = list(self.metadata_root.glob(f"**/{sim.uid}"))
        self.assertEqual(0, len(matches))

        self.op.clear(item=sim, item_type=ItemType.SIMULATION)
        metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        self.assertEqual({}, metadata)

    #
    # filter
    #

    def test_filter_works_for_simulations(self):
        filter = {'a': 1}
        expected_ids = ['sim1', 'sim2', 'sim3']

        sims = self.op.filter(items=self.simulations, item_type=ItemType.SIMULATION, filter=filter)
        self.assertEqual(sorted(expected_ids), sorted([sim.uid for sim in sims]))

    def test_filter_works_for_experiments(self):
        filter = {'2': 3, '3': 4}
        expected_ids = ['exp2', 'exp3']

        exps = self.op.filter(items=self.experiments, item_type=ItemType.EXPERIMENT, filter=filter)
        self.assertEqual(sorted(expected_ids), sorted([sim.uid for sim in exps]))

    def test_filter_works_for_suites(self):
        filter = {'meta': 'data', 'data': 'meta'}
        expected_ids = ['suite1']

        suites = self.op.filter(items=self.suites, item_type=ItemType.SUITE, filter=filter)
        self.assertEqual(sorted(expected_ids), sorted([sim.uid for sim in suites]))

    def test_filter_works_when_there_are_no_matches_but_the_metadata_key_exists(self):
        sim = self.simulations[0]
        existing_metadata = self.op.get(item=sim, item_type=ItemType.SIMULATION)
        existing_key = list(existing_metadata.keys())[0]
        filter = {existing_key: 'definitely-not-a-preset-value'}

        sims = self.op.filter(items=self.simulations, item_type=ItemType.SIMULATION, filter=filter)
        self.assertEqual([], sorted([sim.uid for sim in sims]))

    def test_filter_works_when_requesting_non_existant_metadata_keys(self):
        filter = {'definitely-not-a-metadata-ke-that-has-been-used': 'before'}
        sims = self.op.filter(items=self.simulations, item_type=ItemType.SIMULATION, filter=filter)
        self.assertEqual([], sorted([sim.uid for sim in sims]))
