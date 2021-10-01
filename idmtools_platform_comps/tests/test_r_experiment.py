import allure
import os
import sys
import pytest
from idmtools_models.r.json_r_task import JSONConfiguredRTask
from idmtools_test import COMMON_INPUT_PATH

from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.assets import AssetCollection
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name


@pytest.mark.tasks
@pytest.mark.r
@allure.story("COMPS")
@allure.story("RTask")
@allure.suite("idmtools_platform_comps")
class TestRExperiment(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('COMPS2')
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        self.input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    def validate_common_assets(self, fpath, task):
        """
        Validate common assets on a R task

        Args:
            fpath: Source path to model file
            task: Task object to validate

        Returns:
            None
        """
        self.assertEqual(len(task.common_assets.assets), 1, f'Asset list is: {[str(x) for x in task.common_assets.assets]}')
        self.assertEqual(task.common_assets.assets[0].absolute_path, fpath)

    @pytest.mark.skip
    def test_json_r_static_filename_no_argument_commission(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis", "individual_dynamics_estimates",
                             "estimate_incubation_period.R")
        # task = JSONConfiguredRTask(script_name=fpath, configfile_argument=None, image_name='r-base:3.6.1')
        command = "RScript ./Assets/estimate_incubation_period.R"
        task = CommandTask(command=command)

        task.gather_all_assets()

        # self.assertEqual(str(task.command), f'Rscript ./Assets/estimate_incubation_period.R')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

        ac_lib_path = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis")

        # Create AssetCollection from dir to provide to the Experiment task
        r_model_assets = AssetCollection.from_directory(assets_directory=ac_lib_path, flatten=False, relative_path="ncov_analysis")

        experiment = Experiment.from_task(task, name="test_r_task.py--test_r_model_with_ac",
                                          assets=r_model_assets)

        platform = Platform('HPC_LINUX')
        experiment.run(wait_until_done=True)

        # Check experiment status, only move to Analyzer step if experiment succeeded.
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            sys.exit(-1)

    @pytest.mark.skip
    def test_r_model_w_ac_no_args(self):
        fpath = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis", "individual_dynamics_estimates",
                             "estimate_incubation_period.R")
        task = JSONConfiguredRTask(script_name=fpath, configfile_argument=None, image_name='r-base:3.6.1')
        task.gather_all_assets()

        self.assertEqual(str(task.command),
                         f'Rscript ./Assets/estimate_incubation_period.R')
        self.validate_common_assets(fpath, task)
        self.validate_json_transient_assets(task)

        ac_lib_path = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis")

        # Create AssetCollection from dir to provide to the Experiment task
        ncov_analysis_assets = AssetCollection.from_directory(assets_directory=ac_lib_path, flatten=False,
                                                              relative_path="ncov_analysis")

        experiment = Experiment.from_task(task, name="test_r_task.py--test_r_model_with_ac",
                                          assets=ncov_analysis_assets)

        platform = Platform('HPC_LINUX')
        experiment.run(wait_until_done=True)


        # Check experiment status, only move to Analyzer step if experiment succeeded.
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            sys.exit(-1)

    @pytest.mark.skip
    def test_r_model_with_load_ac(self):
        # Utility does not support R libraries only Python packages at this time
        platform = Platform('COMPS2')

        ac_lib_path = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis")

        # Create AssetCollection from dir to provide to the Experiment task
        ncov_analysis_assets = AssetCollection.from_directory(assets_directory=ac_lib_path, flatten=False,
                                                              relative_path="ncov_analysis")

        command = "RScript Assets/ncov_analysis/individual_dynamics_estimates/estimate_incubation_period.R"
        task = CommandTask(command=command)

        # model_asset = os.path.join(COMMON_INPUT_PATH, "r", "ncov_analysis", "individual_dynamics_estimates",
        #                            "estimate_incubation_period.R")

        # task = JSONConfiguredRTask(script_name=fpath, configfile_argument=None, common_assets=ncov_analysis_assets)

        experiment = Experiment.from_task(task, name="test_r_task.py--test_r_model_with_ac",
                                          assets=ncov_analysis_assets)
        # experiment.assets.add_directory(ac_lib_path)
        experiment.run(wait_until_done=True)

        # Check experiment status, only move to Analyzer step if experiment succeeded.
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            sys.exit(-1)
