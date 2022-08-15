import json
import os
import pathlib
import shutil
from functools import partial
from typing import Any, Dict

import pytest

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
@linux_only
class TestPythonSimulation(ITestWithPersistence):

    def create_experiment(self, platform=None, a=1, b=1, max_running_jobs=None, retries=None, wait_until_done=False, dry_run=True):
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
        # change dry_run=False when run in slurm cluster
        suite.run(platform=platform, wait_until_done=False, wait_on_done=wait_until_done, max_running_jobs=max_running_jobs,
                  retries=retries, dry_run=dry_run)
        print("suite_id: " + suite.id)
        print("experiment_id: " + experiment.id)
        return experiment

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.job_directory = "DEST"
        self.platform = Platform('SLURM_LOCAL', job_directory=self.job_directory)

    def tearDown(self):
        shutil.rmtree(self.job_directory)

    def test_sweeping_and_local_folders_creation(self):
        experiment = self.create_experiment(self.platform, a=3, b=3)
        experiment_dir = self.platform._op_client.get_directory(experiment)
        files = []
        for (dirpath, dirnames, filenames) in os.walk(experiment_dir):
            files.extend(filenames)
            break
        self.assertSetEqual(set(files), set(["metadata.json", "run_simulation.sh", "sbatch.sh"]))

        # verify all files under simulations
        self.assertEqual(experiment.simulation_count, 9)
        count = 0
        for simulation in experiment.simulations:
            simulation_dir = self.platform._op_client.get_directory(simulation)
            asserts_dir = simulation_dir.joinpath("Assets")
            files = []
            for (dirpath, dirnames, filenames) in os.walk(simulation_dir):
                if dirnames == ["Assets"]:
                    # verify Assets folder under simulation is symlink and it link to experiment's Assets
                    self.assertTrue(os.path.islink(asserts_dir))
                    target_link = os.readlink(asserts_dir)
                    self.assertEqual(os.path.basename(pathlib.Path(target_link).parent), experiment.id)
                    count = count + 1
                files.extend(filenames)
            self.assertSetEqual(set(files), set(["metadata.json", "_run.sh", "config.json"]))
        self.assertEqual(count, 9)  # make sure we found total 9 symlinks for Assets folder

    def test_scripts(self):
        platform = Platform('SLURM_LOCAL', job_directory=self.job_directory, max_running_jobs=8, retries=5)
        experiment = self.create_experiment(platform=platform, a=5, b=5)
        experiment_dir = self.platform._op_client.get_directory(experiment)
        # verify sbatch.sh script content in experiment level
        with open(os.path.join(experiment_dir, 'sbatch.sh'), 'r') as fpr:
            contents = fpr.read()
        self.assertIn("#SBATCH --array=1-25%8", contents)  # 25=a*b=5*5, 8=max_running_jobs
        self.assertIn("echo $SLURM_ARRAY_JOB_ID > job_id.txt", contents)
        self.assertIn("srun run_simulation.sh", contents)

        # verify run_simulation.sh script content in experiment level
        with open(os.path.join(experiment_dir, 'run_simulation.sh'), 'r') as fpr:
            contents = fpr.read()
        self.assertIn(
            "JOB_DIRECTORY=$(find . -type d -maxdepth 1 -mindepth 1  | grep -v Assets | head -${SLURM_ARRAY_TASK_ID} | tail -1)",
            contents)
        self.assertIn("JOB_DIRECTORY", contents)
        self.assertIn("bash _run.sh 1> stdout.txt 2> stderr.txt", contents)

        # verify _run.sh script content under simulation level
        simulation_ids = []
        for simulation in experiment.simulations:
            simulation_ids.append(simulation.id)
            simulation_dir = platform._op_client.get_directory(simulation)
            with open(os.path.join(simulation_dir, '_run.sh'), 'r') as fpr:
                contents = fpr.read()
            self.assertIn("until [ \"$n\" -ge 5 ]", contents)  # 5 here is from retries=5 in platform
            self.assertIn("python3 Assets/model3.py --config config.json", contents)

        # verify ids in metadata.json  for suite
        suite = experiment.suite
        suite_dir = platform._op_client.get_directory(suite)
        with open(os.path.join(suite_dir, 'metadata.json'), 'r') as j:
            contents = json.loads(j.read())
            self.assertEqual(contents['_uid'], suite.id)
            self.assertEqual(contents['experiments'][0], experiment.id)

        # verify ids in metadata.json for experiment
        with open(os.path.join(experiment_dir, 'metadata.json'), 'r') as j:
            contents = json.loads(j.read())
            self.assertEqual(contents['_uid'], experiment.id)
            self.assertEqual(contents['parent_id'], suite.id)
            self.assertEqual(set(contents['simulations']), set(simulation_ids))

        # verify ids in metadata.json for simulation, also verify sweep parameter in config.json file
        for simulation in experiment.simulations:
            simulation_dir = platform._op_client.get_directory(simulation)
            with open(os.path.join(simulation_dir, 'metadata.json'), 'r') as j:
                contents = json.loads(j.read())
                self.assertEqual(contents['_uid'], simulation.id)
                self.assertEqual(contents['parent_id'], experiment.id)
                self.assertEqual(contents['task']['command'], 'python3 Assets/model3.py --config config.json')
                with open(os.path.join(simulation_dir, 'config.json'), 'r') as j:
                    config_contents = json.loads(j.read())
                self.assertDictEqual(contents['task']['parameters'],  config_contents['parameters'])

    #@pytest.mark.skip("unskip this line when doing real run in local")
    def test_std_status_jobid_files(self):
        experiment = self.create_experiment(self.platform, a=3, b=3, wait_until_done=True, dry_run=False)
        experiment_dir = self.platform._op_client.get_directory(experiment)
        self.assertTrue(os.path.exists(os.path.join(experiment_dir, "job_id.txt")))
        job_id = open(os.path.join(experiment_dir, 'job_id.txt'), 'r').read().strip()
        self.assertTrue(len(job_id) > 0)
        for simulation in experiment.simulations:
            simulation_dir = self.platform._op_client.get_directory(simulation)
            status_file = os.path.join(simulation_dir, "job_status.txt")
            self.assertTrue(os.path.exists(status_file))
            status = open(status_file, 'r').read().strip()
            self.assertEqual(int(status), 0)
