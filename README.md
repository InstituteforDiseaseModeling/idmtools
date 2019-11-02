# IDM Modeling Tools

# Installation 
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

You can also install just the individual packages to create minimal environments

- `pip install idmtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Core package
- `pip install idmtools-cli --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for COMPS
- `pip install idmtools-platform-local --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for Local Platform
- `pip install idmtools-models --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Python and generic models
- `pip install idmtools-model-dtk --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - EMOD Model support

## Pre-requisites
- Python 3.6/3.7 x64
- Docker(Required for the local platform)

## Development Environment Setup

Clone the repository:
```bash
> git clone https://github.com/InstituteforDiseaseModeling/idmtools.git
```

To setup your environment, you can run `python dev_scripts/bootstrap.py`. This will install all the tools. From then on you can use `pymake` to run common development tasks.

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
setup-dev   -   Setup dev environment(assumes you already have a virtualenv)
clean       -   Clean up temporary files
lint        -   Lint package and tests
test        -   Run Unit tests
test-all    -   Run Tests that require docker and external systems
coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`

Use will also need to ensure you have logged in to the staging docker repo using
`docker login idm-docker-staging.idmod.org`

### IDE/Runtime Setup
For development purpose, it is important to add the following folders as to your `PYTHONPATH` (In PyCharm, right click and `Mark Directoy as > Source Root`):
- `idmtools/idmtools_core`
- `idmtools/idmtools_cli`
- `idmtools/idmtools_platform_local`
- `idmtools/idmtools_platform_comps`
- `idmtools/idmtools_model_emod`
- `idmtools/idmtools_models`
- `idmtools/idmtools_test`

### Running specific tests from the command line

From within a project directory such a local data
`python -m unittest tests.test_docker_operations.TestDockerOperations.test_create_stack_starts`

To enable docker tests and comps test you can do the following on Linux 
`export DOCKER_TESTS=1
python -m unittest tests.test_docker_operations.TestDockerOperations.test_create_stack_starts
`
or on Windows
`
set DOCKER_TESTS=1
python -m unittest tests.test_docker_operations.TestDockerOperations.test_create_stack_starts
`

Lastly, you can do also run the tests without setting the environment variables directly like so
`DOCKER_TESTS=1 python -m unittest tests.test_docker_operations.TestDockerOperations.test_create_stack_starts`

# Troubleshppting the Devevelopment Environment

1. Docker Auth issues.

   Idmtools currently does not prompt users for docker credentials. Because of this you must login
   beforehand using `docker login idm-docker-staging.packages.idmod.org`
2.  Docker image not found

   Check that the idmt