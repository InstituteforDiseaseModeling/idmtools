import docker
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import restart_local_platform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


# Ensure Container is Running
class TestFirstTest(ITestWithPersistence):
    @restart_local_platform(stop_after=False, **get_test_local_env_overrides())
    def test_start_everything(self):
        client = docker.from_env()
        sm = DockerServiceManager(client, **get_test_local_env_overrides())
        sm.create_services()