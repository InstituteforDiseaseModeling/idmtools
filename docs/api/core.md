# Core API Reference

Core classes and functionality for idmtools.

## Overview

The `idmtools.core` package provides the foundational classes and interfaces for building simulations, experiments, and interacting with platforms.

## Quick Reference

### Core Classes

| Class | Module | Description |
|-------|--------|-------------|
| [`Platform`](#platform) | `idmtools.core.platform_factory` | Creates a connection to a compute platform |
| [`Experiment`](#experiment) | `idmtools.entities.experiment` | A collection of simulations |
| [`Simulation`](#simulation) | `idmtools.entities.simulation` | A single model run with specific parameters |
| [`SimulationBuilder`](#simulationbuilder) | `idmtools.builders` | Builds simulations from parameter sweeps |
| `CommandLine` | `idmtools.entities` | Defines the command to execute |
| [`AssetCollection`](#assetcollection) | `idmtools.assets` | A collection of files for simulations |
| [`Asset`](#asset) | `idmtools.assets` | A single file asset |
| [`ITask`](#itask) | `idmtools.entities.itask` | Base class for all tasks |
| [`IAnalyzer`](../data-analysis/analyzers.md) | `idmtools.entities` | Base class for analyzers |

### Common Methods

```python
# Experiment
experiment = Experiment.from_builder(builder, task, name="My Experiment")
experiment.run(platform=platform, wait_until_done=True)

# SimulationBuilder
builder = SimulationBuilder()
builder.add_sweep_definition(callback, values)

# Task
task.set_parameter(key, value)
task.common_assets.add_assets(asset_collection)
task.transient_assets.add_asset("file.py")

# Asset
Asset(filename="config.json", content='{"key": "value"}')
AssetCollection.from_id_file("path/to/id_file.id")

# Platform
platform = Platform("PlatformName")
```

## Platform Factory

### Platform

The main entry point for creating platform instances:

```python
from idmtools.core.platform_factory import Platform

# Create platform
platform = Platform("COMPS", endpoint="...", environment="...")
```

**Key Methods:**

- `get_item()` - Retrieve entity by ID
- `create_items()` - Create entities on platform
- `get_directory()` - Get working directory for entity
- `refresh_status()` - Update entity status

## Entities

### IEntity

Base interface for all entities: `Experiment`, `Simulation`, `Suite`, `ITask`, `AssetCollection`, `IWorkflowItem`

**Methods:**

- `pre_creation()` - Hook called before creation
- `post_creation()` - Hook called after creation
- `to_dict()` - Serialize to dictionary
- `from_dict()` - Deserialize from dictionary

### Simulation

Represents a single simulation:

```python
from idmtools.entities.simulation import Simulation
from idmtools_models.python.python_task import PythonTask

task = PythonTask(script_path="model.py")
sim = Simulation.from_task(task, name="My Simulation")
```

**Key Methods:**

- from_task() - Create from task
- add_asset() - Add input file
- set_parameter() - Set task parameter

### Experiment

Collection of simulations:

```python
from idmtools.entities.experiment import Experiment

sims_template = TemplatedSimulations(base_task=task)
experiment = Experiment.from_template(sims_template, name="My Experiment")
experiment.run(platform=platform, wait_until_done=True)
```


**Key Methods:**

- from_task() - Create from Task
- from_template() - Create from TemplatedSimulations
- from_builder() - Create from SimulationBuilder
- run() - Execute on platform
- refresh_status() - Update status

### Suite

Collection of experiments:

```python
from idmtools.entities.suite import Suite

suite = Suite(name="Complete Study")
suite.add_experiment(exp1)
suite.add_experiment(exp2)
suite.run(platform=platform)
```

**Key Methods:**

- `add_experiment()` - Add experiment to suite
- `run()` - Execute all experiments

## Tasks

### ITask

Base interface for tasks:

**Methods:**

- `set_parameter()` - Set parameter value
- `get_parameter()` - Get parameter value
- `pre_creation()` - Pre-execution hook

### CommandTask

Execute shell commands:

```python
from idmtools.entities.command_task import CommandTask

task = CommandTask(command="python model.py --beta 0.5")
task.add_asset("model.py")
```

**Attributes:**

- `command` - Command to execute
- `parameters` - Command parameters

## Builders

### SimulationBuilder

Build parameter sweeps:

```python
from idmtools.builders import SimulationBuilder

builder = SimulationBuilder()
builder.add_sweep_definition(
    lambda sim, beta: sim.task.set_parameter("beta", beta),
    [0.1, 0.2, 0.3, 0.4, 0.5]
)
```

**Key Methods:**

- `add_sweep_definition()` - Add parameter sweep
- `build()` - Generate simulations

## Assets

### AssetCollection

Manage input files:

```python
from idmtools.assets import AssetCollection

assets = AssetCollection()
assets.add_asset("config.json")
assets.add_directory("data/")
```

**Key Methods:**

- `add_asset()` - Add single file
- `add_directory()` - Add directory
- `get_asset()` - Get asset by name
- `remove_asset()` - Remove asset

### Asset

Represents a single file:

```python
from idmtools.assets import Asset

asset = Asset(
    absolute_path="/path/to/file.txt",
    relative_path="inputs/file.txt"
)
```

**Attributes:**

- `absolute_path` - Source file path
- `relative_path` - Destination path in simulation
- `filename` - File name

## Platform Interface

### IPlatform

Interface all platforms implement:

**Key Methods:**

- `create_items()` - Create entities
- `get_item()` - Retrieve entity
- `refresh_status()` - Update status
- `get_directory()` - Get working directory
- `get_files()` - List entity files
- `retrieve_output_files()` - Download outputs


### EntityStatus

Entity status values:

```python
from idmtools.core import EntityStatus

EntityStatus.CREATED
EntityStatus.RUNNING
EntityStatus.SUCCEEDED
EntityStatus.FAILED
EntityStatus.CANCELLED
```

## Configuration

### IdmConfigParser

Configuration file parser:

```python
from idmtools.core.idmtools_ini import IdmConfigParser

config = IdmConfigParser.load()
comps_config = config.get_section("COMPS")
```

**Key Methods:**

- `load()` - Load configuration
- `get_section()` - Get config section
- `get_option()` - Get config option


## Hooks and Callbacks

### Pre/Post Creation Hooks

```python
def on_pre_creation(item, platform):
    print(f"Creating {item.name}")

def on_post_creation(item, platform):
    print(f"Created {item.uid}")

experiment.pre_creation_hooks.append(on_pre_creation)
experiment.post_creation_hooks.append(on_post_creation)
```

## See Also

- [Models API](models.md) - Task implementations
- [Platforms API](platforms.md) - Platform implementations
- [User Guide](../user-guide/index.md) - Usage examples
- [Tutorials](../tutorials/index.md) - Hands-on examples
