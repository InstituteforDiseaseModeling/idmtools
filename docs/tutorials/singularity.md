# Singularity containers tutorial

Run models inside Singularity containers for reproducible, environment-controlled simulations on HPC clusters (COMPS and Slurm).

## Prerequisites

- idmtools installed: `pip install idmtools[idm]` or `pip install idmtools[slurm]`
- Singularity installed on your target cluster
- A Singularity image (`.sif` file) for your environment

## Learning objectives

- Understand when and why to use Singularity containers
- Run a Python model inside a Singularity container
- Run non-Python models (R, shell scripts, compiled binaries)
- Run parameter sweeps with Singularity tasks

---

## Why Singularity?

Singularity containers package your entire software environment into a single `.sif` file:

- Reproducibility — exact same Python/R/library versions every run
- Portability — run the same container on any cluster
- No root required — unlike Docker, Singularity runs without admin privileges
- HPC-friendly — designed for use on shared HPC clusters like Slurm and COMPS

---

## Tutorial 1: Build a Singularity image

Use `SingularityBuildWorkItem` to build a container image on the platform. This is done once — the resulting `.sif.id` file is reused in all subsequent experiments.

### python_minimal.def

```singularity
Bootstrap: library
From: ubuntu:22.04

%labels
    Author idmtools
    Version 1.0
    Description Minimal Python environment - fast build time

%help
    This container provides a minimal Python 3.11 environment with only essential packages.
    Build time: ~2-3 minutes (vs 10+ minutes for full environments)

    Includes:
    - Python 3.11
    - NumPy (numerical computing)
    - Matplotlib (basic plotting)

    Usage:
        singularity exec python_minimal.sif python3 script.py

%post
    # Update and install Python
    apt-get update && apt-get install -y \
        python3.11 \
        python3-pip \
        ca-certificates

    # Install minimal packages
    pip3 install --no-cache-dir \
        numpy>=1.24.0 \
        matplotlib>=3.7.0

    # Clean up
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    pip3 cache purge

%environment
    export PYTHONUNBUFFERED=1
    export MPLBACKEND=Agg

%runscript
    exec python3 "$@"
```

### Step 1: Build the image

```python
# examples/singularity/definitions/build_images.py
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

platform = Platform("Calculon")

sif_name = "python_minimal.sif"

# Create Singularity build work item from a definition file
sbi = SingularityBuildWorkItem(
    name="Minimal Python - Singularity Build",
    definition_file="python_minimal.def",
    image_name=sif_name
)

# Add tags for tracking
sbi.tags = {"environment": "python_minimal"}

# Submit the build and wait for it to complete
ac = sbi.run(wait_until_done=True, platform=platform)

if sbi.succeeded:
    # Save asset collection ID to a file for reuse in experiments
    ac.to_id_file("python_minimal.sif.id")
    print(f"Build succeeded!")
    print(f"Asset Collection ID saved to: python_minimal.sif.id")
    print(f"Asset Collection ID: {ac.uid}")
else:
    print("Build failed")
```

### Step 2: Use the image in an experiment

Once built, reference the `.sif.id` file in your task:

```python
# examples/singularity/singularity_task_examples/simple_simulator.py
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.assets import AssetCollection
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

platform = Platform("Calculon")

sif_name = "python_minimal.sif"

task = SingularityJSONConfiguredPythonTask(
    script_path="sir_model.py",
    provided_command=CommandLine(
        f"singularity exec ./Assets/{sif_name} python3 Assets/sir_model.py"
    )
)

# Load the previously built .sif image by its asset ID file
task.common_assets.add_assets(AssetCollection.from_id_file("python_minimal.sif.id"))

# Set parameters
task.parameters = {
    "N": 10000,
    "beta": 0.5,
    "gamma": 0.1,
    "days": 160
}

experiment = Experiment.from_task(task, name="Singularity Python Example")
experiment.run(platform=platform, wait_until_done=True)
print(f"Status: {experiment.status}")
```

---

## Tutorial 2: Generic Singularity task (R, shell, binaries)

