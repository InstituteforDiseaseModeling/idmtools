# Quick Reference

A one-page cheat sheet of the most common idmtools patterns. Each section links to the full documentation page for details.

---

## Documentation Map

| Section | What you'll find |
|---------|-----------------|
| [Installation](getting-started/installation.md) | pip install commands, virtual env setup, Docker auth |
| [Configuration](getting-started/configuration.md) | `idmtools.ini` setup for each platform |
| [Quick Start](getting-started/quickstart.md) | Your first experiment end-to-end |
| [Creating Simulations](user-guide/creating-simulations.md) | Task types, `from_builder`, `from_template` patterns |
| [Asset Management](user-guide/assets.md) | Adding files to tasks and simulations |
| [Data Analysis](data-analysis/index.md) | `IAnalyzer`, `AnalyzeManager`, `PlatformAnalysis` (SSMT) |
| [Parameter Sweeps](tutorials/parameter-sweeps.md) | `SimulationBuilder`, multi-parameter sweeps |
| [Singularity](tutorials/singularity.md) | Container-based workflows |
| [COMPS Platform](platforms/comps.md) | COMPS-specific options |
| [Slurm Platform](platforms/slurm.md) | Slurm job options |
| [Container Platform](platforms/container.md) | Docker-based local execution |
| [CLI Reference](cli/index.md) | `idmtools` command-line tools |
| [FAQ](faq/index.md) | Common questions and troubleshooting |

---

## Installation

```bash
pip install idmtools[full]       # all platforms
pip install idmtools[idm]        # core + COMPS
pip install idmtools[slurm]      # core + Slurm
pip install idmtools[container]  # core + Container (Docker)
```

---

## Core Concepts

| Term | Description |
|------|-------------|
| **Task** | Wraps your model script, its parameters, and input files |
| **Simulation** | A single run of a task with one specific set of parameters |
| **Experiment** | A collection of simulations submitted together |
| **Platform** | Where simulations run — COMPS, Slurm, or Container |
| **Assets** | Files shared across simulations (`common_assets`) or per-simulation (`transient_assets`) |
| **Analyzer** | Post-processing using a map-reduce pattern on simulation outputs |

---

## Common Imports

```python
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.entities.command_task import CommandTask
from idmtools.builders import SimulationBuilder

from idmtools_models.python.python_task import PythonTask
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

from idmtools.entities import IAnalyzer
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
```

---

## Task Types

| Task | Use when |
|------|----------|
| `JSONConfiguredPythonTask` | Python script that reads a `config.json` — parameters written automatically |
| `PythonTask` | Python script run directly |
| `CommandTask` | Any command-line program |

```python
# Writes parameters to config.json for your model to read
task = JSONConfiguredPythonTask(
    script_path="model.py",
    parameters={"beta": 0.5, "gamma": 0.1, "N": 10000}
)

# Runs python directly
task = PythonTask(script_path="model.py", python_path="python")

# Any command-line program
task = CommandTask(command="python model.py --config config.json")
```

---

## Experiment Patterns

### Single simulation

```python
platform = Platform("Container", job_directory="/output")
experiment = Experiment.from_task(task, name="My Experiment")
experiment.run(wait_until_done=True, platform=platform)
print(f"Status: {experiment.status}")
```

### Parameter sweep — `from_builder`

```python
builder = SimulationBuilder()
builder.add_sweep_definition(
    JSONConfiguredPythonTask.set_param_partial("beta"),
    [0.1, 0.2, 0.3, 0.4, 0.5]
)
experiment = Experiment.from_builder(builder, task, name="Beta Sweep")
experiment.run(wait_until_done=True, platform=platform)
```

### Parameter sweep — `from_template` with `CommandTask`

```python
from functools import partial
from idmtools.entities import CommandLine

def set_value(simulation, name, value):
    fix_value = round(value, 2) if isinstance(value, float) else value
    simulation.task.command.add_raw_argument(fix_value)
    simulation.tags[name] = fix_value

task = CommandTask(command=CommandLine("python3 Assets/model.py"))
ts = TemplatedSimulations(base_task=task)

sb = SimulationBuilder()
sb.add_sweep_definition(partial(set_value, name="pop_size"), [10000, 20000])
sb.add_sweep_definition(partial(set_value, name="n_days"), [100, 110])
ts.add_builder(sb)

experiment = Experiment.from_template(ts, name="Command Task Sweep")
experiment.run(wait_until_done=True, platform=platform)
```

See [Parameter Sweeps](tutorials/parameter-sweeps.md) for more patterns including ARM sweeps.

---

## Analyzer

```python
class MyAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(filenames=["output/result.json"])

    def filter(self, simulation) -> bool:
        # Optional: return False to skip a simulation
        return int(simulation.tags.get("run_number", 0)) > 0

    def map(self, data, simulation):
        # Called once per simulation — return what you need
        return data[self.filenames[0]]

    def reduce(self, all_data):
        # Called once with all map() results aggregated
        for simulation, result in all_data.items():
            print(f"{simulation.id}: {result}")

with Platform("CALCULON") as platform:
    manager = AnalyzeManager(
        ids=[("your-experiment-id", ItemType.EXPERIMENT)],
        analyzers=[MyAnalyzer()]
    )
    manager.analyze()
```

See [Data Analysis](data-analysis/index.md) for CSV analyzers, `parse=False`, multiple analyzers, and `PlatformAnalysis` (SSMT).

---

## Platform Configuration

`idmtools.ini` is optional — all values can also be passed directly to `Platform()`.

=== "COMPS"

    ```ini
    [COMPS]
    type = COMPS
    endpoint = https://comps.idmod.org
    environment = Calculon
    ```
    ```python
    platform = Platform("COMPS")
    ```

=== "Slurm"

    ```ini
    [Slurm_Local]
    type = SLURM_LOCAL
    job_directory = /path/to/jobs
    ```
    ```python
    platform = Platform("Slurm_Local")
    # without .ini:
    platform = Platform("Slurm_Local", job_directory="/path/to/jobs")
    ```

=== "Container"

    ```ini
    [My_container]
    type = Container
    job_directory = /path/to/jobs
    ```
    ```python
    platform = Platform("My_container")
    # without .ini:
    platform = Platform("Container", job_directory="/path/to/jobs")
    ```

---

## CLI Quick Reference

```bash
idmtools --help                                    # all top-level commands
idmtools version                                   # installed package versions
idmtools info plugins platform-aliases             # list all platform aliases & options

# Container platform
idmtools container jobs                            # list running jobs
idmtools container status --exp-id <id>            # check experiment status
idmtools container cancel --exp-id <id>            # cancel a job
idmtools container history                         # job history

# Slurm platform
idmtools slurm <job_dir> get-status --exp-id <id>  # experiment status
idmtools slurm <job_dir> status-report             # status report

# COMPS platform
idmtools comps <config_block> login                # login to COMPS
idmtools comps <config_block> download             # download outputs
idmtools comps <config_block> singularity          # singularity commands
```

See [CLI Reference](cli/index.md) for the full command list with example output.
