import os
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

def create_experiment(platform):
    # Define path to assets directory
    current_dir = os.path.join(os.path.dirname(__file__))
    assets_directory = os.path.join(current_dir, "..", "python_model", "inputs", "python", "Assets")
    # Define task
    task = JSONConfiguredPythonTask(script_path=os.path.join(assets_directory, "model.py"), parameters=(dict(c=0)))
    task.python_path = "python3"
    # Define templated simulation
    ts = TemplatedSimulations(base_task=task)
    ts.base_simulation.tags['sim_tag'] = "test_tag"
    # Define builder
    builder = SimulationBuilder()

    # Define partial function to update parameter
    def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        return simulation.task.set_parameter(param, value)

    # Let's sweep the parameter 'a' for the values 0-2
    builder.add_sweep_definition(partial(param_update, param="a"), range(3))

    # Let's sweep the parameter 'b' for the values 0-4
    builder.add_sweep_definition(partial(param_update, param="b"), range(5))
    ts.add_builder(builder)

    # Create Experiment using template builder
    experiment = Experiment.from_template(ts, name="python example")
    # Add our own custom tag to experiment
    experiment.tags["tag1"] = 1
    # And all files from assets_directory to experiment folder
    experiment.assets.add_directory(assets_directory=assets_directory)

    experiment.run(platform=platform, wait_until_done=True)
    return experiment

if __name__ == "__main__":
    platform = Platform("Container", job_directory="DEST")
    experiment = create_experiment(platform)
    print(experiment)