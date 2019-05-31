# IDM Modeling Tools

## Pre-requisites
Python 3.7

## Development installation steps
Create a virtual environment
```bash
> virtualenv idmtools
```

Install the packages in dev mode
```bash
> cd idmtools_core
> pip install -e . --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
> cd ..
> cd idmtools_local_runner
> pip install -e .
> cd ..
> cd idmtools_models_collection
> pip install -e .
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

For development purpose, it is important to set the following folders as `Source Root` (on PyCharm, right click and `Mark Directoy as > Source Root`):
- `idmtools/idmtools`
- `idmtools/idmtools_local`
- `idmtools/idmtools_models`

## Running the examples in Jupyter
Ensure that the local runner is up:
```bash
> cd idmtools_local
> docker-compose up
```

Navigate to the `examples` folder and run:
```bash
> docker-compose up
```

You can now open a browser and navigate to: http://localhost:8888.

The examples are available in the `work/notebooks` folder.
