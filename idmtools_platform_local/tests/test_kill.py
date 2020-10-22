import os

import allure
import pytest

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.templated_script_task import TemplatedScriptTask
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import ensure_local_platform_running
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


# this is a test script that is meant for devs, not test. It allows us to quickly test the kill functionality

@pytest.mark.skip
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

    @pytest.mark.long
    @pytest.mark.timeout(300)
    @ensure_local_platform_running(silent=True, **get_test_local_env_overrides())
    def test_kill_long(self, platform):
        task = TemplatedScriptTask(script_path="abc.sh:", template="""#!/usr/bin/env bash
        sleep 80
""")
        experiment = Experiment.from_task(task)
        experiment.run(wait_until_done=True, platform=platform)
