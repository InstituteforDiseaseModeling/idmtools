import os

import allure
import pytest

from COMPS.Data import Simulation as COMPSSimulation, QueryCriteria

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.linux_mounts import get_workdir_from_simulations
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name

current_directory = os.path.dirname(os.path.realpath(__file__))


@allure.suite("idmtools_platform_comps")
class TestCreateSimDirectoryMap(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)

    # test create_sim_directory_map from platform for experiment for windows platform
    def test_create_sim_directory_map_bayesian(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2 experiment id in bayesian
        platform = Platform('Bayesian')
        workdir_dict = platform.create_sim_directory_map(item_id=exp_id, item_type=ItemType.EXPERIMENT)
        comps_exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        comps_sims = comps_exp.get_simulations(QueryCriteria().select_children('hpc_jobs'))
        for comps_sim in comps_sims:
            self.assertEquals(workdir_dict[str(comps_sim.id)], comps_sim.hpc_jobs[0].working_directory)
            self.assertTrue(workdir_dict[str(comps_sim.id)].replace("\\", "/").startswith(
                r"//internal.idm.ctr/IDM-Test/home/idmtools_bamboo/output/test_python_experiment.py"))

    # test create_sim_directory_map from platform for experiment for comps's slurm platform
    def test_create_sim_directory_map_slurm(self):
        exp_id = 'b77793f1-d132-ed11-92ee-f0921c167860'  # comps2 experiment id in slurmstage
        platform = Platform('SlurmStage')
        workdir_dict = platform.create_sim_directory_map(item_id=exp_id, item_type=ItemType.EXPERIMENT)
        comps_exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        comps_sims = comps_exp.get_simulations(QueryCriteria().select_children('hpc_jobs'))
        for comps_sim in comps_sims:
            self.assertEquals(workdir_dict[str(comps_sim.id)], comps_sim.hpc_jobs[0].working_directory)
            self.assertTrue(workdir_dict[str(comps_sim.id)].startswith(
                r"/mnt/idm/home/shchen/output/20220801_emodpy_megatrends_sensitiv_20220912_193441/"))

    # test create_sim_directory_map from platform for simulation for windows platform
    def test_create_sim_directory_map_bayesian_sim(self):
        sim_id = '6fcab2fe-a252-ea11-a2bf-f0921c167862'  # comps2 simulation id in bayesian
        platform = Platform('Bayesian')
        workdir_dict = platform.create_sim_directory_map(item_id=sim_id, item_type=ItemType.SIMULATION)
        comps_sim = COMPSSimulation.get(sim_id, QueryCriteria().select_children('hpc_jobs'))
        self.assertEquals(workdir_dict[sim_id], comps_sim.hpc_jobs[0].working_directory)
        self.assertTrue(workdir_dict[sim_id].replace("\\", "/").startswith(
            r"//internal.idm.ctr/IDM-Test/home/idmtools_bamboo/output/test_python_experiment.py"))

    # test create_sim_directory_map from platform for simulation for comps slurm platform
    def test_create_sim_directory_map_slurm_sim(self):
        sim_id = 'bb7793f1-d132-ed11-92ee-f0921c167860'  # comps2 simulation id in slurmstage
        platform = Platform('SlurmStage')
        workdir_dict = platform.create_sim_directory_map(item_id=sim_id, item_type=ItemType.SIMULATION)
        comps_sim = COMPSSimulation.get(sim_id, QueryCriteria().select_children('hpc_jobs'))
        self.assertEquals(workdir_dict[sim_id], comps_sim.hpc_jobs[0].working_directory)
        self.assertTrue(workdir_dict[sim_id].startswith(
            r"/mnt/idm/home/shchen/output/20220801_emodpy_megatrends_sensitiv_20220912_193441/"))

    # Test get_workdir_from_simulations from idmtools_platform_comps/utils, bayesian
    def test_get_workdir_from_simulations_bayesian(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2 experiment id in bayesian
        platform = Platform('Bayesian')
        comps_exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        comps_sims = comps_exp.get_simulations(QueryCriteria().select_children('hpc_jobs'))
        result_work_dir = get_workdir_from_simulations(platform, comps_simulations=comps_sims)
        for comps_sim in comps_sims:
            self.assertTrue(result_work_dir[str(comps_sim.id)].replace("\\", "/").startswith(
            r"//internal.idm.ctr/IDM-Test/home/idmtools_bamboo/output/test_python_experiment.py"))

    # Test get_workdir_from_simulations from idmtools_platform_comps/utils, slurmstage
    def test_get_workdir_from_simulations_slurm(self):
        exp_id = 'b77793f1-d132-ed11-92ee-f0921c167860'  # comps2 experiment id in SlurmStage
        platform = Platform('SlurmStage')
        comps_exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        comps_sims = comps_exp.get_simulations(QueryCriteria().select_children('hpc_jobs'))
        result_work_dir = get_workdir_from_simulations(platform, comps_simulations=comps_sims)
        for comps_sim in comps_sims:
            self.assertTrue(result_work_dir[str(comps_sim.id)].startswith(
                r"/mnt/idm/home/shchen/output/20220801_emodpy_megatrends_sensitiv_20220912_193441/"))

    # Test get_workdir_from_simulations from idmtools_platform_comps/utils, bayesian and no hpc_jobs query
    def test_get_workdir_from_simulations_bayesian_no_query_hpc(self):
        exp_id = '69cab2fe-a252-ea11-a2bf-f0921c167862'  # comps2 experiment id in bayesian
        platform = Platform('Bayesian')
        comps_exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        comps_sims = comps_exp.get_simulations()  # not query hpc_jobs, so there is no working_directory info returns
        result_work_dir = get_workdir_from_simulations(platform, comps_simulations=comps_sims)
        self.assertTrue(result_work_dir == {})

    # Test get_workdir_from_simulations from idmtools_platform_comps/utils, slurmstage and no hpc_jobs query
    def test_get_workdir_from_simulations_slurm_no_query_hpc(self):
        exp_id = 'b77793f1-d132-ed11-92ee-f0921c167860'  # comps2 experiment id in SlurmStage
        platform = Platform('SlurmStage')
        comps_exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=True)
        comps_sims = comps_exp.get_simulations()  # not query hpc_jobs, so there is no working_directory info returns
        result_work_dir = get_workdir_from_simulations(platform, comps_simulations=comps_sims)
        self.assertTrue(result_work_dir == {})

