# Models API reference

Task and model implementations for different programming languages and frameworks.

## Overview

The `idmtools_models` package provides task implementations for running models written in various languages (Python, R) and with different frameworks.

## Task types quick reference

| Task class | Description |
|------------|-------------|
| `PythonTask` | Run Python scripts directly |
| `JSONConfiguredPythonTask` | Python scripts with JSON config file |
| `JSONConfiguredTask` | Generic scripts with JSON config file |
| `TemplatedScriptTask` | Scripts generated from templates |
| `CommandTask` | Run arbitrary command-line commands |
| `DockerTask` | Run tasks inside a Docker container |
| `SingularityJSONConfiguredPythonTask` | Python scripts in Singularity containers |
| `SingularityJSONConfiguredTask` | Generic scripts in Singularity containers |

## Python models

### PythonTask

Execute Python scripts with parameters:

```python
from idmtools_models.python.python_task import PythonTask

task = PythonTask(
    script_path="model.py",
    python_path="python"
)

# Set parameters
task.parameters = {
    "population": 10000,
    "beta": 0.5,
    "gamma": 0.1
}
```

**Key Attributes:**

- `script_path` - Path to script
- `python_path` - Python executable
- `parameters` - Dictionary of parameters
- `command` - Generated command

**Key Methods:**

- `set_parameter(name, value)` - Set parameter
- `get_parameter(name)` - Get parameter
- `add_asset(path)` - Add input file

**Example:**
```python
# Create task
task = PythonTask(script_path="sir_model.py")

# Configure
task.parameters = {"beta": 0.5, "gamma": 0.1}
task.add_asset("config.json")
task.add_asset("data.csv")

# Create simulation
sim = Simulation.from_task(task)
```

### JSONConfiguredPythonTask

Python task with JSON configuration:

```python
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

task = JSONConfiguredPythonTask(
    script_path="model.py",
    config_filename="config.json"
)

task.set_parameter("beta", 0.5)
# Creates config.json with: {"beta": 0.5}
```

**Features:**

- Automatic JSON config file generation
- Parameter validation
- Nested parameter support

**Example:**

```python
task = JSONConfiguredPythonTask(
    script_path="model.py",
    config_filename="params.json"
)

task.set_parameter("model.beta", 0.5)
task.set_parameter("output.format", "csv")
# Generates nested JSON structure
```

## R models

### RTask (via CommandTask)

Execute R scripts:

```python
from idmtools.entities.command_task import CommandTask

task = CommandTask(command="Rscript model.R")
task.add_asset("model.R")
```

**With Parameters:**
```python
# Pass via command line
task = CommandTask(command=f"Rscript model.R {beta} {gamma}")

# Or via config file
task = CommandTask(command="Rscript model.R config.json")
```

**Example:**
```python
import json

# Create R task
task = CommandTask(command="Rscript sir_model.R config.json")
task.add_asset("sir_model.R")

# Create config
config = {"beta": 0.5, "gamma": 0.1, "population": 10000}
with open("config.json", "w") as f:
    json.dump(config, f)

task.add_asset("config.json")
```

## Templated scripts

### TemplatedScriptTask

Use templates for configuration:

```python
from idmtools_models.templated_script_task import TemplatedScriptTask

# Python script template
python_template = """
population = {{population}}
beta = {{beta}}
gamma = {{gamma}}

def run_model():
    # model code using variables above
    ...
"""

task = TemplatedScriptTask(
    script_path="model.py",
    template_content=python_template
)

task.parameters = {
    "population": 10000,
    "beta": 0.5,
    "gamma": 0.1
}
# Template variables substituted before execution
```

**Features:**

- Jinja2 template syntax
- Variable substitution
- Conditional logic
- Loops and filters

**Advanced Example:**
```python
template = """
# Generated configuration
{% if use_intervention %}
intervention_day = {{intervention_day}}
intervention_effectiveness = {{effectiveness}}
{% endif %}

parameters = {
    "beta": {{beta}},
    "gamma": {{gamma}},
    {% for key, value in extra_params.items() %}
    "{{key}}": {{value}},
    {% endfor %}
}
"""

task = TemplatedScriptTask(
    script_path="model.py",
    template_content=template
)

task.parameters = {
    "use_intervention": True,
    "intervention_day": 30,
    "effectiveness": 0.5,
    "beta": 0.7,
    "gamma": 0.1,
    "extra_params": {"duration": 365, "timestep": 1}
}
```

### Template files

Load templates from files:

```python
# config_template.json
"""
{
    "population": {{population}},
    "parameters": {
        "beta": {{beta}},
        "gamma": {{gamma}}
    },
    "output": {
        "format": "{{output_format}}",
        "directory": "{{output_dir}}"
    }
}
"""

# Create task
task = TemplatedScriptTask(
    script_path="model.py",
    template_path="config_template.json",
    template_output_filename="config.json"
)

task.parameters = {
    "population": 10000,
    "beta": 0.5,
    "gamma": 0.1,
    "output_format": "csv",
    "output_dir": "./results"
}
```

## Generic models

### Generic command tasks

Run any executable:

```python
from idmtools.entities.command_task import CommandTask

# Julia
task = CommandTask(command="julia simulation.jl")

# Compiled executable
task = CommandTask(command="./model --config config.txt")

# Shell script
task = CommandTask(command="bash run_analysis.sh")

# Python with arguments
task = CommandTask(
    command="python model.py --beta 0.5 --gamma 0.1 --output results.json"
)
```

## Docker tasks

### DockerTask

