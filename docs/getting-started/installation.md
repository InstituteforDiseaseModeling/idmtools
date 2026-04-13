# Installation

## Prerequisites

Before installing idmtools, ensure you have:

- **Python 3.10+ (64-bit)** - Check with `python --version`
- **pip** - Python package installer
- **Virtual environment** (recommended)

## Create Virtual Environment

It's recommended to use a virtual environment:

=== "Windows"

    ```bash
    python -m venv idmtools
    idmtools\Scripts\activate
    ```

=== "Linux/macOS"

    ```bash
    python -m venv idmtools
    source idmtools/bin/activate
    ```

## Installation Options

### Full Installation

Install everything:

```bash
pip install idmtools[full]
```

**Includes:**

* idmtools-core

* idmtools-cli

* idmtools-models

* idmtools-platform-comps

* idmtools-platform-container

* idmtools-platform-general

* idmtools-platform-slurm

### Platform-Specific

Choose based on your compute platform:

#### COMPS Platform

```bash
pip install idmtools[idm]
```

#### Slurm Platform

```bash
pip install idmtools[slurm]
```

#### Container (Docker) Platform

```bash
pip install idmtools[container]
```

Requires Docker or Docker Desktop.

### Individual Packages

Install only what you need:

```bash
pip install idmtools                     # Core only
pip install idmtools-cli                 # CLI tools
pip install idmtools-models              # Python/R models
pip install idmtools-platform-comps      # IDM COMPS platform related packages
pip install idmtools-platform-slurm      # Slurm platform related packages
pip install idmtools-platform-container  # Local Container platform related packages
pip install idmtools-platform-general    # File and Process platform packages
```

## Verify Installation

```bash
# Using CLI
idmtools --version

# Or using Python
python -c "import idmtools; print(idmtools.__version__)"
```
Note, Run the above command after installing the latest packages.

## Project Structure

A typical user project that depends on idmtools looks like this:

```
my_project/
├── model.py              # Your simulation model
├── run_experiment.py     # Experiment configuration & submission
├── analyzer.py           # Post-processing / analysis
├── config.json           # Model parameters
├── idmtools.ini          # Platform configuration (optional)
└── Assets/
    └── python_model.sif  # Singularity image (COMPS/Slurm only)
```

## Development Installation

For contributing to idmtools:

```bash
git clone https://github.com/institutefordiseasemodeling/idmtools.git
cd idmtools
python dev_scripts/bootstrap.py
```

This installs all packages in editable mode.

## Troubleshooting

### macOS Users

On macOS with square brackets in shell, escape them:

```bash
pip install idmtools\[full\]
```

### Docker Authentication

For Container platform, login to GitHub Container Registry:

```bash
echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Permission Errors

Use `--user` flag if you don't have admin rights:

```bash
pip install --user idmtools[full]
```

## Next Steps

- [Configuration](configuration.md) - Configure your environment
- [Quick Start](quickstart.md) - Run your first simulation
- [User Guide](../user-guide/index.md) - Learn the basics
