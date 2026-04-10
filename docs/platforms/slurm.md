# Slurm Platform

Comprehensive guide to using idmtools with Slurm HPC clusters.

## Overview

**Slurm** is a popular open-source workload manager for HPC clusters. idmtools provides seamless integration with Slurm clusters, allowing you to submit and manage large-scale simulation workflows.

## Key Features

- **HPC Integration**: Use existing cluster infrastructure
- **Resource Management**: Request specific CPU, memory, and GPU resources
- **Queue Control**: Submit to different partitions/queues
- **Job Arrays**: Efficient batch job submission
- **Module System**: Integration with environment modules
- **Shared Storage**: Leverage shared filesystems

## Prerequisites

### 1. Cluster Access

- SSH access to Slurm head node
- Valid cluster account
- Appropriate partition/queue permissions
- Shared filesystem access (e.g., /home, /scratch)

### 2. Installation

On your local machine:
```bash
pip install idmtools[slurm]
```

On the cluster (if needed):
```bash
# Load Python module (cluster-dependent)
module load python/3.11

# Install idmtools
pip install --user idmtools[slurm]
```

### 3. SSH Configuration

Setup passwordless SSH (recommended):
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096

# Copy to cluster
ssh-copy-id username@cluster.example.com

# Test connection
ssh username@cluster.example.com "hostname"
```

## Verify Slurm is Running

Before submitting jobs, verify your Slurm cluster is available:

```bash
sinfo -a
```

Expected output:

```
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
LocalQ*      up   infinite      1   idle localhost
```

## Basic Configuration

### Minimum Configuration

Minimum required in `idmtools.ini`:

```ini
[MY_SLURM]
type = SLURM
job_directory = /home/userxyz/my_outputs
```
```python
# call with ini file
Platform('MY_SLURM')
```

Or directly from code:

```python
Platform('SLURM_LOCAL', job_directory='/home/userxyz/my_outputs')
```


### Full Configuration File

Create `~/.idmtools/idmtools.ini`:

```ini
[my_Slurm]
type = Slurm
job_directory = /home/myusername/idmtools_jobs
partition = general
account = myproject
time_limit = 01:00:00
cpus_per_task = 1
mem_per_cpu = 4G
```

Load configuration:

```python
platform = Platform("my_Slurm")
```

## SlurmPlatform Attributes

All attributes from `SlurmPlatform` in `slurm_platform.py`:

| Attribute | Description |
|-----------|-------------|
| `mail_type` | Email notification type (e.g. `BEGIN`, `END`, `FAIL`) |
| `mail_user` | Email address for job notifications |
| `nodes` | Number of nodes to request |
| `ntasks` | Number of tasks |
| `cpus_per_task` | Number of CPUs per task |
| `ntasks_per_core` | Number of tasks per core |
| `max_running_jobs` | Maximum running jobs per experiment |
| `mem` | Memory per node in MB |
| `mem_per_cpu` | Memory per CPU in MB |
| `partition` | Slurm partition/queue to submit to |
| `constraint` | Compute node constraint |
| `time` | Job time limit (e.g. `01:00:00`) |
| `account` | Account to charge for the job |
| `exclusive` | Nodes cannot be shared with other jobs/users |
| `requeue` | Allow job to be requeued if a node fails |
| `retries` | Default number of retries for failed jobs |
| `sbatch_custom` | Custom commands to append to the sbatch script |
| `modules` | Environment modules to load before execution |
| `dir_exist_ok` | Allow job directories to already exist |
| `array_batch_size` | Maximum Slurm job array size |
| `propogate_slurm_env_var` | Propagate inherited SLURM env vars into generated scripts |
| `run_on_slurm` | Submit the current script itself as a Slurm job |
| `mpi_type` | MPI type: `pmi2`, `pmix` (Slurm MPI), or `mpirun` (independent MPI) |

See the [sbatch documentation](https://slurm.schedmd.com/sbatch.html) for full details.

## Running Simulations

### Basic Example

```python
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.python_task import PythonTask

# Create platform
platform = Platform(
    "Slurm_Local",
    job_directory="/scratch/myusername/jobs"
)

# Create task
task = PythonTask(
    script_path="model.py",
    python_path="python3"
)

# Set parameters
task.parameters = {
    "population": 10000,
    "beta": 0.5,
    "gamma": 0.1
}

