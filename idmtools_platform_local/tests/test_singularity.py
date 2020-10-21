import allure
import pytest
from idmtools.entities.experiment import Experiment
from idmtools_models.templated_script_task import TemplatedScriptTask
from idmtools_test.utils.confg_local_runner_test import get_test_local_env_overrides
from idmtools_test.utils.decorators import ensure_local_platform_running
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


defaults = get_test_local_env_overrides()
defaults['enable_singularity_support'] = True


@pytest.mark.docker
@pytest.mark.python
@pytest.mark.serial
@allure.story("LocalPlatform")
@allure.story("Singularity")
@allure.suite("idmtools_platform_local")
class TestSingularity(ITestWithPersistence):
    @pytest.mark.long
    @pytest.mark.timeout(90)
    @ensure_local_platform_running(silent=True, **defaults)
    def test_singularity_hello_world(self, platform):
        task = TemplatedScriptTask(script_path="hello.sh", template="""#!/usr/bin/env bash
singularity pull --name hello.simg docker://alpine
sleep 1
dir
singularity exec ./hello.simg ls -l
""")
        experiment = Experiment.from_task(task)
        experiment.run(wait_on_done=True, platform=platform)
        self.assertTrue(experiment.succeeded)
