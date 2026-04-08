# Python Models Tutorial

Learn how to create and run Python-based simulations with idmtools.

## Overview

This tutorial demonstrates how to use **JSONConfiguredPythonTask** to run Python models on various compute platforms. We'll build a simple SIR (Susceptible-Infected-Recovered) epidemiological model.

## Prerequisites

Install the package for your target platform:

```bash
pip install idmtools[idm]        # COMPS platform
pip install idmtools[container]  # Container platform (local Docker)
pip install idmtools[slurm]      # Slurm platform
pip install idmtools[full]       # All platforms
```

## Step 1: Create Your Model

First, create a simple SIR model in `sir_model.py`:

```python
# examples/python_model/python_sir_models/sir_model.py
import sys
import json
import matplotlib.pyplot as plt

def sir_model(N, beta, gamma, days, initial_infected=1):
    """
    Simple SIR model implementation.

    Parameters:
    - N: Total population
    - beta: Transmission rate
    - gamma: Recovery rate
    - days: Number of days to simulate
    - initial_infected: Initial number of infected individuals
    """
    # Initialize compartments
    S = N - initial_infected
    I = initial_infected
    R = 0

    # Store time series
    S_history = [S]
    I_history = [I]
    R_history = [R]

    # Run simulation
    for day in range(days):
        # Calculate new infections and recoveries
        new_infections = beta * S * I / N
        new_recoveries = gamma * I

        # Update compartments
        S -= new_infections
        I += new_infections - new_recoveries
        R += new_recoveries

        # Store results
        S_history.append(S)
        I_history.append(I)
        R_history.append(R)

    # Save results
    results = {
        "S": S_history,
        "I": I_history,
        "R": R_history,
        "final_infected_total": R,
        "peak_infected": max(I_history),
        "peak_day": I_history.index(max(I_history))
    }

    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(S_history, label="Susceptible", color="blue")
    plt.plot(I_history, label="Infected", color="red")
    plt.plot(R_history, label="Recovered", color="green")
    plt.xlabel("Days")
    plt.ylabel("Number of Individuals")
    plt.title(f"SIR Model: β={beta:.3f}, γ={gamma:.3f}")
    plt.legend()
    plt.grid(True)
    plt.savefig("sir_curve.png", dpi=150)
    plt.close()

    print(f"Simulation complete: Peak infected = {max(I_history):.0f} on day {I_history.index(max(I_history))}")

    return results

if __name__ == "__main__":
    # Read parameters from command line or config file
    if len(sys.argv) > 1:
        # Read from config file
        with open(sys.argv[1], "r") as f:
            config = json.load(f)
    else:
        # Default parameters
        config = {
            "N": 10000,
            "beta": 0.5,
            "gamma": 0.1,
            "days": 160
        }

    # Run model
    sir_model(**config)
```

## Step 2: Create idmtools Script

Create `run_python_sir.py` to run the model with idmtools:

```python
# examples/python_model/python_sir_models/run_python_sir.py
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# Create platform
platform = Platform("Container", job_directory="DEST")

task = JSONConfiguredPythonTask(script_path="sir_model.py")

# Set parameters
task.parameters = {
    "N": 10000,
    "beta": 0.5,
    "gamma": 0.1,
    "days": 160
}
ts = TemplatedSimulations(base_task=task)
# Create experiment
experiment = Experiment.from_task(
    task,
    name="SIR Python Model - Single Run"
)

# Run experiment
experiment.run(
    platform=platform,
    wait_until_done=True
)

print(f"Experiment ID: {experiment.id}")
print(f"Status: {experiment.status}")
```

## Step 3: Run Your First Simulation

```bash
python run_python_sir.py
```

You should see output like:
```
Commissioning experiment...
Running simulation...
Simulation complete: Peak infected = 1234 on day 45
Experiment ID: abc123...
Status: Succeeded
```

## Step 4: Parameter Sweeps

Now let's explore different beta values using `SimulationBuilder`:

```python
# examples/python_model/python_sir_models/run_python_sir_sweep.py
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# Create platform
platform = Platform("Container", job_directory="DEST")

task = JSONConfiguredPythonTask(script_path="sir_model.py")

# Set base parameters shared across all simulations
task.parameters = {
    "N": 10000,
    "gamma": 0.1,
    "days": 160
}

builder = SimulationBuilder()

# Sweep over beta (transmission rate)
beta_values = [0.3, 0.4, 0.5, 0.6, 0.7]

def set_beta(simulation: Simulation, beta):
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
```

