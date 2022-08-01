import os
import tempfile
from functools import partial
from pathlib import Path
from uuid import UUID

import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType, EntityStatus

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_slurm.platform_operations.utils import add_dammy_suite, SlurmExperiment, SlurmSimulation
from idmtools.assets.asset import Asset

setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")


@pytest.mark.serial
@linux_only
class TestSlurmOperations(ITestWithPersistence):

    def create_experiment(self, platform=None):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, 'python', 'model1.py'),
                                        parameters=dict(c='c-value'))
        task.common_assets.add_asset('input/hello.sh')
        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()
        builder.add_sweep_definition(setA, range(0, 2))
        ts.add_builder(builder)
        exp = Experiment(name=self.case_name, simulations=ts, tags=dict(number_tag=123, KeyOnly=None))
        suite = add_dammy_suite(exp)
        suite.run(platform=platform, wait_until_done=False, wait_on_done=False, dry_run=True)
        return suite, exp

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + '--' + self._testMethodName
        self.job_directory = 'DEST'
        self.platform = Platform('SLURM_LOCAL', job_directory=self.job_directory)
        self.suite, self.exp = self.create_experiment(self.platform)

    def test_retrieve_experiment(self):
        exp = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT)
        # Test attributes
        self.assertEqual(self.exp.uid, exp.uid)
        self.assertEqual(self.exp.name, exp.name)

        # Comps returns tags as string regardless of type
        self.assertEqual({k: (v or None) for k, v in self.exp.tags.items()}, exp.tags)

        # Test the raw retrieval
        slurm_experiment = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT, raw=True)
        self.assertIsInstance(slurm_experiment, SlurmExperiment)
        self.assertEqual(str(self.exp.uid), slurm_experiment.uid)
        self.assertEqual(self.exp.name, slurm_experiment.name)
        self.assertEqual({k: (v or None) for k, v in self.exp.tags.items()}, slurm_experiment.tags)

        # Test retrieving less columns
        slurm_experiment = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT, raw=True)
        self.assertEqual(str(self.exp.uid), slurm_experiment.uid)
        self.assertEqual(self.exp.name, slurm_experiment.name)
        self.assertEqual(str(self.exp.uid), slurm_experiment.uid)

    def test_retrieve_simulation(self):
        base = self.exp.simulations[0]
        sim = self.platform.get_item(base.uid, ItemType.SIMULATION)
        # Test attributes
        self.assertEqual(sim.uid, base.uid)
        self.assertEqual(sim.name, base.name)
        self.assertEqual({k: v for k, v in base.tags.items()}, sim.tags)

        # Test the raw retrieval
        slurm_simulation: SlurmSimulation = self.platform.get_item(base.uid, ItemType.SIMULATION, raw=True)
        self.assertIsInstance(slurm_simulation, SlurmSimulation)
        self.assertEqual(str(base.uid), slurm_simulation.uid)
        self.assertEqual(self.case_name, slurm_simulation.name)
        self.assertEqual({k: v for k, v in base.tags.items()}, slurm_simulation.tags)

    def test_parent(self):
        parent_exp = self.platform.get_parent(self.exp.simulations[0].uid, ItemType.SIMULATION)
        self.assertEqual(self.exp.uid, parent_exp.uid)
        self.assertEqual({k: v or None for k, v in self.exp.tags.items()}, parent_exp.tags)
        parent_suite = self.platform.get_parent(self.exp.uid, ItemType.EXPERIMENT)
        self.assertEqual(self.suite.uid, parent_suite.uid)

    # To test get_children with raw=False(default). Children should be idmtools Simulation or Experiment type
    def test_children(self):
        with self.subTest('test_get_children_for_experiment'):
            children = self.platform.get_children(self.exp.uid, ItemType.EXPERIMENT)
            for child in children:
                self.assertTrue(isinstance(child, Simulation))
                self.assertTrue(isinstance(child.uid, UUID))
            self.assertEqual(len(self.exp.simulations), len(children))
            for s in self.exp.simulations:
                self.assertIn(s.uid, [s.uid for s in children])
            self.assertCountEqual(self.platform.get_children(self.exp.simulations[0].uid, ItemType.SIMULATION), [])

        with self.subTest('test_get_children_for_suite'):
            children = self.platform.get_children(self.suite.uid, ItemType.SUITE)
            for child in children:
                self.assertTrue(isinstance(child, Experiment))
                self.assertTrue(isinstance(child.uid, UUID))
            self.assertEqual(len(children), 1)
            for e in self.suite.experiments:
                self.assertIn(e.uid, [e.uid for e in children])

    # To test get_children with raw=True. Children should be Slurm type
    def test_children_with_raw(self):
        with self.subTest('test_get_children_for_experiment_raw_true'):
            children = self.platform.get_children(self.exp.uid, ItemType.EXPERIMENT, raw=True)
            self.assertEqual(len(self.exp.simulations), len(children))
            for child in children:
                self.assertTrue(isinstance(child, SlurmSimulation))
                self.assertTrue(isinstance(child.uid, str))
        with self.subTest('test_get_children_for_suite_raw_true'):
            children = self.platform.get_children(self.suite.uid, ItemType.SUITE, raw=True)
            self.assertEqual(len(children), 1)
            for child in children:
                self.assertTrue(isinstance(child, SlurmExperiment))
                self.assertTrue(isinstance(child.uid, str))

    def test_experiment_list_assets(self):
        with self.subTest('test_list_assets'):
            assets = self.platform._experiments.list_assets(self.exp)
            self.assertEqual(2, len(assets))
            self.assertEqual(set([asset.filename for asset in assets]), set(['model1.py', 'hello.sh']))
            experiment_dir = Path.resolve(self.platform._op_client.get_directory(self.exp))
            expected_assets_path = [str(experiment_dir.joinpath('Assets/model1.py')),
                                    str(experiment_dir.joinpath('Assets/hello.sh'))]
            self.assertEqual(set([asset.absolute_path for asset in assets]), set(expected_assets_path))

        with self.subTest('test_list_assets_add_exclude'):
            assets = self.platform._simulations.list_assets(self.exp.simulations[0], exclude='hello.sh')
            self.assertEqual(4, len(assets))
            self.assertTrue(["hello.sh" is not asset.filename for asset in assets])

    def test_simulation_list_assets(self):
        count = 0
        for sim in self.exp.simulations:
            assets = self.platform._simulations.list_assets(sim)
            self.assertEqual(3, len(assets))
            self.assertEqual(set([asset.filename for asset in assets]),
                             set(['model1.py', 'hello.sh', 'config.json']))
            simulation_dir = Path.resolve(self.platform._op_client.get_directory(sim))
            expected_assets_path = [str(simulation_dir.joinpath('Assets/model1.py')),
                                    str(simulation_dir.joinpath('Assets/hello.sh')),
                                    str(simulation_dir.joinpath('config.json'))]
            self.assertEqual(set([asset.absolute_path for asset in assets]), set(expected_assets_path))
            count += 1
        self.assertEqual(count, 2)

    def test_to_entity(self):
        slurm_experiment = self.platform.get_item(self.exp.id, item_type=ItemType.EXPERIMENT, raw=True)
        idm_experiment = self.platform._experiments.to_entity(slurm_experiment)
        self.assertEqual(slurm_experiment.id, idm_experiment.id)
        self.assertEqual(slurm_experiment.uid, idm_experiment.id)
        self.assertEqual(slurm_experiment.name, idm_experiment.name)
        self.assertEqual(slurm_experiment.tags, idm_experiment.tags)
        self.assertEqual(set(slurm_experiment.simulations),
                         set([sim.id for sim in idm_experiment.simulations.items]))

        # we only compare asset filenames
        slurm_experiment_assets = [asset['filename'] for asset in slurm_experiment.assets]
        idm_experiment_assets = [asset.filename for asset in idm_experiment.assets]
        self.assertEqual(set(slurm_experiment_assets), set(idm_experiment_assets))
        self.assertEqual(slurm_experiment.status, 'CREATED')
        self.assertEqual(idm_experiment.status, EntityStatus.CREATED)

    def test_get_files(self):
        with self.subTest('test_get_files_for_experiment'):
            exp_files = self.platform.get_files(self.exp, ['Assets/model1.py', 'Assets/hello.sh'])
            with open(os.path.join(COMMON_INPUT_PATH, 'python', 'model1.py'), 'rb') as m:
                self.assertEqual(exp_files[self.exp.simulations[0].uid]['Assets/model1.py'], m.read())
            with open('input/hello.sh', 'rb') as m:
                self.assertEqual(exp_files[self.exp.simulations[0].uid]['Assets/hello.sh'], m.read())

        with self.subTest('test_get_files_for_simulation'):
            # get_file from one of simulations
            output_dir = tempfile.TemporaryDirectory().name  # save files to temp dir
            files_needed = ["config.json", 'Assets/model1.py', 'Assets/hello.sh']
            files_retrieved = self.platform.get_files(item=self.exp.simulations[0], files=files_needed,
                                                      output=output_dir)
            with open(os.path.join(output_dir, self.exp.simulations[0].id, 'Assets', 'model1.py'), 'rb') as m:
                self.assertEqual(files_retrieved['Assets/model1.py'], m.read())
            with open(os.path.join(output_dir, self.exp.simulations[0].id, 'Assets', 'hello.sh'), 'rb') as m:
                self.assertEqual(files_retrieved['Assets/hello.sh'], m.read())
            with open(os.path.join(output_dir, self.exp.simulations[0].id, 'config.json'), 'rb') as m:
                self.assertEqual(files_retrieved['config.json'], m.read())

        with self.subTest('test_get_files_for_experiment_no_existing'):
            with self.assertRaises(RuntimeError) as context:
                self.platform.get_files(self.exp, ['Assets/no_existing.txt'])
            self.assertTrue(
                    "Couldn't find asset for path 'Assets/no_existing.txt'." in str(context.exception.args[0]))

    def test_get_files_by_id(self):
        with self.subTest('test_get_files_by_id_for_experiment'):
            exp_files = self.platform.get_files_by_id(self.exp.id, ItemType.EXPERIMENT,
                                                      ['Assets/model1.py', 'Assets/hello.sh'])
            with open(os.path.join(COMMON_INPUT_PATH, 'python', 'model1.py'), 'rb') as m:
                self.assertEqual(exp_files[self.exp.simulations[0].uid]['Assets/model1.py'], m.read())
            with open('input/hello.sh', 'rb') as m:
                self.assertEqual(exp_files[self.exp.simulations[0].uid]['Assets/hello.sh'], m.read())

        with self.subTest('test_get_files_by_id_for_simulation'):
            # get_file from one of simulations
            output_dir = tempfile.TemporaryDirectory().name  # save files to temp dir
            files_needed = ["config.json", 'Assets/model1.py', 'Assets/hello.sh']
            files_retrieved = self.platform.get_files_by_id(self.exp.simulations[0].id, ItemType.SIMULATION,
                                                            files=files_needed, output=output_dir)
            with open(os.path.join(output_dir, self.exp.simulations[0].id, 'Assets', 'model1.py'), 'rb') as m:
                self.assertEqual(files_retrieved['Assets/model1.py'], m.read())
            with open(os.path.join(output_dir, self.exp.simulations[0].id, 'Assets', 'hello.sh'), 'rb') as m:
                self.assertEqual(files_retrieved['Assets/hello.sh'], m.read())
            with open(os.path.join(output_dir, self.exp.simulations[0].id, 'config.json'), 'rb') as m:
                self.assertEqual(files_retrieved['config.json'], m.read())

    def test_get_files_from_dynamic_created(self):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, 'python', 'model1.py'),
                                        parameters=dict(c='c-value'))
        task.common_assets.add_asset(Asset(content="test", filename="test.txt"))
        exp = Experiment.from_task(task, name=self.case_name)
        suite = add_dammy_suite(exp)
        platform = Platform('SLURM_LOCAL', job_directory="test")
        suite.run(platform=platform, wait_until_done=False, wait_on_done=False, dry_run=True)
        my_exp = platform.get_item(exp.id, ItemType.EXPERIMENT)
        self.assertEqual(my_exp.id, exp.id)
        assets = my_exp.assets
        self.assertEqual(2, len(assets))
        self.assertEqual(set([asset.filename for asset in assets]), set(['model1.py', 'test.txt']))
