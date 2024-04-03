import os

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# load up an existing experiment with completed simulations
with Platform('CALCULON'):
    # Create First Experiment
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                                 [i for i in range(5)])
    model_path = os.path.join("..", "..", "python_model", "inputs", "python_model_with_deps", "Assets", "model.py")
    sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
    sims_template.add_builder(builder=builder)

    experiment = Experiment.from_template(sims_template)
    experiment.run(wait_until_done=True)

    # IMPORTANT NOTE:
    # Currently it is important you wait on existing Simulations to finish provision when changing assets later
    # idmtools cannot detect this state at the moment and it can leave to unexpected behaviour


    # You could start with experiment = Experiment.from_id(...., copy_assets=True)
    # Changing the Common Assets
    experiment.assets = experiment.assets.copy()
    # Add new simulations to the experiment
    model_path = os.path.join("..", "..", "python_model", "inputs", "python_model_with_deps", "Assets", "newmodel2.py")
    sims_template = TemplatedSimulations(base_task=JSONConfiguredPythonTask(script_path=model_path))
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"),
                                 [i for i in range(6, 10)])
    sims_template.add_builder(builder=builder)
    experiment.simulations.extend(sims_template)

    # If you are adding a large amount of simulations through a Template, it is recommended to do the following to keep generator use and lower memory footprint
    #
    # sims_template.add_simulations(experiment.simulations)
    # experiment.simulations = simulations

    # run all simulations in the experiment that have not run before and wait
    experiment.run(wait_until_done=True, regather_common_assets=True)
