import json
import os
import pathlib
from functools import partial
from typing import Any, Dict

import numpy as np
import pandas as pd
import pytest
from pathlib import Path

import sys

if sys.platform == "win32":
    from win32con import FALSE

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import FileSimulation, FileExperiment, FileSuite

from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
@linux_only
class TestFilePlatform(ITestWithPersistence):

    def create_experiment(self, platform=None, a=1, b=1, retries=None, wait_until_done=False):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        task.python_path = "python3"

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(a))
        builder.add_sweep_definition(partial(param_update, param="b"), range(b))
        ts.add_builder(builder)

        # Now we can create our Experiment using our template builder
        experiment = Experiment.from_template(ts, name=self.case_name)
        # Add our own custom tag to simulation
        experiment.tags["tag1"] = 1
        # And add common assets from local dir
        experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

        # Create suite
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        # Commission
        suite.run(platform=platform, wait_until_done=wait_until_done, retries=retries)
        print("suite_id: " + suite.id)
        print("experiment_id: " + experiment.id)
        return experiment

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.job_directory = "DEST"
        self.platform = Platform('FILE', job_directory=self.job_directory)

    def test_suite_experiment_simulation_files(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        # first verify files and dirs under suite
        suite = experiment.parent
        suite_dir = self.platform.get_directory(suite)
        self.assertEqual(Path(suite_dir), Path(str(suite_dir)))
        files = []
        dirs = []
        for (dirpath, dirnames, filenames) in os.walk(suite_dir):
            files.extend(filenames)
            dirs.extend(dirnames)
            break
        self.assertSetEqual(set(files), set(["metadata.json"]))
        self.assertEqual(dirs[0], f"{experiment.name}_{experiment.id}")
        # second verify files and dirs under experiment
        experiment_dir = self.platform.get_directory(experiment)
        files = []
        for (dirpath, dirnames, filenames) in os.walk(experiment_dir):
            files.extend(filenames)
            break
        self.assertSetEqual(set(files), set(["metadata.json", "run_simulation.sh", "batch.sh"]))

        # verify all files under simulations
        self.assertEqual(experiment.simulation_count, 9)
        count = 0
        for simulation in experiment.simulations:
            simulation_dir = self.platform.get_directory(simulation)
            asserts_dir = simulation_dir.joinpath("Assets")
            files = []
            for (dirpath, dirnames, filenames) in os.walk(simulation_dir):
                if dirnames == ["Assets"]:
                    # verify Assets folder under simulation is symlink and it link to experiment's Assets
                    self.assertTrue(os.path.islink(asserts_dir))
                    target_link = os.readlink(asserts_dir)
                    self.assertEqual(os.path.basename(pathlib.Path(target_link).parent), "..")
                    count = count + 1
                files.extend(filenames)
            self.assertSetEqual(set(files), set(["metadata.json", "_run.sh", "config.json"]))
        self.assertEqual(count, 9)  # make sure we found total 9 symlinks for Assets folder

    def test_generated_scripts(self):
        platform = Platform('FILE', job_directory=self.job_directory, retries=5)
        experiment = self.create_experiment(platform=platform, a=5, b=5)
        experiment_dir = self.platform.get_directory(experiment)
        # verify sbatch.sh script content in experiment level
        with open(os.path.join(experiment_dir, 'batch.sh'), 'r') as fpr:
            contents = fpr.read()
        self.assertIn(
            'find $(pwd) -maxdepth 2 -name "_run.sh" -print0 | xargs -0 -I% dirname % | xargs -d "\\n" -I% bash -c \'cd $(pwd) && $(pwd)/run_simulation.sh %  1>> stdout.txt 2>> stderr.txt\'',
            contents)

        # verify run_simulation.sh script content in experiment level
        with open(os.path.join(experiment_dir, 'run_simulation.sh'), 'r') as fpr:
            contents = fpr.read()
        self.assertIn(
            "JOB_DIRECTORY=$1\necho \"enter directory: \'$JOB_DIRECTORY\'\"", contents)
        self.assertIn("cd $JOB_DIRECTORY", contents)
        self.assertIn("bash _run.sh 1> stdout.txt 2> stderr.txt", contents)

        # verify _run.sh script content under simulation level
        simulation_ids = []
        for simulation in experiment.simulations:
            simulation_ids.append(simulation.id)
            simulation_dir = platform.get_directory(simulation)
            with open(os.path.join(simulation_dir, '_run.sh'), 'r') as fpr:
                contents = fpr.read()

            self.assertIn("python3 Assets/model3.py --config config.json", contents)

        # verify ids in metadata.json  for suite
        suite = experiment.suite
        suite_dir = platform.get_directory(suite)
        with open(os.path.join(suite_dir, 'metadata.json'), 'r') as j:
            contents = json.loads(j.read())
            self.assertEqual(contents['_uid'], suite.id)
            self.assertEqual(contents['uid'], suite.id)
            self.assertEqual(contents['id'], suite.id)
            self.assertEqual(contents['parent_id'], None)
            self.assertEqual(contents['tags'], {'name': 'suite_tag', 'idmtools': '123'})
            self.assertEqual(contents['item_type'], 'Suite')

        # verify ids in metadata.json for experiment
        with open(os.path.join(experiment_dir, 'metadata.json'), 'r') as j:
            contents = json.loads(j.read())
            self.assertEqual(contents['_uid'], experiment.id)
            self.assertEqual(contents['uid'], experiment.id)
            self.assertEqual(contents['id'], experiment.id)
            self.assertEqual(contents['parent_id'], suite.id)
            self.assertEqual(contents['item_type'], 'Experiment')
            self.assertEqual(contents['status'], 'CREATED')
            self.assertEqual(len(contents['assets']), 6)
            self.assertEqual(contents['name'], 'test_platform_file.py--test_generated_scripts')
            self.assertEqual(contents['task_type'], 'idmtools.entities.command_task.CommandTask')

        # verify ids in metadata.json for simulation, also verify sweep parameter in config.json file
        for simulation in experiment.simulations:
            simulation_dir = platform.get_directory(simulation)
            with open(os.path.join(simulation_dir, 'metadata.json'), 'r') as j:
                contents = json.loads(j.read())
                self.assertEqual(contents['_uid'], simulation.id)
                self.assertEqual(contents['uid'], simulation.id)
                self.assertEqual(contents['id'], simulation.id)
                self.assertEqual(contents['parent_id'], experiment.id)
                self.assertEqual(contents['task']['command'], 'python3 Assets/model3.py --config config.json')
                with open(os.path.join(simulation_dir, 'config.json'), 'r') as j:
                    config_contents = json.loads(j.read())
                self.assertDictEqual(contents['task']['parameters'], config_contents['parameters'])

    def test_create_sim_directory_map(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        exp_map = self.platform.create_sim_directory_map(experiment.id, item_type=ItemType.EXPERIMENT)
        sims_map_dict = {}
        for sim in experiment.simulations:
            sim_map = self.platform.create_sim_directory_map(sim.id, item_type=ItemType.SIMULATION)
            self.assertTrue(sim_map[sim.id],
                            os.path.join(self.job_directory, experiment.parent_id, experiment.id, sim.id))
            sims_map_dict.update({sim.id: sim_map[sim.id]})
        self.assertDictEqual(exp_map, sims_map_dict)
        self.assertTrue(len(exp_map) == 9)

    def test_create_sim_directory_df(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        exp_df = self.platform.create_sim_directory_df(experiment.id)
        sims_df = pd.DataFrame()
        for sim in experiment.simulations:
            sim_map = self.platform.create_sim_directory_map(sim.id, item_type=ItemType.SIMULATION)
            sim_tags = sim.tags
            sim_df = pd.DataFrame(sim_tags, index=[0])
            sim_df['simid'] = sim.id
            sim_df['outpath'] = sim_map[sim.id]
            sims_df = pd.concat([sims_df, sim_df], ignore_index=True)
        self.assertTrue(np.all(exp_df.sort_values('simid').values == sims_df.sort_values('simid').values))
        self.assertTrue(exp_df.shape == (9, 6))

    def test_create_sim_directory_csv(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        self.platform.save_sim_directory_df_to_csv(experiment.id)
        exp_df = self.platform.create_sim_directory_df(experiment.id)
        import csv
        sim_list = []
        with open(f"{experiment.id}.csv", newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                sim_list.append(row)
        self.assertTrue(exp_df.values.tolist(), sim_list)
        self.assertTrue(len(sim_list) == 9)
        # cleanup
        os.remove(f"{experiment.id}.csv")

    def test_platform_delete_experiment(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        suite_dir = self.platform.get_directory(experiment.parent)
        exp_dir = self.platform.get_directory(experiment)
        self.platform._experiments.platform_delete(experiment.id)
        # make sure we don't delete suite in this case
        self.assertTrue(os.path.exists(suite_dir))
        # make sure we only delete experiment folder under suite
        self.assertFalse(os.path.exists(exp_dir))
        with self.assertRaises(RuntimeError) as context:
            self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        self.assertTrue(f"Not found Experiment with id '{experiment.id}'" in str(context.exception.args[0]))

    def test_platform_delete_suite(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        self.platform._suites.platform_delete(experiment.parent_id)
        # make sure we delete suite folder
        self.assertFalse(os.path.exists(os.path.join(self.job_directory, experiment.parent_id)))
        with self.assertRaises(RuntimeError) as context:
            self.platform.get_item(experiment.parent_id, item_type=ItemType.SUITE, raw=True)
        self.assertTrue(f"Not found Suite with id '{experiment.parent_id}'" in str(context.exception.args[0]))

    def test_file_suite_experiment_simulation(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        # Test FileSuite
        file_suite = self.platform.get_item(experiment.parent.id, item_type=ItemType.SUITE, raw=True)
        self.assertTrue(isinstance(file_suite, FileSuite))
        self.assertEqual(repr(file_suite), f"<FileSuite {file_suite.id} - {len(file_suite.experiments)} experiments>")
        self.assertEqual(file_suite.id, experiment.parent.id)
        self.assertEqual(file_suite.uid, experiment.suite.id)
        self.assertEqual(file_suite.status, "CREATED")
        self.assertEqual(file_suite.parent, None)
        self.assertDictEqual(file_suite.tags, experiment.parent.tags)
        self.assertEqual(len(file_suite.experiments), 1)
        # validate get_platform_object() method
        file_suite1 = file_suite.get_platform_object()
        self.assertTrue(isinstance(file_suite1, FileSuite))
        self.assertEqual(id(file_suite), id(file_suite1))
        # Test FileExperiment
        file_experiment = self.platform.get_item(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        self.assertTrue(isinstance(file_experiment, FileExperiment))
        self.assertEqual(file_experiment.id, experiment.id)
        self.assertEqual(file_experiment.status, "CREATED")
        self.assertEqual(file_experiment.parent_id, experiment.parent_id)
        self.assertEqual(len(file_experiment.simulations), 9)
        self.assertEqual(repr(file_experiment),
                         f"<FileExperiment {file_experiment.id} - {len(file_experiment.simulations)} simulations>")
        self.assertEqual(file_experiment.parent_id, experiment.parent_id)
        # validate file_experiment assets
        file_experiment_assets = [asset['filename'] for asset in file_experiment.assets]
        experiment_assets = [asset.filename for asset in experiment.assets]
        self.assertEqual(set(file_experiment_assets), set(experiment_assets))

        # Test FileSimulation
        file_simulations = self.platform.get_children(experiment.id, item_type=ItemType.EXPERIMENT, raw=True)
        self.assertEqual(len(file_simulations), 9)
        for file_simulation in file_simulations:
            self.assertTrue(isinstance(file_simulation, FileSimulation))
            self.assertEqual(file_simulation.status.name, "CREATED")
            self.assertEqual(file_simulation.parent_id, file_experiment.id)

        file_simulation_assets = [asset['filename'] for asset in file_simulations[0].assets]
        simulation_assets = [asset.filename for asset in experiment.simulations[0].assets]
        self.assertEqual(set(file_simulation_assets), set(simulation_assets))

    def test_get_directory_with_suite(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        suite: Suite = experiment.parent
        file_suite: FileSuite = suite.get_platform_object()
        # verify get_directory for server suite (file_suite)
        self.assertEqual(self.platform.get_directory(file_suite), file_suite.get_directory())
        self.assertEqual(self.platform.directory(file_suite), self.platform.get_directory(file_suite))
        # verify get_directory for local suite (idmtools suite)
        self.assertEqual(self.platform.directory(suite), suite.get_directory())
        self.assertEqual(self.platform.directory(suite), self.platform.get_directory(suite))

        self.assertEqual(self.platform.directory(suite), self.platform.get_directory(file_suite))

    def test_get_directory_with_exp(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        file_experiment = experiment.get_platform_object()
        # verify get_directory for server experiment (file_experiment)
        self.assertEqual(self.platform.get_directory(file_experiment), file_experiment.get_directory())
        self.assertEqual(self.platform.directory(file_experiment), self.platform.get_directory(file_experiment))
        # verify get_directory for local experiment (idmtools experiment)
        self.assertEqual(self.platform.directory(experiment), experiment.get_directory())
        self.assertEqual(self.platform.directory(experiment), self.platform.get_directory(experiment))

        self.assertEqual(self.platform.directory(experiment), self.platform.get_directory(file_experiment))

    def test_get_directory_with_sim(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        file_sim: FileSimulation = self.platform.get_item(experiment.simulations[0].id, item_type=ItemType.SIMULATION,
                                                          raw=True)
        # verify get_directory for server sim (file_sim)
        self.assertEqual(self.platform.directory(file_sim), self.platform.get_directory(file_sim))
        self.assertEqual(self.platform.directory(file_sim), file_sim.get_directory())
        idmtools_sim: Simulation = self.platform.get_item(experiment.simulations[0].id,
                                                              item_type=ItemType.SIMULATION,
                                                              raw=FALSE)
        # verify get_directory for local sim (idmtools sim)
        print(idmtools_sim.get_directory())
        self.assertEqual(self.platform.directory(idmtools_sim), self.platform.get_directory(idmtools_sim))
        self.assertEqual(self.platform.directory(idmtools_sim), idmtools_sim.get_directory())

        self.assertEqual(self.platform.directory(file_sim), self.platform.get_directory(idmtools_sim))

