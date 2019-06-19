# IDM Modeling Tools

## Pre-requisites
- Python 3.6/3.7 x64
- Docker

## Development Environment Setup

Clone the repository:
```bash
> git clone https://github.com/InstituteforDiseaseModeling/idmtools.git
```

Install the packages in dev mode with the `test` extra (from repository folder).
```bash
> cd idmtools_core
> pip install -e .[test,3.6] --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
> cd ..
> cd idmtools_local_runner
> pip install -e .[test]
> cd ..
> cd idmtools_models_collection
> pip install -e .[test]
```

Create a Docker network named `idmtools_network`:
```bash
> docker network create idmtools_network
```

Navigate to the `idmtools_local_runner` folder and start the local runner:
```bash
> docker-compose up
```

For development purpose, it is important to add the following folders as to your `PYTHONPATH` (In PyCharm, right click and `Mark Directoy as > Source Root`):
- `idmtools/idmtools_core`
- `idmtools/idmtools_local_runner`
- `idmtools/idmtools_models_collection`

## Running the examples in Jupyter
Ensure that the local runner is up:
```bash
> cd idmtools_local_runner
> docker-compose up
```

Navigate to the `examples` folder and run:
```bash
> docker-compose up
```

You can now open a browser and navigate to: http://localhost:8888.

The examples are available in the `work/notebooks` folder.
