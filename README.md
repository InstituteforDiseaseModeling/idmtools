# Packages Status
![Staging: idmtools-core](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-core/badge.svg?branch=dev)
![Staging: idmtools-cli](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-cli/badge.svg?branch=dev)
![Staging: idmtools-models](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-models/badge.svg?branch=dev)
![Staging: idmtools-platform-comps](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-comps/badge.svg?branch=dev)
![Staging: idmtools-platform-slurm](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-slurm/badge.svg?branch=dev)
![Staging: idmtools-test](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-test/badge.svg?branch=dev)

# Other status
![Dev: Rebuild documentation](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Rebuild%20documentation/badge.svg?branch=dev)
![Lint](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Lint/badge.svg?branch=dev)

# IDM Modeling Tools

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [User Installation](#user-installation)
  - [Recommended install](#recommended-install)
  - [Advanced install](#advanced-install)
  - [Installing development/early release versions](#installing-developmentearly-release-versions)
    - [PyPI](#pypi)
  - [Pre-requisites](#pre-requisites)
- [Reporting issues](#reporting-issues)
- [Requesting a feature](#requesting-a-feature)
- [Development documentation](#development-documentation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Installation

Documentation is located at https://docs.idmod.org/projects/idmtools/en/latest/. 

To build the documentation locally, do the following:

1. Create and activate a venv.
2. Navigate to the root directory of the repo and enter the following:

    ```
    pip install -r dev_scripts/package_requirements.txt
    pip install -r docs/requirements.txt
    python dev_scripts/bootstrap.py
    cd docs
    make html
    ```
3. (Optional) To automatically serve the built docs locally in your browser, enter the following from
   the root directory:

    ```
    python dev_scripts/serve_docs.py
    ```

## Recommended install

- The recommended installation is to use:
```bash
pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install all idmtools packages, except the idmtools-test package. The installation includes core, CLI, models, COMPS, General, Container, and Slurm platforms.
- For only run simulations on COMPS:
```bash
pip install idmtools[idm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the idmtools core, CLI, models, and COMPS platform.

- For only run simulations in Slurm cluster:
```bash
pip install idmtools[slurm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the idmtools core, CLI, models, slurm_utils, and Slurm platform.

- For only run simulations in Docker container locally:
```bash
pip install idmtools[container] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the idmtools core, CLI, models, General, and Container platforms.

- For run unittests, you may need to install the idmtools-test package:
```bash
pip install idmtools-test --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

## Advanced install
You can also install just the individual packages to create minimal environments:

- `pip install idmtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Core package
- `pip install idmtools-cli --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for COMPS
- `pip install idmtools-models --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Python and generic models
- `pip install idmtools-platform-general --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for File/Process Platforms
- `pip install idmtools-platform-slurm --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for Slurm Platform
- `pip install idmtools-platform-container --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for Container Platform
- `pip install idmtools-test --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Test package

## Installing development/early release versions

Development versions are available through both IDM's pypi registry and through Github.

### IDMOD's PyPI staging registry

If you have your authentication defined in your pip.conf or pip.ini file, you can use the following commands to install from staging:
- `pip install idmtools --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Core package
- `pip install idmtools-cli --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for COMPS
- `pip install idmtools-models --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Python and generic models
- `pip install idmtools-platform-general --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for File/Process Platforms
- `pip install idmtools-platform-slurm --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for Slurm Platform
- `pip install idmtools-platform-container --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for Container Platform
- `pip install idmtools-test --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Test package

## Pre-requisites
- Python 3.8/3.9/3.10/3.11/3.12 x64-bit
- Windows 10 Pro or Enterprise, or a Linux operating system
- Docker(required for the container platform)
  On Windows, please use Docker Desktop 4.0.0 or later

# Reporting issues

Include the following information in your post:

-   Describe what you expected to happen.
-   If possible, include a `minimal reproducible example` to help us
    identify the issue. This also helps check that the issue is not with
    your own code.
-   Describe what actually happened. Include the full traceback if there
    was an exception.

You can report an issue directly on GitHub or by emailing [idmtools-issue@idmod.org](mailto:idmtools-issue@idmod.org). Please include steps to reproduce the issue

# Requesting a feature 

You can request a feature but opening a ticket on the repo or by emailing [idmtools-feature@idmod.org](mailto:idmtools-feature@idmod.org)

# Development documentation

[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/InstituteforDiseaseModeling/idmtools)

See [DEVELOPMENT_README.md](DEVELOPMENT_README.md)