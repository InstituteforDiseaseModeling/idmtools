# CLI reference

Command-line interface tools for idmtools.

## Available commands

### Getting help

**Command:**
```bash
idmtools --help
```

**Output:**
```
Usage: idmtools [OPTIONS] COMMAND [ARGS]...

  Allows you to perform multiple idmtools commands.

Options:
  --debug / --no-debug  When selected, enables console level logging
  --help                Show this message and exit.

Commands:
  comps        COMPS platform related commands.
  config       Contains commands related to the creation of idmtools.ini.
  container    Container platform related commands.
  examples     Display a list of examples organized by plugin type.
  file         File platform related commands.
  gitrepo      Contains commands related to examples download.
  info         Troubleshooting and debugging information.
  init         Commands to help start or extend projects through templating.
  init-export  Export list of project templates.
  package      Contains commands related to package versions.
  slurm        Slurm platform related commands.
  version      List version info about idmtools and plugins.

idmtools <command> --help    # Command-specific help
```

### List platform plugins configuration aliases

**Command:**
```bash
idmtools info plugins platform-aliases
```

**Output:**
```
(idmtools_pypi_313) PS C:\git_pypi\idmtools> idmtools info plugins platform-aliases
+---------------------------+-------------------------------------------------------------------------------------------------------+
| Platform plugin aliases   | Configuration options                                                                                 |
|---------------------------+-------------------------------------------------------------------------------------------------------|
| CALCULON                  | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon', 'python_executable': 'python3'}    |
| NDCLOUD                   | {'endpoint': 'https://comps.idmod.org', 'environment': 'NDcloud', 'python_executable': 'python3'}     |
| NIBBLER                   | {'endpoint': 'https://comps.idmod.org', 'environment': 'Nibbler', 'python_executable': 'python3'}     |
| SLURMSTAGE                | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage', 'python_executable': 'python3'} |
| CUMULUS                   | {'endpoint': 'https://comps2.idmod.org', 'environment': 'Cumulus', 'python_executable': 'python'}     |
| SLURM                     | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon', 'python_executable': 'python3'}    |
| SLURM2                    | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage', 'python_executable': 'python3'} |
| BOXY                      | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage', 'python_executable': 'python3'} |
| CONTAINER                 | {'job_directory': 'C:\\Users\\sharonch'}                                                              |
| PROCESS                   | {'job_directory': 'C:\\Users\\sharonch'}                                                              |
| SLURM_LOCAL               | {'job_directory': 'C:\\Users\\sharonch'}                                                              |
| SLURM_CLUSTER             | {'job_directory': 'C:\\Users\\sharonch'}                                                              |
| CALCULON_SSMT             | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon', 'python_executable': 'python3'}    |
| NDCLOUD_SSMT              | {'endpoint': 'https://comps.idmod.org', 'environment': 'NDcloud', 'python_executable': 'python3'}     |
| NIBBLER_SSMT              | {'endpoint': 'https://comps.idmod.org', 'environment': 'Nibbler', 'python_executable': 'python3'}     |
| SLURMSTAGE_SSMT           | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage', 'python_executable': 'python3'} |
| CUMULUS_SSMT              | {'endpoint': 'https://comps2.idmod.org', 'environment': 'Cumulus', 'python_executable': 'python'}     |
| SLURM_SSMT                | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon', 'python_executable': 'python3'}    |
| SLURM2_SSMT               | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage', 'python_executable': 'python3'} |
| BOXY_SSMT                 | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage', 'python_executable': 'python3'} |
| FILE                      | {'job_directory': 'C:\\Users\\sharonch'}                                                              |
+---------------------------+-------------------------------------------------------------------------------------------------------+

```

### COMPS platform CLI commands
**Command:**
```bash
idmtools comps --help
```

**Output:**
```
Usage: idmtools comps [OPTIONS] CONFIG_BLOCK COMMAND [ARGS]...

  Commands related to managing the COMPS platform.

  CONFIG_BLOCK - Name of configuration section or alias to load COMPS
  connection information from

Options:
  --help  Show this message and exit.

Commands:
  ac-exist          Check ac existing based on requirement file Args:...
  assetize-outputs  Allows assetizing outputs from the command line
  download          Allows Downloading outputs from the command line
  login             Login to COMPS
  req2ac            Create ac from requirement file Args: asset_tag: tag...
  singularity       Singularity commands

```

### Container platform CLI commands

**Command:**
```bash
idmtools container --help
```

**Output:**
```
Usage: idmtools container [OPTIONS] COMMAND [ARGS]...

  Container Platform CLI commands.

  Args:     all: Bool, show all commands

  Returns:     None

Options:
  --all   Show all commands
  --help  Show this message and exit.

Commands:
  cancel   Cancel an Experiment/Simulation job.
  history  View the job history.
  jobs     List running Experiment/Simulation jobs.
  status   Check the status of an Experiment/Simulation.

```

### Slurm platform CLI commands

**Command:**
```bash
idmtools slurm --help
```

**Output:**
```
Usage: idmtools slurm [OPTIONS] JOB_DIRECTORY COMMAND [ARGS]...

  Commands related to managing the SLURM platform.

  job_directory: Slurm Working Directory

Options:
  --help  Show this message and exit.

Commands:
  get-job        Get Suite/Experiment/Simulation slurm job
  get-latest     Get the latest experiment info
  get-path       Get Suite/Experiment/Simulation directory
  get-status     Get status of Experiment/Simulation
  status         Get simulation's status
  status-report  Get simulation's report

```

## Platform-specific CLIs

Some platforms have additional CLI tools:

- **COMPS**: Additional COMPS-specific commands
- **Slurm**: Job management commands
- **Container**: Container management

## See also

- [User guide](../user-guide/index.md) - Using the CLI in workflows
