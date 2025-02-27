<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [User Installation](#user-installation)
  - [Recommended install](#recommended-install)
  - [Advanced install](#advanced-install)
  - [Installing development/early release versions](#installing-developmentearly-release-versions)
    - [IDMOD's PyPI staging registry](#idmods-pypi-staging-registry)
  - [Pre-requisites](#pre-requisites)
- [Reporting issues](#reporting-issues)
- [Requesting a feature](#requesting-a-feature)
- [Development documentation](#development-documentation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
# Instruction for running idmtools on macOS
## Pre-requisites
- Python 3.8/3.9/3.10/3.11/3.12 x64-bit
- OS:
  - macOS (10.15 Catalina or later) 
- Docker or Docker Desktop for macOS (required for the container platform)
- Only support Intel based **x86_64** architecture if you want to run emodpy related disease models on **Docker** container platform. Apple based ARM architecture currently is not supported. 

## Installation
- Create and activate a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  
    ```
- Install emodpy related disease models if running emod related disease models 
    ```bash
    pip install emodpy-xxx --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```
  xxx can be replaced with the specific emodpy package name you want to install.

- Install/update the latest idmtools related packages
    ```bash
    pip install idmtools\[full\] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple --full-reinstall --no-cache-dir --upgrade
    ```
- Optional: Install only idmtools **container** packages if you are only interested in running simulations on local Docker container platform
    ```bash
    pip install idmtools\[container\] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple --full-reinstall --no-cache-dir --upgrade
    ```
  
## Run examples
- emodpy-malaria examples for running container platform at: https://github.com/EMOD-Hub/emodpy-malaria/tree/main/examples-container
- emodpy-malaria examples for running idm COMPS platform at: https://github.com/EMOD-Hub/emodpy-malaria/tree/main/examples
- idmtools examples for running simple python script in container platform: https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/examples/platform_container
- idmtools examples for running simple python script in COMPS platform: https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/examples/python_model
