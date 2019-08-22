import os
from importlib import reload

import pytest

from idmtools.core import PlatformFactory, EntityStatus
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_platform_local.docker.DockerOperations import DockerOperations
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test.utils.confg_local_runner_test import reset_local_broker, get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform


@pytest.mark.docker
class TestPlatformSimulations(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        reset_local_broker()
        from idmtools_platform_local.workers.brokers import setup_broker
        setup_broker()
        # ensure we start from no environment
        dm = DockerOperations()
        dm.cleanup(True)

        import idmtools_platform_local.tasks.create_experiement
        import idmtools_platform_local.tasks.create_simulation
        reload(idmtools_platform_local.tasks.create_experiement)
        reload(idmtools_platform_local.tasks.create_simulation)

    @restart_local_platform(silent=True, **get_test_local_env_overrides())
    def test_fetch_simulation_files(self):
        platform = PlatformFactory.create_from_block('Local_Staging')

        pe = PythonExperiment(name=self.case_name, model_path=os.path.join(COMMON_INPUT_PATH, "python",
                                                                           "realpath_verify.py"))

        pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        em = ExperimentManager(experiment=pe, platform=platform)
        em.run()
        em.wait_till_done()

        self.assertTrue(all([s.status == EntityStatus.FAILED for s in pe.simulations]))
