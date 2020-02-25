# flake8: noqa E402
import json
import os
from abc import ABC, abstractmethod
from functools import partial
import sys

current_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_directory)

import pytest
from idmtools.builders import SimulationBuilder, StandAloneSimulationsBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.iplatform import IPlatform
from idmtools.managers import ExperimentManager
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.emod_experiment import EMODExperiment, IEMODExperiment
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import sims_from_experiment, get_simulation_path
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


@pytest.mark.emod
class EMODPlatformTest(ABC):

    @classmethod
    @abstractmethod
    def get_emod_experiment(cls, ) -> IEMODExperiment:
        pass

    @classmethod
    @abstractmethod
    def get_emod_binary(cls, ) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_platform(cls) -> IPlatform:
        pass

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    @pytest.mark.long
    def test_serialization(self):
        # Step1: create experiment and simulation with serialization file in output
        from config_update_parameters import config_update_params
        BIN_PATH = os.path.join(COMMON_INPUT_PATH, "serialization")

        sim_duration = 2  # in years
        num_seeds = 1
        e1 = EMODExperiment.from_default(self.case_name + " create serialization", default=EMODSir(),
                                         eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
        e1.demographics.clear()
        demo_file = os.path.join(COMMON_INPUT_PATH, "serialization", "single_node_demographics.json")
        e1.demographics.add_demographics_from_file(demo_file)

        simulation = e1.base_simulation

        # Update bunch of config parameters
        sim = config_update_params(simulation)
        timesteps = [sim_duration * 365]
        add_serialization_timesteps(simulation=sim, timesteps=[sim_duration * 365],
                                    end_at_final=False, use_absolute_times=False)

        start_day = sim.get_parameter("Start_Time")
        last_serialization_day = sorted(timesteps)[-1]
        end_day = start_day + last_serialization_day
        sim.set_parameter("Simulation_Duration", end_day)

        sim.tags = {'role': 'serializer', 'idmtools': 'single serialization test'}

        builder = SimulationBuilder()
        set_Run_Number = partial(param_update, param="Run_Number")
        builder.add_sweep_definition(set_Run_Number, range(num_seeds))
        e1.tags = {'idmtools': 'create serialization', 'exp1': 'tag1'}

        e1.builder = builder
        em = ExperimentManager(experiment=e1, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(e1.succeeded)

        # ---------------------------------------------------------------------------------------------
        # Step2: Create new experiment and sim with previous serialized file
        # TODO, ideally we could add new sim to existing exp, but currently we can not do with issue #459

        # First get previous serialized file path
        comps_exp = self.platform.get_item(item_id=e1.uid, item_type=ItemType.EXPERIMENT)
        comps_sims = sims_from_experiment(comps_exp)
        serialized_file_path = [get_simulation_path(sim) for sim in comps_sims][0]

        # create new experiment
        e2 = EMODExperiment.from_default(self.case_name + " realod serialization", default=EMODSir(),
                                         eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
        e2.demographics.clear()
        demo_file = os.path.join(COMMON_INPUT_PATH, "serialization", "single_node_demographics.json")
        e2.demographics.add_demographics_from_file(demo_file)
        e2.tags = {'idmtools': 'reload serialization', 'exp2': 'tag2'}

        reload_sim = e2.simulation()
        reload_sim.tags = {'role': 'reloader', 'idmtools': 'single serialization test'}
        # reload_sim.config.pop('Serialization_Time_Steps') # Need this step if we use same exp
        reload_sim.set_parameter("Config_Name", "reloading sim")
        reload_sim.set_parameter("Simulation_Duration", sim_duration * 365)
        load_serialized_population(simulation=reload_sim, population_path=os.path.join(serialized_file_path, 'output'),
                                   population_filenames=['state-00730.dtk'])

        b = StandAloneSimulationsBuilder()
        b.add_simulation(reload_sim)
        e2.builder = b
        # Ideally we do not need to create another ExperimentManager if we can use same experiment
        em2 = ExperimentManager(experiment=e2, platform=self.platform)
        em2.run()
        em2.wait_till_done()

        # validation to make sure reload sim has same channel as serlized sim and same timesteps
        from idmtools.analysis.download_analyzer import DownloadAnalyzer
        from idmtools.analysis.analyze_manager import AnalyzeManager

        filenames = ['output/InsetChart.json', 'output/state-00730.dtk']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='serialized_file_download')]
        exp_id = [(e1.uid, ItemType.EXPERIMENT)]
        manager = AnalyzeManager(platform=self.platform, ids=exp_id, analyzers=analyzers)
        manager.analyze()

        filenames = ['output/InsetChart.json']
        analyzers = [DownloadAnalyzer(filenames=filenames, output_path='reload_sim_download')]
        exp_id = [(e2.uid, ItemType.EXPERIMENT)]
        manager = AnalyzeManager(platform=self.platform, ids=exp_id, analyzers=analyzers)
        manager.analyze()

        reload_comps_exp = self.platform.get_item(item_id=e2.uid, item_type=ItemType.EXPERIMENT)
        reload_comps_sims = sims_from_experiment(reload_comps_exp)

        serialized_sim_chart_path = os.path.join('serialized_file_download', str(comps_sims[0].id), 'InsetChart.json')
        serialized_sim_dtkfile_path = os.path.join('serialized_file_download', str(comps_sims[0].id), 'state-00730.dtk')
        reload_sim_chart_path = os.path.join('reload_sim_download', str(reload_comps_sims[0].id), 'InsetChart.json')

        self.assertTrue(os.path.exists(serialized_sim_chart_path))
        self.assertTrue(os.path.exists(serialized_sim_dtkfile_path))
        self.assertTrue(os.path.exists(reload_sim_chart_path))

        with open(serialized_sim_chart_path) as infile:
            serialized_chart = json.load(infile)
        with open(reload_sim_chart_path) as infil1e1:
            reloaded_chart = json.load(infil1e1)

        # make sure they have same keys
        serialized_keys = sorted(serialized_chart['Channels'].keys())
        reload_keys = sorted(reloaded_chart['Channels'].keys())
        self.assertEqual(len(serialized_keys), len(reload_keys))

        for key in serialized_keys:
            self.assertTrue(key in reload_keys)

        # make sure timestamps are the same for these 2 sims
        serialized_channel_length = len(serialized_chart['Channels']['Infected']['Data'])
        reload_channel_length = len(reloaded_chart['Channels']['Infected']['Data'])
        self.assertEqual(serialized_channel_length, reload_channel_length)
        self.assertEqual(serialized_channel_length, 730)


@pytest.mark.comps
@pytest.mark.emod
class TestCompsEMOOD(ITestWithPersistence, EMODPlatformTest):

    @classmethod
    def setUpClass(cls):
        cls.platform: IPlatform = cls.get_platform()

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    @classmethod
    def get_emod_experiment(cls) -> IEMODExperiment:
        return EMODExperiment

    @classmethod
    def get_platform(cls) -> IPlatform:
        return Platform('COMPS')

    @classmethod
    def get_emod_binary(cls, ) -> str:
        return os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")
