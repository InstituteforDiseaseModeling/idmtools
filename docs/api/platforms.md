# Platforms API reference

Platform implementations for different compute environments.

## Overview

The platform packages provide implementations for running simulations on various compute platforms including COMPS, Slurm, Docker containers, and local execution.

## Platform factory

### Platform

Factory for creating platform instances:

```python
from idmtools.core.platform_factory import Platform

# Create platform by name
platform = Platform("COMPS")

# With configuration
platform = Platform(
    "COMPS",
    endpoint="https://comps.idmod.org",
    environment="Bayesian"
)

# From config file
platform = Platform("COMPS", missing_ok=True)
```

**Factory Methods:**

- `Platform(name, **kwargs)` - Create platform instance
- `get_platform(name)` - Get platform class

## COMPS platform

### COMPSPlatform

IDM's on premises based and cloud based platform implementation:

```python
from idmtools.core.platform_factory import Platform

platform = Platform(
    "COMPS",
    endpoint="https://comps.idmod.org",
    environment="Nibbler",
    priority="Highest",
    num_cores=1
)
```

**Constructor Parameters:**

- `endpoint` (str) - COMPS server URL
- `environment` (str) - Environment name (Calculon(on premises), Nibbler(Azure cloud), SLURMStage, etc.)
- `priority` (str) - Job priority (Lowest, BelowNormal, Normal, AboveNormal, Highest)
- `num_cores` (int) - CPU cores per simulation
- `node_group` (str) - Target node group
- `max_workers` (int) - Max concurrent operations

**Key Methods:**

- `platform.get_item(exp_id, item_type=ItemType.EXPERIMENT)` - Get experiment by id
- `platform.get_item(exp_id, item_type=ItemType.SIMULATION)` - Get simulation by id
- `platform._experiments.platform_cancel(experiment.id)` - Cancel running experiment


**Example:**
```python
# Create platform
platform = Platform(
    "COMPS",
    endpoint="https://comps.idmod.org",
    environment="Calculon"
)

# Run experiment
experiment.run(platform=platform, wait_until_done=True)

# Filter simulations by tags
simulations = platform.filter_simulations_by_tags(
    suite_id, item_type=ItemType.SUITE,
    tags={"a": lambda v: 1 <= v <= 2, "sim_tag": "test_tag"}, entity_type=True)

# Get experiment details
exp = platform.get_item(exp_id, ItemType.EXPERIMENT)
print(f"Status: {exp.status}")
print(f"Simulations: {len(exp.simulations)}")
```


### SSMT work items


```python
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

# Create SSMT work item
wi_name = "SSMT WorkItem Example"
command = "python3 Assets/Hello_model.py"

platform = Platform('SlurmStage')
wi = SSMTWorkItem(name=wi_name, command=command, assets=AssetCollection.from_directory("Assets"))
wi.run(True, platform=platform)
```

## Slurm platform

### SlurmPlatform

HPC cluster implementation:

```python
from idmtools.core.platform_factory import Platform

platform = Platform(
    "SLURM_LOCAL",
    job_directory="/scratch/jdoe/idmtools"
)
```

**Constructor Parameters:**

- `host` (str) - Slurm head node hostname
- `username` (str) - SSH username
- `job_directory` (str) - Working directory on cluster
- `partition` (str) - Default partition/queue
- `account` (str) - Account to charge
- `time_limit` (str) - Default time limit
- ...


**Example:**
```python
# Create platform
platform = Platform("SLURM_LOCAL", job_directory=".",  mail_user="test@test.com",
                            account="test_acct", mail_type="begin", mem_per_cpu=2048)
)

# Run
experiment.run(platform=platform, wait_until_done=True)

# Check job status
experiment.refresh_status(platform)
```

## Container platform

### ContainerPlatform attributes

| Attribute | Description |
|-----------|-------------|
| `job_directory` | The directory where job data is stored. |
| `docker_image` | The Docker image to run the container. |
| `extra_packages` | Additional packages to install in the container. |
| `data_mount` | The data mount point in the container. |
| `user_mounts` | User-defined mounts for additional volume bindings. |
| `container_prefix` | Prefix for container names. |
| `force_start` | Flag to force start a new container. |
| `new_container` | Flag to start a new container. |
| `include_stopped` | Flag to include stopped containers in operations. |
| `debug` | Flag to enable debug mode. |
| `container_id` | The ID of the container being used. |
| `max_job` | The maximum number of jobs to run in parallel. |
| `retries` | The number of retries to attempt for a job. |
| `ntasks` | Number of MPI processes. If greater than 1, it triggers mpirun. |


```python
from idmtools.core.platform_factory import Platform

platform = Platform(
    "Container",
    max_workers=4,
    job_directory="/path/to/workdir"
)
```


## Platform configuration

### Configuration file

Example `~/.idmtools/idmtools.ini`:

```ini

[My_Container]
type = Container
max_workers = 4
job_dirrectory = /tmp/idmtools

```


## See also

- [Core API](core.md) - Core interfaces and classes
- [Models API](models.md) - Task implementations
- [Platform Guides](../platforms/index.md) - Platform-specific documentation
- [Tutorials](../tutorials/index.md) - Hands-on examples
