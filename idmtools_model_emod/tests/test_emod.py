import json
import os
from abc import ABC, abstractmethod

import pytest

from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import IPlatform
from idmtools.managers import ExperimentManager
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.emod_model import EMODExperiment, DockerEMODExperiment, IEMODExperiment
from idmtools_model_emod.utils import get_github_eradication_url
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(COMMON_INPUT_PATH, "files", "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(COMMON_INPUT_PATH, "files", "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(COMMON_INPUT_PATH, "files", "demographics.json")
DEFAULT_ERADICATION_PATH = os.path.join(COMMON_INPUT_PATH, "emod", "Eradication.exe")

emod_version = '2.20.0'


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
    def test_sir_with_StandAloneSimulationsBuilder(self):
        e = self.get_emod_experiment().from_default(self.case_name, default=EMODSir(),
                                                    eradication_path=self.get_emod_binary())

        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        sim = e.simulation()
        sim.set_parameter("Enable_Immunity", 0)
        b = StandAloneSimulationsBuilder()
        b.add_simulation(sim)
        e.builder = b

        em = ExperimentManager(experiment=e, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        # get the files in a platform agnostic way
        for sim in e.simulations:
            files = self.platform.get_files(sim, ["config.json"])
            config_parameters = json.loads(files["config.json"])['parameters']
            self.assertEqual(config_parameters["Enable_Immunity"], 0)

    @pytest.mark.long
    def test_sir_with_ExperimentBuilder(self):
        e = self.get_emod_experiment().from_default(self.case_name, default=EMODSir(),
                                                    eradication_path=self.get_emod_binary())
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        builder.add_sweep_definition(param_a_update, range(0, 2))
        e.builder = builder
        em = ExperimentManager(experiment=e, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        run_number = 0
        for sim in e.simulations:
            files = self.platform.get_files(sim, ["config.json"])
            config_parameters = json.loads(files["config.json"])['parameters']
            self.assertEqual(config_parameters["Enable_Immunity"], 0)
            self.assertEqual(config_parameters["Run_Number"], run_number)
            run_number = run_number + 1

    @pytest.mark.long
    def test_batch_simulations_StandAloneSimulationsBuilder(self):
        e = self.get_emod_experiment().from_default(self.case_name, default=EMODSir(),
                                                    eradication_path=self.get_emod_binary())
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        b = StandAloneSimulationsBuilder()

        for i in range(20):
            sim = e.simulation()
            sim.set_parameter("Enable_Immunity", 0)
            b.add_simulation(sim)

        e.builder = b

        em = ExperimentManager(experiment=e, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)
        for sim in e.simulations:
            files = self.platform.get_files(sim, ["config.json"])
            config_parameters = json.loads(files["config.json"])['parameters']
            self.assertEqual(config_parameters["Enable_Immunity"], 0)

    @pytest.mark.long
    def test_batch_simulations_ExperimentBuilder(self):
        e = self.get_emod_experiment().from_default(self.case_name, default=EMODSir(),
                                                    eradication_path=self.get_emod_binary())
        e.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        # s = Suite(name="test suite")
        # s.experiments.append(e)
        e.base_simulation.set_parameter("Enable_Immunity", 0)

        def param_a_update(simulation, value):
            simulation.set_parameter("Run_Number", value)
            return {"Run_Number": value}

        builder = ExperimentBuilder()
        # Sweep parameter "Run_Number"
        builder.add_sweep_definition(param_a_update, range(0, 20))
        e.builder = builder
        em = ExperimentManager(experiment=e, platform=self.platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(e.succeeded)

    def test_duplicated_eradication(self):
        """
        Eradication is in the collection but also specified in the eradication_path.
        We should only end up with one copy of Eradication, being at the root of the collection.
        The exe/Eradication should be discarded.
        """
        from idmtools.assets import AssetCollection
        duplicated_model_path = os.path.join(COMMON_INPUT_PATH, "duplicated_model")
        asset_collection = AssetCollection()
        asset_collection.add_directory(assets_directory=duplicated_model_path)
        experiment = EMODExperiment(name="test",
                                    eradication_path=os.path.join(duplicated_model_path, "exe", "Eradication"))
        experiment.add_assets(asset_collection)
        experiment.pre_creation()

        # Check that we only have 2 assets
        self.assertEqual(2, len(experiment.assets.assets))
        # Check that Eradication is at the root and the one in exe/ not present
        exe_eradication = experiment.assets.get_one(filename="Eradication")
        self.assertEqual("", exe_eradication.relative_path)
        self.assertEqual("Eradication", exe_eradication.filename)
        self.assertEqual(os.path.join(duplicated_model_path, "exe", "Eradication"), exe_eradication.absolute_path)


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


@pytest.mark.docker
@pytest.mark.emod
class TestLocalPlatformEMOD(ITestWithPersistence, EMODPlatformTest):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    @classmethod
    def setUpClass(cls) -> None:
        from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager
        from idmtools_platform_local.infrastructure.docker_io import DockerIO
        import docker
        cls.do = DockerIO()
        cls.sdm = DockerServiceManager(docker.from_env())
        cls.sdm.cleanup(True, True)
        cls.do.cleanup(True)
        cls.platform: IPlatform = cls.get_platform()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.sdm.cleanup(True, True)
        cls.do.cleanup(True)

    @classmethod
    def get_emod_experiment(cls, ) -> IEMODExperiment:
        return DockerEMODExperiment

    @classmethod
    def get_platform(cls) -> IPlatform:
        return Platform('Local')

    @classmethod
    def get_emod_binary(cls, ) -> str:
        return get_github_eradication_url(emod_version)
