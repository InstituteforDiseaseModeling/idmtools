# Creating simulations & experiments

Learn how to create simulations and organize them into experiments in idmtools.

## Key concepts

- **Task** — wraps your model script and its parameters
- **Simulation** — a single run of a task with specific parameters
- **Experiment** — a collection of simulations submitted together to a platform

## Basic example

```python
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# Create platform
platform = Platform('Container', job_directory='anywhere')

# Create a python task that runs a model.py. Make sure model.py exists in local dir
task = JSONConfiguredPythonTask(script_path="model.py")

# Add to experiment (required for commission)
experiment = Experiment.from_task(
    task,
    name="My First Experiment"
)

# Commission
experiment.run(wait_until_done=True, platform=platform)

# Check status
print(f"Status: {experiment.status}")
```

## Task types

### JSONConfiguredPythonTask

Runs a Python script and automatically writes parameters to a `config.json` file that your model reads:

```python
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

task = JSONConfiguredPythonTask(
    script_path="model.py",
    parameters={"beta": 0.5, "gamma": 0.1, "N": 10000}
)
```

### PythonTask

Runs a Python script directly:

```python
from idmtools_models.python.python_task import PythonTask

task = PythonTask(
    script_path="model.py",
    python_path="python"
)
```

### CommandTask

Runs any command-line program:

```python
from idmtools.entities.command_task import CommandTask

task = CommandTask(command="python model.py --config config.json")
```

## Simulation tags

Tags are key-value metadata used for filtering and querying results:

```python
sim.tags = {
    "model_version": "1.0",
    "scenario": "baseline",
    "researcher": "team_a"
}
```

## Adding assets

Add input files your model needs:

```python
# Add individual files
task.common_assets.add_asset("data.csv")

# Add a directory of files
task.common_assets.add_directory("inputs/")
```

## Running an experiment

```python
experiment.run(wait_until_done=True, platform=platform)

print(f"Experiment ID: {experiment.id}")
print(f"Status: {experiment.status}")
```

## Multiple simulations

### Experiment.from_template

Use `from_template` with `TemplatedSimulations` and a `SimulationBuilder` to define sweeps before creating the experiment:

```python
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations

def set_value(simulation, name, value):
    fix_value = round(value, 2) if isinstance(value, float) else value
    simulation.task.command.add_raw_argument(fix_value)
    simulation.tags[name] = fix_value

command = CommandLine("python3 Assets/model.py")
task = CommandTask(command=command)
ts = TemplatedSimulations(base_task=task)

sb = SimulationBuilder()
sb.add_sweep_definition(partial(set_value, name="pop_size"), [10000, 20000])
sb.add_sweep_definition(partial(set_value, name="n_days"), [100, 110])
ts.add_builder(sb)

experiment = Experiment.from_template(ts, name="Command Task Sweep")
experiment.run(wait_until_done=True, platform=platform)
```

### Experiment.from_builder

Use `from_builder` with `SimulationBuilder` for systematic parameter sweeps:

```python
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment

builder = SimulationBuilder()
builder.add_sweep_definition(
    JSONConfiguredPythonTask.set_param_partial("beta"),
    [0.1, 0.2, 0.3, 0.4, 0.5]
)

experiment = Experiment.from_builder(builder, task, name="Beta Sweep")
experiment.run(wait_until_done=True, platform=platform)
```

See [Parameter Sweeps](../tutorials/parameter-sweeps.md) for more sweep patterns.

## Next steps

- [Parameter Sweeps](../tutorials/parameter-sweeps.md) - Run systematic parameter variations
- [Asset Management](assets.md) - Manage input files and resources
- [Data Analysis](../data-analysis/analyzers.md) - Process simulation outputs
- [Platform Guides](../platforms/index.md) - Platform-specific details
