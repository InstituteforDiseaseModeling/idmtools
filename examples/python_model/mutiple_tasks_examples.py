import os
from functools import partial

from idmtools.assets import Asset, AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask


def run_example_PythonTask(ac_id):
    task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "task_model", "model_file.py"))

    ts = TemplatedSimulations(base_task=task)
    common_assets = AssetCollection.from_id(ac_id,  as_copy=True)
    sim = ts.new_simulation()
    experiment = Experiment(name="run_example_PythonTask", simulations=[sim], assets=common_assets)
    experiment.run(wait_until_done=True)


def run_example_CommandTask(ac_id):
    command = "python Assets/model_file.py"
    task = CommandTask(command=command)

    model_asset = Asset(absolute_path=os.path.join("inputs", "task_model", "model_file.py"))
    common_assets = AssetCollection.from_id(ac_id, as_copy=True)
    common_assets.add_asset(model_asset)
    # create experiment from task
    experiment = Experiment.from_task(task, name="run_example_CommandTask", assets=common_assets)
    experiment.run(wait_until_done=True)


def run_pip_list():
    command = "Assets/run.sh"
    task = CommandTask(command=command)
    ac = AssetCollection()
    model_asset = Asset(absolute_path=os.path.join("inputs", "task_model", "run.sh"))
    ac.add_asset(model_asset)
    # create experiment from task
    experiment = Experiment.from_task(task, name="run_pip_list", assets=ac)
    experiment.run(wait_until_done=True)


def run_example_task_from_template(ac_id):
    common_assets = AssetCollection.from_id(ac_id, as_copy=True)
    task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "task_model", "model_file.py"),
                                    common_assets=common_assets, parameters=dict(c=0))
    ts = TemplatedSimulations(base_task=task)
    setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
    builder = SimulationBuilder()
    builder.add_sweep_definition(setA, range(0, 2))
    ts.add_builder(builder)
    # create experiment from task
    experiment = Experiment.from_template(ts, name="run_example_task_from_template")
    experiment.run(wait_until_done=True)


if __name__ == '__main__':
    platform = Platform('SlurmStage')
    ac_id = "728c0426-2df1-ee11-9302-f0921c167864"
    if ac_id:
        run_example_CommandTask(ac_id)
        run_example_PythonTask(ac_id)
        run_example_task_from_template(ac_id)
        run_pip_list()
    else:
        print('Failed to generate asset collection!')

