# CLI Reference

Command-line interface tools for idmtools.

## Available Commands

### Getting Help

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

### List Platform Plugins Configuration Aliases

**Command:**
```bash
idmtools info plugins platform-aliases --help
```

**Output:**
```
+---------------------------+-------------------------------------------------------------------------+
| Platform Plugin Aliases   | Configuration Options                                                   |
|---------------------------+-------------------------------------------------------------------------|
| SLURM_LOCAL               | {'job_directory': 'user_job_directory'}                                 |
| SLURM_CLUSTER             | {'job_directory': 'user_job_directory'}                                 |
| FILE                      | {'job_directory': 'user_job_directory'}                                 |
| PROCESS                   | {'job_directory': 'user_job_directory'}                                 |
| CALCULON_SSMT             | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon'}      |
| IDMCLOUD_SSMT             | {'endpoint': 'https://comps.idmod.org', 'environment': 'IDMcloud'}      |
| NDCLOUD_SSMT              | {'endpoint': 'https://comps.idmod.org', 'environment': 'NDcloud'}       |
| BMGF_IPMCLOUD_SSMT        | {'endpoint': 'https://comps.idmod.org', 'environment': 'BMGF_IPMcloud'} |
| QSTART_SSMT               | {'endpoint': 'https://comps.idmod.org', 'environment': 'Qstart'}        |
| NIBBLER_SSMT              | {'endpoint': 'https://comps.idmod.org', 'environment': 'Nibbler'}       |
| SLURMSTAGE_SSMT           | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage'}   |
| CUMULUS_SSMT              | {'endpoint': 'https://comps2.idmod.org', 'environment': 'Cumulus'}      |
| SLURM_SSMT                | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon'}      |
| SLURM2_SSMT               | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage'}   |
| BOXY_SSMT                 | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage'}   |
| CONTAINER                 | {'job_directory': 'user_job_directory'}                                 |
| CALCULON                  | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon'}      |
| IDMCLOUD                  | {'endpoint': 'https://comps.idmod.org', 'environment': 'IDMcloud'}      |
| NDCLOUD                   | {'endpoint': 'https://comps.idmod.org', 'environment': 'NDcloud'}       |
| BMGF_IPMCLOUD             | {'endpoint': 'https://comps.idmod.org', 'environment': 'BMGF_IPMcloud'} |
| QSTART                    | {'endpoint': 'https://comps.idmod.org', 'environment': 'Qstart'}        |
| NIBBLER                   | {'endpoint': 'https://comps.idmod.org', 'environment': 'Nibbler'}       |
| SLURMSTAGE                | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage'}   |
| CUMULUS                   | {'endpoint': 'https://comps2.idmod.org', 'environment': 'Cumulus'}      |
| SLURM                     | {'endpoint': 'https://comps.idmod.org', 'environment': 'Calculon'}      |
| SLURM2                    | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage'}   |
| BOXY                      | {'endpoint': 'https://comps2.idmod.org', 'environment': 'SlurmStage'}   |
+---------------------------+-------------------------------------------------------------------------+

```

### COMPS Platform CLI Commands
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

### Container Platform CLI commands

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

### Slurm Platform CLI commands

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

## Platform-Specific CLIs

Some platforms have additional CLI tools:

- **COMPS**: Additional COMPS-specific commands
- **Slurm**: Job management commands
- **Container**: Container management

## See Also

- [User Guide](../user-guide/index.md) - Using the CLI in workflows
