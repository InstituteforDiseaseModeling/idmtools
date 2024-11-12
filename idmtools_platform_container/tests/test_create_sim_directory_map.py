from functools import partial
import allure
import os
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_file.platform_operations.utils import add_dummy_suite
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

current_directory = os.path.dirname(os.path.realpath(__file__))
setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")


@allure.story("Slurm")
@allure.suite("idmtools_platform_container")
class TestCreateSimDirectoryMap(ITestWithPersistence):

    @classmethod
    def setUpClass(cls) -> None:
        cls.job_directory = 'DEST'
        cls.platform = Platform('Container', job_directory=cls.job_directory)
        cls.suite, cls.exp = cls.create_experiment(cls.platform)

    def create_experiment(self, platform=None):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, 'python', 'model1.py'),
                                        parameters=dict(c='c-value'))
        task.common_assets.add_asset('inputs/run.sh')
        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()
        builder.add_sweep_definition(setA, range(0, 2))
        ts.add_builder(builder)
        exp = Experiment.from_template(ts, name="Test create sim map", tags=dict(number_tag=123, KeyOnly=None))
        suite = add_dummy_suite(exp)
        suite.run(platform=platform, wait_until_done=True)
        return suite, exp

    # test create_sim_directory_map from platform for experiment
    def test_create_sim_directory_map(self):
        workdir_dict = self.platform.create_sim_directory_map(item_id=self.exp.id, item_type=ItemType.EXPERIMENT)
        experiment = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT, raw=False)
        sims = experiment.simulations
        for sim in sims:
            self.assertEqual(workdir_dict[sim.id], str(self.platform.get_container_directory(sim)))

    # test create_sim_directory_map from platform for simulation
    def test_create_sim_directory_map_sim(self):
        sims = self.platform.get_children(item_id=self.exp.id, item_type=ItemType.EXPERIMENT)
        workdir_dict = self.platform.create_sim_directory_map(item_id=sims[0].id, item_type=ItemType.SIMULATION)
        self.assertEqual(workdir_dict[sims[0].id], str(self.platform.get_container_directory(sims[0])))

    def test_create_sim_directory_df(self):
        experiment = self.platform.get_item(self.exp.uid, ItemType.EXPERIMENT, raw=False)
        exp_df = self.platform.create_sim_directory_df(experiment.id)
        for sim in experiment.simulations:
            sim_container_path = self.platform.get_container_directory(sim)
            # verify exp_df stores the correct outpath for each sim
            self.assertEqual(sim_container_path, exp_df[exp_df['simid'] == sim.id]['outpath'].values[0])



