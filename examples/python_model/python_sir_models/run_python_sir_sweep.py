# run_python_sir_sweep.py
from idmtools.assets import AssetCollection, Asset
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.python.python_task import PythonTask
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

# Create platform
platform = Platform("Container", job_directory="DEST")
#platform = Platform("SlurmStage")

platform_type = platform.__class__.__name__

sif_name = "python_minimal.sif"
## If is Comps platform, we need to run in singularity
if platform_type == 'COMPSPlatform':
    command = CommandLine(
        f"singularity exec ./Assets/{sif_name} python3 Assets/sir_model.py",
    )
    task = SingularityJSONConfiguredPythonTask(provided_command=command, script_path="sir_model.py")
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

# Set base parameters
task.parameters = {
    "N": 10000,
    "gamma": 0.1,
    "days": 160
}

# Create builder for parameter sweep
builder = SimulationBuilder()

# Sweep over beta (transmission rate)
beta_values = [0.3, 0.4, 0.5, 0.6, 0.7]

def set_beta(simulation:Simulation, beta):
    simulation.task.parameters["beta"] = beta
    simulation.tags["beta"] = beta
    simulation.name = f"SIR_beta_{beta:.2f}"

builder.add_sweep_definition(set_beta, beta_values)

# Create experiment from builder
experiment = Experiment.from_builder(
    builder,
    task,
    name="SIR Python Model - Beta Sweep"
)

print(f"Created {len(experiment.simulations)} simulations")

# Run experiment
experiment.run(
    platform=platform,
    wait_until_done=True
)

print(f"Experiment ID: {experiment.id}")
print(f"Status: {experiment.status}")