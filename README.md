
# Packages Status
![Staging: idmtools-core](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-core/badge.svg?branch=dev)
![Staging: idmtools-cli](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-cli/badge.svg?branch=dev)
![Staging: idmtools-models](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-models/badge.svg?branch=dev)
![Staging: idmtools-platform-comps](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-comps/badge.svg?branch=dev)
![Staging: idmtools-platform-local](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-local/badge.svg?branch=dev)
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
  - [Advanced Install](#advanced-install)
  - [Installing Development/Early Release Versions](#installing-developmentearly-release-versions)
    - [PyPI](#pypi)
  - [Pre-requisites](#pre-requisites)
- [Reporting issues](#reporting-issues)
- [Requesting a feature](#requesting-a-feature)
- [Development Documentation](#development-documentation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Installation

Documentation is located at https://docs.idmod.org/projects/idmtools/en/latest/. 

## Recommended install

The recommended install is to use
```bash
pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the core tools, the cli, the comps and local platforms, support for EMOD models, and python models

If you do not need the local platform, you can use the following command
```bash
pip install idmtools[idm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the core tools, the cli, the comps, support for EMOD models, and python models

If you are Python 3.6, you will also need to run
```bash
pip install dataclasses
```
## Advanced Install
You can also install just the individual packages to create minimal environments

- `pip install idmtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Core package
- `pip install idmtools-cli --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for COMPS
- `pip install idmtools-platform-local --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for Local Platform
- `pip install idmtools-models --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Python and generic models

## Installing Development/Early Release Versions

Development versions are available through both IDM's pypi registry and through Github.

### PyPI

If you have your authentication defined in your pip.conf or pip.ini file, you can use the following commands to install from staging
- `pip install idmtools --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Core package
- `pip install idmtools-cli --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for COMPS
- `pip install idmtools-platform-local --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for Local Platform
- `pip install idmtools-models --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Python and generic models

## Pre-requisites
- Python 3.6/3.7/3.8 x64
- Docker(Required for the local platform)
  On Windows, please use Docker Desktop 2.1.0.5 or 2.2.0.1

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

# Development Documentation

See [DEVELOPMENT_README.md](DEVELOPMENT_README.md)