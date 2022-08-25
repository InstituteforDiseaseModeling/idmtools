import os
import sys
from functools import partial
from typing import Any, Dict
from pathlib import Path
from idmtools import IdmConfigParser
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# NOTE TO USER
# You need to define your own SlurmNative configuration block before running this example
# Please update examples/idmtools.ini accordingly
platform = Platform('SlurmNative')

with platform:
    parser = IdmConfigParser()
    parser._load_config_file(file_name='idmtools_item_sequence_example.ini')
    parser.ensure_init(file_name='idmtools_item_sequence_example.ini', force=True)
    sequence_file = Path(
        IdmConfigParser.get_option("item_sequence", "sequence_file", 'item_sequences.json')).expanduser()
    if sequence_file.exists():
        sequence_file.unlink()

    task = JSONConfiguredPythonTask(script_path=os.path.join("..", "..", "python_model", "inputs", "python_model_with_deps", "Assets", "model.py"),
                                    parameters=(dict(c=0)))
    ts = TemplatedSimulations(base_task=task)
    builder = SimulationBuilder()

    def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        simulation.task.set_parameter(param, value)
        return {param: value}

    setA = partial(param_update, param="a")
    setB = partial(param_update, param='b')
    builder.add_sweep_definition(setA, range(2))
    builder.add_sweep_definition(setB, range(3))

    ts.add_builder(builder)

    experiment = Experiment.from_template(ts)
    experiment.tags['id'] = experiment.id

    experiment.simulations = list(experiment.simulations)
    for sim in list(experiment.simulations):
        sim.tags['id'] = sim.id

    experiment.run(True)
    sys.exit(0 if experiment.succeeded else -1)