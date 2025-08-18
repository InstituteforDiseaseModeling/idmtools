import os
import pathlib
import shutil
from idmtools.core import ItemType


def remove_dir(self):
    if os.path.exists(self.job_directory):
        shutil.rmtree(self.job_directory)


def get_dirs_and_files(self,dir):
    file_res = []
    dir_res = []
    # iterate directory
    for entry in dir.iterdir():
        if entry.is_file():
            file_res.append(entry)
        elif entry.is_dir():
            dir_res.append(entry)

    return dir_res, file_res


def verify_result(self, suite):
    experiments = self.platform.get_children(suite.id, item_type=ItemType.SUITE)
    experiment = experiments[0]
    suite_dir = str(self.platform.get_directory(suite))
    exp_dir = str(self.platform.get_directory(experiment))
    suite_sub_dirs, suite_files = get_dirs_and_files(self, pathlib.Path(suite_dir))
    # Verify all files under suite
    self.assertTrue(len(suite_files) == 1)
    self.assertEqual(suite_files[0], pathlib.Path(suite_dir + "/metadata.json"))
    # Verify all sub directories under suite
    self.assertTrue(len(suite_sub_dirs) == 0)

    for experiment in suite.experiments:
        experiment_dir = self.platform.get_directory(experiment)
        experiment_sub_dirs, experiment_files = get_dirs_and_files(self, experiment_dir)
        # Verify all files under experiment
        self.assertTrue(len(experiment_files) == 4)
        experiment_path_prefix = exp_dir + "/"
        expected_files = set([pathlib.Path(experiment_path_prefix + "metadata.json"),
                              pathlib.Path(experiment_path_prefix + "run_simulation.sh"),
                              pathlib.Path(experiment_path_prefix + "sbatch.sh"),
                              pathlib.Path(experiment_path_prefix + "batch.sh")])
        self.assertSetEqual(set(experiment_files), expected_files)
        # Verify all sub directories under experiment
        self.assertTrue(len(experiment_sub_dirs) == 2)
        self.assertSetEqual(set(experiment_sub_dirs),
                            set([pathlib.Path(exp_dir + "/" + experiment.simulations[0].id),
                                 pathlib.Path(experiment_path_prefix + "Assets")]))
