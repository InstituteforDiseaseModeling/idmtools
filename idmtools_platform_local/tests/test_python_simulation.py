from importlib import reload

import pytest

from idmtools_platform_local.docker.DockerOperations import DockerOperations
from operator import itemgetter
from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools.core import EntityStatus, PlatformFactory
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
import os

from idmtools_test.utils.confg_local_runner_test import reset_local_broker, get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform


@pytest.mark.docker
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        reset_local_broker()
        from idmtools_platform_local.workers.brokers import setup_broker
        setup_broker()
        # ensure we start from no environment
        dm = DockerOperations()
        dm.cleanup(True)

        import idmtools_platform_local.tasks.create_experiment
        import idmtools_platform_local.tasks.create_simulation
        reload(idmtools_platform_local.tasks.create_experiment)
        reload(idmtools_platform_local.tasks.create_simulation)

    @restart_local_platform(silent=True, **get_test_local_env_overrides())
    def test_direct_sweep_one_parameter_local(self):

        platform = PlatformFactory.create_from_block('Local_Staging')

        # CreateSimulationTask.broker =

        name = self.case_name
        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        pe.builder = builder

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in pe.simulations]))
        # validation
        self.assertEqual(pe.name, name)
        self.assertEqual(pe.simulation_count, 5)
        self.assertIsNotNone(pe.uid)
        self.assertTrue(all([s.status == EntityStatus.FAILED for s in pe.simulations]))
        self.assertFalse(pe.succeeded)

        # validate tags
        tags = []
        for simulation in pe.simulations:
            self.assertEqual(simulation.experiment.uid, pe.uid)
            tags.append(simulation.tags)
        expected_tags = [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)

    def test_add_prefixed_relative_path_to_assets_local(self):
        from idmtools.core import PlatformFactory, EntityStatus
        # platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")
        platform = PlatformFactory.create_from_block('Local_Staging')
        model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
        ac = AssetCollection()
        assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets", "MyExternalLibrary")
        ac.add_directory(assets_directory=assets_path, relative_path="MyExternalLibrary")
        # assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
        # ac.add_directory(assets_directory=assets_path)
        pe = PythonExperiment(name=self.case_name, model_path=model_path, assets=ac)
        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        pe.base_simulation.envelope = "parameters"

        pe.base_simulation.set_parameter("b", 10)
        pe.base_simulation.envelope = "parameters"

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 2))
        pe.builder = builder
        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()
        self.assertTrue(all([s.status == EntityStatus.SUCCEEDED for s in pe.simulations]))