## Step 5: Using Configuration Files

For complex models, use JSON configuration files to sweep parameters — each simulation gets its own config file with its specific parameter values:

```python
# examples/python_model/python_sir_models/run_python_sir_with_config.py
import json
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# Create platform
platform = Platform("Container", job_directory="DEST")

task = JSONConfiguredPythonTask(script_path="sir_model.py")

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
```

## Step 6: Analyzing Results

Create an analyzer to process outputs:

```python
# examples/python_model/python_sir_models/analyze_sir_results.py
import pandas as pd
import matplotlib.pyplot as plt

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class SIRAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(
            filenames=["output.json", "sir_curve.png"]
        )

    def map(self, data, simulation):
        """Extract results from each simulation."""
        results = data.get("output.json")
        if not results:
            return None

        return {
            "sim_id": str(simulation.id),
            "beta": float(simulation.tags.get("beta", 0)),
            "gamma": float(simulation.tags.get("gamma", 0)),
            "peak_infected": results["peak_infected"],
            "peak_day": results["peak_day"],
            "final_recovered": results["final_infected_total"]
        }

    def reduce(self, all_data):
        """Aggregate and visualize results."""

        rows = []
        for simulation, result in all_data.items():
            rows.append(result)

        df = pd.DataFrame(rows)
        # Create summary plot
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Peak infected vs beta
        axes[0].scatter(df["beta"], df["peak_infected"])
        axes[0].set_xlabel("Transmission Rate (β)")
        axes[0].set_ylabel("Peak Infected")
        axes[0].set_title("Peak Infections vs Transmission Rate")
        axes[0].grid(True)

        # Plot 2: Peak day vs beta
        axes[1].scatter(df["beta"], df["peak_day"])
        axes[1].set_xlabel("Transmission Rate (β)")
        axes[1].set_ylabel("Peak Day")
        axes[1].set_title("Timing of Peak vs Transmission Rate")
        axes[1].grid(True)

        plt.tight_layout()
        plt.savefig("sir_analysis.png", dpi=150)
        plt.close()

        print("\nSummary Statistics:")
        print(df.describe())

        return df


if __name__ == "__main__":
    # Set the platform where you want to run your analysis
    with Platform('Container', job_directory="DEST") as platform:
        # Set the experiment you want to analyze
        exp_id = 'f9f8e80c-4a09-f111-9318-f0921c167864'  

        # Initialize the analyser class with the name of file to save to and start the analysis
        analyzers = [SIRAnalyzer()]

        # Specify the id Type, in this case an Experiment
        manager = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        manager.analyze()

```

## Step 7: Running on Different Platforms

All examples above use the Container platform for local execution. To run on COMPS or Slurm, swap the platform and use the appropriate task type. The `platform_type` check selects the right task and command for each environment:

```python
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

# Swap the platform line to change where your experiment runs
platform = Platform("Container", job_directory="DEST")  # local Docker
# platform = Platform("Slurm_local", job_directory="DEST")  # Slurm cluster
# platform = Platform("COMPS", environment="Calculon")  # COMPS

platform_type = platform.__class__.__name__
sif_name = "python_minimal.sif"

if platform_type == 'COMPSPlatform':
    command = CommandLine(
        f"singularity exec ./Assets/{sif_name} python3 Assets/sir_model.py",
    )
    task = SingularityJSONConfiguredPythonTask(provided_command=command, script_path="sir_model.py")
    # Add Singularity image as a COMPS asset
    task.common_assets.add_assets(AssetCollection.from_id_file(f"../../singularity/definitions/{sif_name}.id"))

elif platform_type == 'SlurmPlatform':
    command = CommandLine(
        f"singularity exec ./Assets/{sif_name} python3 Assets/sir_model.py",
    )
    task = SingularityJSONConfiguredPythonTask(provided_command=command, script_path="sir_model.py")
    # Add Singularity image as a Slurm asset
    task.common_assets.add_asset("python_minimal.sif")

elif platform_type == 'ContainerPlatform':
    task = JSONConfiguredPythonTask(script_path="sir_model.py")

# The rest of your script (set parameters, build simulations, run) is the same
```

## Next Steps

- [Parameter Sweeps](parameter-sweeps.md) - Advanced sweep techniques
- [User Guide](../user-guide/index.md) - Detailed documentation

## See Also

- [API Reference](../api/index.md)
- [Creating Simulations](../user-guide/creating-simulations.md)
- [Analyzers](../data-analysis/index.md)
