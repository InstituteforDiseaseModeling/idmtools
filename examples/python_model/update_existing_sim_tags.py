import os

from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# load up an existing experiment with completed simulations
from idmtools_platform_comps.utils.general import update_tags_for_existing_item

with Platform('Calculon') as platform:
    # Create First Experiment
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                                 [i for i in range(2)])
    model_path = os.path.join("inputs", "python_model_with_deps", "Assets", "model.py")
    sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
    sims_template.add_builder(builder=builder)

    experiment = Experiment.from_template(sims_template, name="update tags")
    experiment.run(wait_until_done=True)

    # update simulation tags - notes simulations are already in COMPS
    simulations = experiment.simulations.items
    for sim in simulations:
        tags = {"a": 1, "b": "test"}
        update_tags_for_existing_item(platform, sim.id, ItemType.SIMULATION, tags)

    # update experiment tags
    tags_exp = {"exp_tag": "test"}
    update_tags_for_existing_item(platform, experiment.id, ItemType.EXPERIMENT, tags_exp)