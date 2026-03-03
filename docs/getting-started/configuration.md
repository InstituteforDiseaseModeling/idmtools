# Configuration

Learn how to configure idmtools for your environment.

## Configuration File

`idmtools.ini` is an optional configuration file for defining platforms. When present, idmtools automatically searches for it starting from the current working directory and walking up through parent directories until it finds one or reaches the filesystem root.

You do not need this file — platforms can always be configured directly in code by passing parameters to `Platform()`.

## Platform Configuration

### COMPS

```ini
# idmtools.ini
[COMPS]
type = COMPS
endpoint = https://comps.idmod.org
environment = Calculon
```

```python
platform = Platform("COMPS")
```

### Slurm

```ini
# idmtools.ini
[Slurm_Local]
type = SLURM_LOCAL
job_directory = MY_JOB_DIRECTORY
```

```python
# With idmtools.ini
platform = Platform("Slurm_Local")

# Without idmtools.ini
platform = Platform("Slurm_Local", job_directory="MY_JOB_DIRECTORY")
```

### Container

```ini
# idmtools.ini
[My_container]
type = Container
job_directory = MY_JOB_DIRECTORY
```

```python
# With idmtools.ini
platform = Platform("My_container")

# Without idmtools.ini
platform = Platform("Container", job_directory="MY_JOB_DIRECTORY")
```

## Next Steps

- [Quick Start](quickstart.md) - Run your first simulation
- [User Guide](../user-guide/index.md) - Learn more about idmtools
- [Platform Guides](../platforms/index.md) - Platform-specific configuration