Use `SingularityJSONConfiguredTask` for any language or executable:

### R script example

```python
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.assets import Asset, AssetCollection
from idmtools_models.singularity_json_task import SingularityJSONConfiguredTask

platform = Platform("COMPS")

task = SingularityJSONConfiguredTask(config_file_name="config.json")

task.provided_command = CommandLine(
    "singularity exec ./Assets/r_env.sif Rscript Assets/analysis.R --config config.json"
)

# Add R script as an asset
task.common_assets.add_asset(Asset(
    filename="analysis.R",
    content="""
library(jsonlite)
config <- fromJSON("config.json")
cat("alpha =", config$alpha, "\\n")
cat("beta  =", config$beta, "\\n")
# your analysis here
"""
))

task.common_assets.add_assets(AssetCollection.from_id_file("r_env.sif.id"))

task.parameters = {
    "alpha": 0.05,
    "beta": 0.95,
    "iterations": 1000
}

experiment = Experiment.from_task(task, name="R in Singularity")
experiment.run(platform=platform, wait_until_done=True)
```

### Shell script example

```python
task = SingularityJSONConfiguredTask(config_file_name="params.json")

task.provided_command = CommandLine(
    "singularity exec ./Assets/analysis_env.sif bash Assets/process_data.sh"
)

task.common_assets.add_asset(Asset(
    filename="process_data.sh",
    content="""#!/bin/bash
THRESHOLD=$(jq -r '.threshold' params.json)
echo "Processing with threshold: $THRESHOLD"
# your data processing logic here
"""
))

task.parameters = {
    "threshold": 0.75,
    "output_dir": "results",
    "num_workers": 4
}
```

---

## Tutorial 3: Parameter sweep with Singularity

Combine Singularity tasks with `SimulationBuilder` for full parameter sweeps:

```python
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools_models.singularity_json_task import SingularityJSONConfiguredTask

platform = Platform("COMPS")

# Base task
base_task = SingularityJSONConfiguredTask()
base_task.provided_command = CommandLine(
    "singularity exec ./Assets/python_env.sif python3 ./Assets/model.py"
)
base_task.common_assets.add_assets(AssetCollection.from_id_file("python_env.sif.id"))
base_task.common_assets.add_asset("model.py")

base_task.parameters = {
    "alpha": 0.1,
    "beta": 0.2
}

# Build parameter sweep
builder = SimulationBuilder()

def set_alpha(simulation: Simulation, value):
    return simulation.task.set_parameter("alpha", value)

builder.add_sweep_definition(set_alpha, [0.1, 0.2, 0.3, 0.4, 0.5])

# Create and run experiment
experiment = Experiment.from_builder(
    builder,
    base_task,
    name="Singularity Parameter Sweep"
)

experiment.run(platform=platform, wait_until_done=True)
print(f"Ran {len(experiment.simulations)} simulations")
print(f"Status: {experiment.status}")
```

---

## Using the `.id` file pattern

When working with COMPS or Slurm, upload your `.sif` once and reuse the asset ID:

```python
from idmtools.assets import AssetCollection

# Load previously uploaded .sif by its asset ID file
ac = AssetCollection.from_id_file("path/to/python_env.sif.id")
task.common_assets.add_assets(ac)
```

This avoids re-uploading large container images on every run.

---

## Project structure

A typical Singularity-based project:

```
my_project/
├── model.py                  # Your model script
├── run_experiment.py         # Experiment submission
├── python_env.def            # Singularity definition file
├── python_env.sif            # Built container image (local)
├── python_env.sif.id         # COMPS asset ID (after upload)
└── idmtools.ini              # Platform configuration
```

---

## Next steps

- [Parameter Sweeps Guide](../tutorials/parameter-sweeps.md) - Advanced sweep patterns
- [Asset Management](../user-guide/assets.md) - Managing `.sif` files and other assets
- [COMPS Platform](../platforms/comps.md) - COMPS-specific Singularity options
- [Slurm Platform](../platforms/slurm.md) - Running Singularity on Slurm clusters
