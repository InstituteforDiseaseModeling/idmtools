# Getting Started

Welcome to idmtools! This section will help you get up and running quickly.

## Prerequisites

- **Python**: Versions 3.10, 3.11, 3.12, 3.13, or 3.14 are supported.
- **Operating System**:
  - Windows 10+ Pro or Enterprise
  - Linux
  - macOS (10.15 Catalina or later)
- **Docker** (optional): Required for Container platform

## Installation

Choose an installation method based on your needs:

### Full Installation

Install all idmtools packages:

```bash
pip install idmtools[full]
```

This installs: core, CLI, models, and all platform plugins.

### Platform-Specific Installation

Install only what you need:

=== "COMPS Platform"

    ```bash
    pip install idmtools[idm]
    ```

    Includes: core, CLI, models, COMPS platform

=== "Slurm Platform"

    ```bash
    pip install idmtools[slurm]
    ```

    Includes: core, CLI, models, General platform, Slurm platform

=== "Container Platform"

    ```bash
    pip install idmtools[container]
    ```

    Includes: core, CLI, models, General platform, Container platform

## Quick Start

Create your first simulation in 3 steps:

### 1. Import idmtools

```python
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
```

### 2. Create a Task

```python
task = JSONConfiguredPythonTask(
    script_path="my_model.py",
    parameters={"param1": 10, "param2": 20}
)
```

### 3. Run Experiment

```python
# Create experiment
experiment = Experiment.from_task(
    task,
    name="My First Experiment"
)

# Get platform and run
with Platform("Local") as platform:
    experiment.run(wait_until_done=True)
```

## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [Configuration](configuration.md) - Configure your environment
- [Quick Start Tutorial](quickstart.md) - Complete walkthrough
- [Data Analysis](../data-analysis/index.md) - Analyze simulation outputs with Analyzers, AnalyzeManager, and PlatformAnalysis

## Need Help?

- Check the [FAQ](../faq/index.md)
- Browse [Tutorials](../tutorials/index.md)
- See [Examples](../user-guide/index.md)