# Create experiment
experiment = Experiment.from_task(
    task,
    name="Slurm Experiment"
)

# Run on Slurm
experiment.run(
    platform=platform,
    wait_until_done=True
)

print(f"Experiment ID: {experiment.uid}")
```


### Job Arrays

idmtools automatically uses Slurm job arrays for efficiency:

```python
from idmtools.builders import SimulationBuilder

# Create parameter sweep
builder = SimulationBuilder()
builder.add_sweep_definition(
    lambda sim, beta: sim.task.set_parameter("beta", beta),
    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
)

experiment = Experiment.from_builder(
    builder,
    task,
    name="Slurm Array Job"
)

# Submits as single job array (9 tasks)
experiment.run(platform=platform, wait_until_done=True)

# Check job status
# $ squeue -u myusername
# JOBID   USER    PARTITION  NAME        ST  TIME
# 12345_[1-9]  myuser  compute   Slurm_Array  PD  0:00
```

## Environment Configuration

### Module Loading

```python
# Load required modules
platform.modules = ["python/3.11", "gcc/11.2", "openmpi/4.1"]

# Modules loaded automatically before job execution
```

## Working with Partitions/Queues

### Partition Selection

```python
# Submit to specific partition
platform.partition = "compute"  # or "gpu", "bigmem", "debug", etc.
```



### Account/Project

```python
# Charge to specific account
platform.account = "proj12345"
```

## File Management

### Working Directory

```python
# Set job working directory
platform = Platform(
    "Slurm_Local",
    job_directory="/scratch/myuser/jobs"  # Fast scratch filesystem
)
```

### Asset Handling

```python
# Assets are copied to job directory
experiment.add_asset("config.json")
experiment.add_asset("input_data.csv")
```

## Monitoring and Management

### Check Job Status

```python
# Refresh experiment status
experiment.refresh_status(platform)

print(f"Status: {experiment.status}")
```

### Cancel Jobs

idmtools submits jobs as Slurm job arrays. Use the `scancel` command on the cluster to cancel them.

**View jobs in the queue:**

```bash
squeue
```

**Cancel a specific task** (job array ID + index):

```bash
scancel <job-id>_<index>
```

**Cancel all tasks** in a job array:

```bash
scancel <job-id>
```

See the [scancel documentation](https://slurm.schedmd.com/scancel.html) for full details.

### Job Information

```bash
# Check job status (on cluster)
squeue -u myusername

# Detailed job info
scontrol show job <job_id>

# Job history
sacct -u myusername --starttime=2024-01-01

# Job efficiency
seff <job_id>
```

## MPI/Parallel Jobs

### OpenMPI

```python
# MPI job configuration
task = CommandTask(
    command="mpirun -np 32 ./parallel_model"
)

experiment = Experiment.from_template(task, name="MPI Job")
platform = Platform("Slurm_local", job_directory =".", mpi_type = "pmi2", nodes=2, ntasks_per_node=16, modules=["openmpi/4.1"])
experiment.run(platform=platform, wait_until_done=True)
```

## Troubleshooting

### SSH Connection Issues

```python
# Test SSH connection
import paramiko

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
try:
    ssh.connect("cluster.example.com", username="myuser")
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    ssh.close()
```

### Job Submission Failures

```bash
# Check Slurm configuration
sinfo

# Check partition access
sinfo -p <partition_name>

# Check account balance (if applicable)
sshare -A <account_name>
```

## Limitations

!!! warning "Unsupported features"
    - **WorkItems** are not supported on the Slurm platform.
    - **AssetCollection** creation or referencing an existing `AssetCollection` is not supported. If migrating from COMPS, remove code like:

        ```python
        # Remove this when using Slurm Platform
        asset_collection = AssetCollection.from_asset_collection_id('...')
        ```

## Recommendations

- Back up simulation results regularly — scratch filesystems are often purged on clusters.
- Use appropriate partitions: `debug` for short tests, `compute` for production runs.
- Monitor resource usage with `seff <job_id>` after jobs complete to optimize future requests.

## Next Steps

- [User Guide](../user-guide/index.md) - General concepts
- [Tutorials](../tutorials/index.md) - Hands-on examples
- [Platform Comparison](index.md#platform-comparison) - Compare platforms
- [Analyzers](../data-analysis/analyzers.md) - Process simulation results

## See Also
- [Official Slurm Documentation](https://slurm.schedmd.com/)