Run in Docker container:

```python
from idmtools_platform_container.docker_task import DockerTask

task = DockerTask(
    image="python:3.11-slim",
    command="python model.py"
)

task.add_asset("model.py")
task.docker_config = {
    "mem_limit": "4g",
    "cpus": 2.0
}
```

**Key Attributes:**

- `image` - Docker image name
- `command` - Command to run
- `docker_config` - Docker configuration

**Example:**
```python
# Use custom image
task = DockerTask(
    image="myrepo/simulation:latest",
    command="python run.py config.json"
)

# Configure resources
task.docker_config = {
    "mem_limit": "8g",
    "cpus": 4.0,
    "gpus": "all",
    "environment": {
        "NUM_THREADS": "4"
    }
}
```

## Task utilities

### Parameter management

```python
# Set parameter
task.set_parameter("beta", 0.5)

# Get parameter
beta = task.get_parameter("beta")

# Set multiple
task.parameters.update({
    "beta": 0.5,
    "gamma": 0.1,
    "population": 10000
})

# Check if parameter exists
if "beta" in task.parameters:
    print(f"Beta: {task.parameters['beta']}")
```

### Asset management

```python
# Add single file
task.add_asset("config.json")

# Add with custom path
task.add_asset_file("local.txt", relative_path="inputs/remote.txt")

# Add directory
task.add_assets_directory("data/")

# Add multiple
for file in ["file1.csv", "file2.csv", "file3.csv"]:
    task.add_asset(file)
```

### Command construction

```python
# CommandTask automatically builds command
task = CommandTask(command="python model.py")

# Add arguments
task.command.add_argument("--beta")
task.command.add_argument("0.5")

# Or use command string
task = CommandTask(
    command="python model.py --beta 0.5 --gamma 0.1"
)

# Get full command
print(task.command)  # "python model.py --beta 0.5 --gamma 0.1"
```

## Model specific tasks

### EMOD task (if installed)

```python
# Requires emodpy

task = EmodTask.from_default()
task.set_parameter("Run_Number", 0)
task.set_parameter("Simulation_Duration", 365)
```


## Task validation

### Pre-execution validation

```python
def validate_parameters(task):
    """Validate task parameters before execution."""
    beta = task.get_parameter("beta")
    gamma = task.get_parameter("gamma")

    if beta <= 0 or gamma <= 0:
        raise ValueError("Beta and gamma must be positive")

    if beta <= gamma:
        print("Warning: R0 < 1, epidemic will not spread")

# Add validation hook
task.pre_creation_hooks.append(validate_parameters)
```

### Asset validation

```python
def validate_assets(task):
    """Ensure required assets exist."""
    required_files = ["config.json", "model.py"]

    for filename in required_files:
        if filename not in task.assets:
            raise FileNotFoundError(f"Required asset missing: {filename}")

task.pre_creation_hooks.append(validate_assets)
```

## Custom tasks

### Creating custom task types

```python
from idmtools.entities.itask import ITask

class CustomTask(ITask):
    """Custom task implementation."""

    def __init__(self, custom_param=None):
        super().__init__()
        self.custom_param = custom_param

    def pre_creation(self, platform):
        """Setup before execution."""
        # Custom pre-execution logic
        print(f"Preparing task with param: {self.custom_param}")

    def post_creation(self, platform):
        """Cleanup after execution."""
        # Custom post-execution logic
        pass

    def gather_assets(self):
        """Define task assets."""
        return self.assets

# Use custom task
task = CustomTask(custom_param="value")
sim = Simulation.from_task(task)
```

### Task inheritance

```python
class EnhancedPythonTask(PythonTask):
    """Enhanced Python task with additional features."""

    def __init__(self, *args, virtual_env=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.virtual_env = virtual_env

    def pre_creation(self, platform):
        """Activate virtual environment."""
        if self.virtual_env:
            self.python_path = f"{self.virtual_env}/bin/python"
        super().pre_creation(platform)

# Use enhanced task
task = EnhancedPythonTask(
    script_path="model.py",
    virtual_env="/path/to/venv"
)
```

## Best practices

### 1. Parameter naming

```python
# Good: Clear, descriptive names
task.set_parameter("transmission_rate", 0.5)
task.set_parameter("recovery_rate", 0.1)
task.set_parameter("initial_population", 10000)

# Avoid: Ambiguous names
task.set_parameter("x", 0.5)
task.set_parameter("y", 0.1)
```

### 2. Type safety

```python
# Validate parameter types
def set_typed_parameter(task, name, value, expected_type):
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be {expected_type}")
    task.set_parameter(name, value)

# Use
set_typed_parameter(task, "beta", 0.5, float)
set_typed_parameter(task, "days", 365, int)
```

### 3. Asset organization

```python
# Good: Organized asset structure
task.add_asset_file("input.csv", relative_path="data/input.csv")
task.add_asset_file("config.json", relative_path="config/settings.json")
task.add_asset_file("model.py", relative_path="scripts/model.py")

# Avoid: Flat structure with many files
task.add_asset("file1.csv")
task.add_asset("file2.csv")
# ... 50 more files ...
```

## See also

- [Core API](core.md) - Core classes and interfaces
- [Platforms API](platforms.md) - Platform implementations
- [Python Models Tutorial](../tutorials/python-models.md) - Hands-on examples

## Full API documentation

For complete API documentation:

- `idmtools_models.python.python_task`
- `idmtools_models.templated_script_task`
- `idmtools.entities.command_task`
- `idmtools_platform_container.docker_task`
