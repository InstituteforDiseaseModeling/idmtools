![Staging: idmtools-cli](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-cli/badge.svg?branch=dev)

# idmtools-cli

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Development Tips](#development-tips)
- [Using the CLI](#using-the-cli)
  - [Experiment commands](#experiment-commands)
    - [Status](#status)
    - [Delete](#delete)
  - [Simulation Commands](#simulation-commands)
  - [Status](#status-1)
  - [Example commands](#example-commands)
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

# Development Tips

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

## Experiment commands

### Status

You can check the status of experiments use the follow command. It will also summarize the simulations under
the experiment as a progress bar with green section for completed tasks, yellow for in progress, red for failed, and
white for queued. 

```
> idmtools experiment status
```

Alternatively, you can run from anywhere using
```
> idmtools experiment status
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
>idmtools experiment delete <experiment_id>
```

## Simulation Commands

## Status 

You can check the status of simulations use the follow command.

```
>idmtools simulation status
```

You can also filter by a either id, experiment id, status, and tags or any combination of the aforementioned

```bash
> idmtools simulation --platform Local status --experiment-id EFX6JXBV
> idmtools simulation --platform Local status --id XDT0VMVV
> idmtools simulation --platform Local status --tag a 5 --tag b
> idmtools simulation --platform Local status --experiment-id --status failed
```


## Example commands

### View

You can check idmtools available examples. You can use --raw to determine to display in detailed or simplified format

```
> idmtools example view
```

### Repos

You can list all public repos for a GitHub owner. You can use --owner to specify an owner
--owner default to be 'institutefordiseasemodeling'

```
> idmtools example repos
```

### Releases

You can list all releases of a repo by providing --owner and --repo. 
--owner default to be 'institutefordiseasemodeling' and --repo default to 'idmtools'

```
> idmtools example releasess
```

### Peep

You can list all current files/dirs of a repo folder by providing --url. 

```
> idmtools example peep
```

### Download

You can download files from a public repo to a specified local folder (default to current folder). By default, it will 
download idmtools examples. You can also download any files from any public repo by using --url (multiple is supported)

```
> idmtools example download
```
