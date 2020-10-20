from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import ensure_local_platform_running
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


# Ensure Container is Running
class TestFirstTest(ITestWithPersistence):
    @ensure_local_platform_running(silent=True, **get_test_local_env_overrides())
    def test_start_everything(self, platform):
        pass
