from functools import partial

import allure
import os

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_slurm.platform_operations.utils import add_dummy_suite
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.utils import get_case_name

current_directory = os.path.dirname(os.path.realpath(__file__))
setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")


@allure.story("Slurm")
@allure.suite("idmtools_platform_slurm")
class TestCreateSimDirectoryMap(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = get_case_name(os.path.basename(__file__) + "--" + self._testMethodName)
        print(self.case_name)
        self.job_directory = 'DEST'
        self.platform = Platform('SLURM_LOCAL', job_directory=self.job_directory)
        self.suite, self.exp = self.create_experiment(self.platform)

    def create_experiment(self, platform=None):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, 'python', 'model1.py'),
                                        parameters=dict(c='c-value'))
        task.common_assets.add_asset('input/hello.sh')
        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()
        builder.add_sweep_definition(setA, range(0, 2))
        ts.add_builder(builder)
        exp = Experiment(name=self.case_name, simulations=ts, tags=dict(number_tag=123, KeyOnly=None))
        suite = add_dummy_suite(exp)
        suite.run(platform=platform, wait_until_done=False, wait_on_done=False, dry_run=True)
        return suite, exp

    # test create_sim_directory_map from platform for experiment
    def test_create_sim_directory_map(self):
        workdir_dict = self.platform.create_sim_directory_map(item_id=self.exp.id, item_type=ItemType.EXPERIMENT)
        experiment = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT)
        sims = experiment.simulations.items
        for sim in sims:
            self.assertEqual(workdir_dict[sim.id].replace("\\", "/"), f'DEST/{self.suite.id}/{self.exp.id}/{sim.id}')

    # test create_sim_directory_map from platform for simulation
    def test_create_sim_directory_map_sim(self):
        sims = self.platform.get_children(item_id=self.exp.id, item_type=ItemType.EXPERIMENT)
        workdir_dict = self.platform.create_sim_directory_map(item_id=sims[0].id, item_type=ItemType.SIMULATION)
        self.assertEqual(workdir_dict[sims[0].id].replace("\\", "/"), f'DEST/{self.suite.id}/{self.exp.id}/{sims[0].id}')

    # test create_sim_directory_map from platform for suite
    def test_create_sim_directory_map_suite(self):
        workdir_dict = self.platform.create_sim_directory_map(item_id=self.suite.id, item_type=ItemType.SUITE)
        experiment = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT)
        sims = experiment.simulations.items
        for sim in sims:
            self.assertEqual(workdir_dict[sim.id].replace("\\", "/"), f'DEST/{self.suite.id}/{self.exp.id}/{sim.id}')


