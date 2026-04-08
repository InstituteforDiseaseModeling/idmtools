# Parameter Sweeps

Systematic parameter exploration with idmtools.

## Part 1: Simple Single-Parameter Sweep

```python
# examples/parameter_sweeps/single_sweep_in_container.py
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools_models.python.python_task import PythonTask

platform = Platform("Container", job_directory="DEST")

task = PythonTask(script_path="inputs/run_model_and_plot.py")
task.transient_assets.add_asset("inputs/sir-model-config.py")

# Set base parameters shared across all simulations
task.parameters = {
    "gamma": 0.1,
    "days": 160,
    "population": 10000
}

builder = SimulationBuilder()

beta_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

def set_beta_parameter(simulation, beta):
    simulation.task.parameters["beta"] = beta
    simulation.tags["beta"] = beta  # tag for filtering during analysis

builder.add_sweep_definition(set_beta_parameter, beta_values)

experiment = Experiment.from_builder(
    builder,
    task,
    name="Single Parameter Sweep"
)

experiment.run(platform=platform, wait_until_done=True)

print(f"Experiment ID: {experiment.id}")
print(f"Status: {experiment.status}")
```

## Part 2: Two-Dimensional Grid Sweep

Sweeps all combinations of `beta` and `gamma`:

```python
# examples/parameter_sweeps/grid_sweep.py
from itertools import product
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment

beta_values = [0.3, 0.4, 0.5, 0.6, 0.7]
gamma_values = [0.05, 0.1, 0.15, 0.2]

# generate all (beta, gamma) pairs
combinations = list(product(beta_values, gamma_values))

def set_params(simulation, params):
    beta, gamma = params
    simulation.task.set_parameter("beta", beta)
    simulation.task.set_parameter("gamma", gamma)
    simulation.tags["beta"] = beta
    simulation.tags["gamma"] = gamma
    simulation.tags["R0"] = beta / gamma  # derived tag useful for analysis
    simulation.name = f"beta_{beta:.2f}_gamma_{gamma:.2f}"

builder = SimulationBuilder()
builder.add_sweep_definition(set_params, combinations)

# Creates 5 × 4 = 20 simulations
experiment = Experiment.from_builder(builder, task, name="2D Grid Sweep")
experiment.run(platform=platform, wait_until_done=True)
```

## Part 3: Multi-Dimensional Sweep

Sweeps four parameters:

```python
# examples/parameter_sweeps/multidimensional_sweep.py
from itertools import product
import numpy as np
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment

params = {
    "beta": np.linspace(0.3, 0.7, 5),
    "gamma": np.linspace(0.05, 0.2, 4),
    "population": [1000, 5000, 10000],
    "initial_infected": [1, 10, 50]
}

# full factorial: all combinations across all four parameters
combinations = list(product(
    params["beta"],
    params["gamma"],
    params["population"],
    params["initial_infected"]
))

print(f"Total combinations: {len(combinations)}")  # 5×4×3×3 = 180

def set_all_params(simulation, params):
    beta, gamma, pop, init_inf = params
    simulation.task.set_parameter("beta", beta)
    simulation.task.set_parameter("gamma", gamma)
    simulation.task.set_parameter("population", pop)
    simulation.task.set_parameter("initial_infected", init_inf)
    simulation.tags = {
        "beta": beta,
        "gamma": gamma,
        "population": pop,
        "initial_infected": init_inf,
        "R0": beta / gamma
    }
    simulation.name = f"N{pop}_beta{beta:.2f}_gamma{gamma:.2f}_init_inf{init_inf}"

builder = SimulationBuilder()
builder.add_sweep_definition(set_all_params, combinations)

experiment = Experiment.from_builder(builder, task, name="Multi-Dimensional Factorial")
experiment.run(platform=platform, wait_until_done=True)
```

## Part 4: Latin Hypercube Sampling

Efficiently samples high-dimensional parameter spaces:

```python
# examples/parameter_sweeps/lhs_sweep.py
from scipy.stats import qmc
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment

n_params = 4
n_samples = 100

# LHS fills the parameter space more evenly than random sampling
sampler = qmc.LatinHypercube(d=n_params)
sample = sampler.random(n=n_samples)

param_bounds = {
    "beta": (0.1, 0.9),
    "gamma": (0.05, 0.3),
    "population": (1000, 100000),
    "days": (100, 365)
}

# scale unit hypercube samples to actual parameter ranges
bounds_lower = [v[0] for v in param_bounds.values()]
bounds_upper = [v[1] for v in param_bounds.values()]
scaled_samples = qmc.scale(sample, bounds_lower, bounds_upper)

param_names = list(param_bounds.keys())
param_sets = []
for sample_vals in scaled_samples:
    param_dict = {name: val for name, val in zip(param_names, sample_vals)}
    param_dict["population"] = int(param_dict["population"])  # must be integer
    param_dict["days"] = int(param_dict["days"])
    param_sets.append(param_dict)

def set_lhs_params(simulation, params):
    for key, value in params.items():
        simulation.task.set_parameter(key, value)
    simulation.tags.update(params)
    simulation.tags["R0"] = params["beta"] / params["gamma"]

builder = SimulationBuilder()
builder.add_sweep_definition(set_lhs_params, param_sets)

experiment = Experiment.from_builder(builder, task, name="Latin Hypercube Sampling")
experiment.run(platform=platform, wait_until_done=True)
```

## Part 5: Scenario-Based Sweep

Organizes sweeps by named scenarios:

```python
# examples/parameter_sweeps/scenario_sweep.py
from itertools import product
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment

scenarios = {
    "baseline": {
        "intervention": False,
        "beta": [0.5, 0.6, 0.7],
        "gamma": [0.1, 0.15],
    },
    "masks": {
        "intervention": True,
        "beta": [0.3, 0.4, 0.5],  # reduced transmission
        "gamma": [0.1, 0.15],
    },
    "lockdown": {
        "intervention": True,
        "beta": [0.1, 0.2, 0.3],  # strongly reduced transmission
        "gamma": [0.1, 0.15],
    },
}

# flatten all scenarios into a single list of parameter dicts
all_params = []
for scenario_name, config in scenarios.items():
    for beta, gamma in product(config["beta"], config["gamma"]):
        all_params.append({
            "scenario": scenario_name,
            "intervention": config["intervention"],
            "beta": beta,
            "gamma": gamma,
            "R0": beta / gamma
        })

print(f"Total parameter sets: {len(all_params)}")

def set_scenario_params(simulation, params):
    simulation.task.set_parameter("beta", params["beta"])
    simulation.task.set_parameter("gamma", params["gamma"])
    simulation.task.set_parameter("intervention", params["intervention"])
    simulation.tags = params  # store all params as tags for easy filtering
    simulation.name = f"{params['scenario']}_beta{params['beta']:.2f}"

builder = SimulationBuilder()
builder.add_sweep_definition(set_scenario_params, all_params)

experiment = Experiment.from_builder(builder, task, name="Scenario-Based Sweep")
experiment.run(platform=platform, wait_until_done=True)

print(f"Experiment ID: {experiment.id}")
print(f"Status: {experiment.status}")
```

## Next Steps

- [Creating Simulations & Experiments](../user-guide/creating-simulations.md) - Core concepts
- [Data Analysis](../data-analysis/index.md) - Process simulation results
- [Python Models](python-models.md) - Model implementation examples
