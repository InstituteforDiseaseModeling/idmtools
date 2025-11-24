import io
import os
import sys
import unittest
from functools import partial
from time import time
from typing import Any, Dict
import pytest
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
class TestFilePlatform(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.job_directory = "DEST"
        self.platform = Platform('FILE', job_directory=self.job_directory)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_assetcollection_hook(self, mock_stdout):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        task.python_path = "python3"

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(3))
        ts.add_builder(builder)

        # Now we can create our Experiment using our template builder
        experiment = Experiment.from_template(ts, name=self.case_name)
        # Add our own custom tag to simulation
        experiment.tags["tag1"] = 1
        # And add common assets from local dir
        experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

        # Create suite
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        ran_at = str(time())
        sys.stdout = mock_stdout

        def add_pre_creation_hook(item: AssetCollection, platform: 'FILEPlatform'):
            print("hello add_pre_creation_hook! succeeded = " + str(item.succeeded))

        def add_post_creation_hook(item: AssetCollection, platform: 'FILEPlatform'):
            print("hello add_post_creation_hook! succeeded = " + str(item.status))

        experiment.assets.add_pre_creation_hook(add_pre_creation_hook)
        experiment.assets.add_post_creation_hook(add_post_creation_hook)

        def add_sim_pre_creation_hook(item: AssetCollection, platform: 'FILEPlatform'):
            print("hello add_sim_pre_creation_hook! succeeded = " + str(item.succeeded))

        def add_sim_post_creation_hook(item: AssetCollection, platform: 'FILEPlatform'):
            print("hello add_sim_post_creation_hook! succeeded = " + str(item.status))

        base_sim = experiment.simulations.items.base_simulation
        base_sim.assets.add_pre_creation_hook(add_sim_pre_creation_hook)
        base_sim.assets.add_post_creation_hook(add_sim_post_creation_hook)
        if sys.platform == 'win32' and sys.version_info < (3, 8):
                with self.assertRaises(OSError) as ex:
                    suite.run(platform=self.platform, wait_until_done=False, retries=2)
                self.assertTrue(ex.exception.args[0], "symbolic link privilege not held")
                return
        else:
            suite.run(platform=self.platform, wait_until_done=False, retries=2)
        stdout = mock_stdout.getvalue()
        self.assertTrue("hello add_pre_creation_hook! succeeded = False" in stdout)
        self.assertTrue("hello add_post_creation_hook! succeeded = EntityStatus.CREATED" in stdout)
        self.assertTrue("hello add_sim_pre_creation_hook! succeeded = False" in stdout)
        self.assertTrue("hello add_sim_post_creation_hook! succeeded = EntityStatus.CREATED" in stdout)
