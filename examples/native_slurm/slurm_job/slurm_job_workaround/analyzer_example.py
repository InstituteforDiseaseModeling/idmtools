"""
There are 2 ways to run this example for analyzer.

Option1: run "python3 analyzer_example.py".
- This will run python script (i.e analyzer_example.py) on Slurm head node
- analyzer_example.py first build experiment/simulations, and then triggers a Slurm job to run experiment/simulations
- Next, analyzer_example.py continue to run AnalyzeManager for data analysis on Slurm head node

Option2, run "sbatch sbatch_for_analyzer_example.sh".
- This will trigger a slurm job to run python script (i.e analyzer_example.py) in computation node.
- analyzer_example.py first build experiment/simulations, and then triggers a Slurm job to run experiment/simulations
- Next, analyzer_example.py continue to run AnalyzeManager to do data analysis on computation node

These two examples takes Northwestern University Slurm environment QUEST as a demonstration and the examples are supposed
 to run on QUEST head nodes. If you want to run these samples on other Slurm environments, based on their Slurm setup
 configuration or requirements, you may have to pass different Slurm parameters (here, partition, time and account are
 required Slurm parameters in QUEST).
"""
from functools import partial

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
import os
from idmtools.entities.ianalyzer import IAnalyzer, ANALYZABLE_ITEM


class MyAnalyzer(IAnalyzer):
    """
    A simple custom analyzer.
    """

    def __init__(self, filenames=None, output_path='output'):
        super().__init__()
        self.output_path = output_path
        self.filenames = filenames or []

    def initialize(self):
        self.output_path = os.path.join(self.working_dir, self.output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def map(self, data, item: ANALYZABLE_ITEM):
        a = data['config.json']['parameters']['a']
        b = data['config.json']['parameters']['b']
        c = data['config.json']['parameters']['c']
        return a + b + c

    def reduce(self, data):
        value = sum(data.values())
        print(value)
        with open('output.txt', 'w') as file:
            file.write(str(value))
        return value


job_directory = os.path.join(os.path.expanduser('~'), "example/slurm_job")
platform = Platform('SLURM_LOCAL', job_directory=job_directory, partition='b1139', time='10:00:00', account='b1139')


def run_experiment():

    builder = SimulationBuilder()

    # Sweep parameter "a"
    def param_update(simulation: Simulation, param, value):
        return simulation.task.set_parameter(param, value)

    builder.add_sweep_definition(partial(param_update, param="a"), range(3))
    builder.add_sweep_definition(partial(param_update, param="b"), range(5))

    task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                    envelope="parameters", parameters=(dict(c=0)))
    task.python_path = "python3"
    ts = TemplatedSimulations(base_task=task)
    ts.add_builder(builder)
    e = Experiment.from_template(ts, name="test experiment")
    e.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))
    suite = Suite(name='Idm Suite')
    suite.add_experiment(e)
    suite.run(platform=platform, wait_on_done=True, max_running_jobs=5, retries=5, dry_run=False)
    return e.id


analyzers = [MyAnalyzer(filenames=['config.json'])]
exp_id = run_experiment()
#exp_id = "443beef1-9202-4959-886a-858d8f9c9fdf"
am = AnalyzeManager(configuration={}, platform=platform,
                            ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
am.analyze()
