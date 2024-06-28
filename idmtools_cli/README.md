![Staging: idmtools-cli](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-cli/badge.svg?branch=dev)

# idmtools-cli

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Development tips](#development-tips)
- [Using the CLI](#using-the-cli)
  - [Version command](#version-command)
  - [Experiment commands for Local Platform](#experiment-commands-for-local-platform)
    - [Status](#status)
    - [Delete](#delete)
  - [Simulation commands for Local Platform](#simulation-commands-for-local-platform)
  - [Status](#status-1)
  - [GitRepo commands](#gitrepo-commands)
    - [View](#view)
    - [Repos](#repos)
    - [Releases](#releases)
    - [Peep](#peep)
    - [Download](#download)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-cli --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

# Development tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`

# Using the CLI

The CLI requires the workers service to already be running.
`idmtools`

## Version command

To determine version of idmtools and related plugins, use the version cli command.


```
> idmtools version
```

Example output
```bash
emodpy                               Version: 1.3.0                           
  Plugins:
    EMODTask                  
idmtools                             Version: 1.4.0+nightly.0                 
  Plugins:
    CommandTask               
idmtools-cli                         Version: 1.4.0+nightly.0                 
idmtools-models                      Version: 1.4.0+nightly.0                 
  Plugins:
    JSONConfiguredPythonTask  
    JSONConfiguredRTask       
    JSONConfiguredTask        
    PythonTask                
    RTask                     
    ScriptWrapperTask         
    TemplatedScriptTask       
idmtools-platform-comps              Version: 1.4.0+nightly.0                 
  Plugins:
    COMPSPlatform             
    SSMTPlatform                        
idmtools-platform-slurm              Version: 1.0.0+nightly                   
  Plugins:
    SlurmPlatform             
```


## Experiment commands for Local Platform

### Status

You can check the status of experiments use the follow command. It will also summarize the simulations under
the experiment as a progress bar with green section for completed tasks, yellow for in progress, red for failed, and
white for queued. 

```
> idmtools experiment --platform Local status --help
```
 

In addition, we used in conjunction with a console that supports auto-highlighting of hyperlinks, you will be able to
easily open up the asset directories by clicking on the data path URLs.

You can also perform filtering on the experiments
```bash
> idmtools experiment --platform Local status --tag type PythonExperiment
> idmtools experiment --platform Local status --id 8EHU147Z
```

### Delete

You can delete experiments and their child simulations using the following command. Optionally you can also delete
the associated data directories as well by using the *--data* option.

```
>idmtools experiment --platform Local delete <experiment_id>
```

## Simulation commands for Local Platform

## Status 

You can check the status of simulations use the follow command.

```
>idmtools simulation --platform Local status
```

You can also filter by a either id, experiment id, status, and tags or any combination of the aforementioned

```bash
> idmtools simulation --platform Local status --experiment-id EFX6JXBV
> idmtools simulation --platform Local status --id XDT0VMVV
> idmtools simulation --platform Local status --tag a 5 --tag b
> idmtools simulation --platform Local status --experiment-id --status failed
```


## GitRepo commands

### View

You can check idmtools available examples. You can use --raw to determine to display in detailed or simplified format

```
> idmtools gitrepo view
```

### Repos

You can list all public repos for a GitHub owner. You can use --owner to specify an owner and --page for pagination
--owner default to 'institutefordiseasemodeling'
--page default to 1

```
> idmtools gitrepo repos
```

### Releases

You can list all releases of a repo by providing --owner and --repo
--owner default to 'institutefordiseasemodeling' and --repo default to 'idmtools'

```
> idmtools gitrepo releasess
```

### Peep

You can list all current files/dirs of a repo folder by providing --url

```
> idmtools gitrepo peep
```

### Download

You can download files from a public repo to a specified local folder (default to current folder). By default, it will 
download idmtools examples. You can also download any files from any public repo by using --url (multiple is supported)

```
> idmtools gitrepo download
```
