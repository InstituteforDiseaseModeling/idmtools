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


## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [Configuration](configuration.md) - Configure your environment
- [Quick Start](quickstart.md) - Complete walkthrough


## Need Help?

- Check the [FAQ](../faq/index.md)
- Browse [Tutorials](../tutorials/index.md)
- See [Examples](../user-guide/index.md)
