import docker
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

# This is so local platform is stopped at end. It is named so it is picked up last


class TestLastTest(ITestWithPersistence):
    def test_stop_everything(self):
        client = docker.from_env()
        sm = DockerServiceManager(client, **get_test_local_env_overrides())
        sm = DockerServiceManager(client, **get_test_local_env_overrides())
        sm.cleanup(True)
        sm.stop_services()
