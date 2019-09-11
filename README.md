# IDM Modeling Tools

## Pre-requisites
- Python 3.6/3.7 x64
- Docker

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

### IDE/Runtime Setup
For development purpose, it is important to add the following folders as to your `PYTHONPATH` (In PyCharm, right click and `Mark Directoy as > Source Root`):
- `idmtools/idmtools_core`
- `idmtools/idmtools_cli`
- `idmtools/idmtools_platform_local`
- `idmtools/idmtools_platform_comps`
- `idmtools/idmtools_model_dtk`
- `idmtools/idmtools_models`
- `idmtools/idmtools_test`

### Manual Install

Alternatively, you can install the packages manually by doing the following. 
```bash
> cd idmtools_core
> pip install -e .[test] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
> cd ..
> cd idmtools_cli
> pip install -e .[test]
> cd idmtools_platform_local
> pip install -e .[test]
> cd ..
> cd idmtools_platform_comps
> pip install -e .[test]
> cd ..
> cd idmtools_model_dtk
> pip install -e .[test]
> cd ..
> cd idmtools_models
> pip install -e .[test]
> cd ..
> cd idmtools_test
> pip install -e .

```

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

## Running the examples in Jupyter

Navigate to the `examples` folder and run:
```bash
> docker-compose up
```

You can now open a browser and navigate to: http://localhost:8888.

The examples are available in the `work/notebooks` folder.
