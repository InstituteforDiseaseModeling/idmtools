# IDM Modeling Tools

## Pre-requisites
Python 3.7 x64
Docker

## Development installation steps
Create a virtual environment
```bash
> virtualenv idmtools
```

Install the packages in dev mode
```bash
> cd idmtools_core
> pip install -e .[test] --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
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

Run the local runner:
```bash
> cd idmtools_local
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
