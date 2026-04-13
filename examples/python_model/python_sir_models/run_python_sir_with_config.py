# run_python_sir_with_config.py
import json

from idmtools.assets import AssetCollection, Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

# Create platform
#platform = Platform("Container", job_directory="DEST")
platform = Platform("SlurmStage")

platform_type = platform.__class__.__name__
sif_name = "python_minimal.sif"
## If is Comps platform, we need to run in singularity
if platform_type == 'COMPSPlatform':
    command = CommandLine(
        f"singularity exec ./Assets/{sif_name} python3 Assets/sir_model_config.py",
    )
    task = SingularityJSONConfiguredPythonTask(provided_command=command, script_path="sir_model_config.py")
    # Add Singularity as COMPS assets
    task.common_assets.add_assets(AssetCollection.from_id_file(f"../../singularity/definitions/{sif_name}.id"))

elif platform_type == 'ContainerPlatform':
    command = CommandLine("python3 Assets/sir_model.py")
    task = JSONConfiguredPythonTask(
        script_path="sir_model.py"
    )
else:
    print("TODO for Slurm and File/Process platfroms")
    print("Need to use python_analysis.sif image")
    exit(1)

# Create builder
builder = SimulationBuilder()

def create_config_file(simulation, params):
    """Create config file for each simulation."""
    config = {
        "N": 10000,
        "beta": params["beta"],
        "gamma": params["gamma"],
        "days": 160
    }

    # Write config to file
    config_filename = f"config_{simulation.id}.json"
    with open(config_filename, "w") as f:
        json.dump(config, f, indent=2)

    # Add config file as asset
    simulation.add_asset(config_filename)

    # Set command line argument to use custom config file
    simulation.task.command.add_argument(config_filename)

    # Tag simulation
    simulation.tags.update(params)
    simulation.name = f"SIR_beta_{params['beta']:.2f}_gamma_{params['gamma']:.2f}"

# Define parameter combinations
param_combinations = [
    {"beta": 0.5, "gamma": 0.1},
    {"beta": 0.6, "gamma": 0.15},
    {"beta": 0.7, "gamma": 0.2},
]

builder.add_sweep_definition(create_config_file, param_combinations)

# Create and run experiment
experiment = Experiment.from_builder(
    builder,
    task,
    name="SIR Python Model - Config Files"
)

experiment.run(platform=platform, wait_until_done=True)

print(f"Experiment complete: {experiment.id}")
print(f"Status: {experiment.status}")