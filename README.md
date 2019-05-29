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
> cd idmtools
> pip install -e .
> cd ..
> cd idmtools_local
> pip install -e .
> cd ..
> cd idmtools_models
> pip install -e .
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