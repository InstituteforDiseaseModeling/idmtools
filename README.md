
# Packages Status
![Staging: idmtools-core](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-core/badge.svg?branch=dev)
![Staging: idmtools-cli](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-cli/badge.svg?branch=dev)
![Staging: idmtools-models](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-models/badge.svg?branch=dev)
![Staging: idmtools-platform-comps](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-comps/badge.svg?branch=dev)
![Staging: idmtools-platform-local](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-local/badge.svg?branch=dev)
![Staging: idmtools-platform-slurm](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-slurm/badge.svg?branch=dev)
![Staging: idmtools-test](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-test/badge.svg?branch=dev)

# Other status
![Dev: Rebuild documentation](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Rebuild%20documentation/badge.svg?branch=dev)
![Lint](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Lint/badge.svg?branch=dev)

# IDM Modeling Tools

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [User Installation](#user-installation)
  - [Recommended install](#recommended-install)
  - [Advanced Install](#advanced-install)
  - [Installing Development/Early Release Versions](#installing-developmentearly-release-versions)
    - [PyPI](#pypi)
    - [Github](#github)
      - [Installing From Development Branch(or other specific branch)](#installing-from-development-branchor-other-specific-branch)
  - [Pre-requisites](#pre-requisites)
  - [Additional Resources](#additional-resources)
- [Development Environment Setup](#development-environment-setup)
  - [First Time Setup](#first-time-setup)
  - [Installing from a Pull Request](#installing-from-a-pull-request)
  - [General Use](#general-use)
  - [Tips](#tips)
  - [IDE/Runtime Setup](#ideruntime-setup)
  - [Running smoke tests or all tests from Github Actions](#running-smoke-tests-or-all-tests-from-github-actions)
  - [Running specific tests from the command line](#running-specific-tests-from-the-command-line)
  - [WSL2 on Windows Setup(Experimental)](#wsl2-on-windows-setupexperimental)
  - [Troubleshooting the Development Environment](#troubleshooting-the-development-environment)
- [Reporting an Issue](#reporting-an-issue)
- [Requesting a feature](#requesting-a-feature)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Installation

## Recommended install
The recommended install is to use
```bash
pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the core tools, the cli, the comps and local platforms, support for EMOD models, and python models

If you do not need the local platform, you can use the following command
```bash
pip install idmtools[idm] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
This will install the core tools, the cli, the comps, support for EMOD models, and python models

If you are Python 3.6, you will also need to run
```bash
pip install dataclasses
```
## Advanced Install
You can also install just the individual packages to create minimal environments

- `pip install idmtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Core package
- `pip install idmtools-cli --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for COMPS
- `pip install idmtools-platform-local --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for Local Platform
- `pip install idmtools-models --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Python and generic models

## Installing Development/Early Release Versions

Development versions are available through both IDM's pypi registry and through Github.

### PyPI


If you have your authentication defined in your pip.conf or pip.ini file, you can use the following commands to install from staging
- `pip install idmtools --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Core package
- `pip install idmtools-cli --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for COMPS
- `pip install idmtools-platform-local --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Support for Local Platform
- `pip install idmtools-models --index-url=https://<USERNAME>:<PASSWORD>@packages.idmod.org/api/pypi/pypi-staging/simple` - Python and generic models

### Github

You can install directly from Github. You can install directly from PRs, Branches, and Tags. You can use either *git+https://* or *git+ssh://git@*

#### Installing From Development Branch(or other specific branch)

To install from the development branch, use the following commands
```bash
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools&subdirectory=idmtools_core"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_platform_comps&subdirectory=idmtools_platform_comps"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_cli&subdirectory=idmtools_cli"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_models&subdirectory=idmtools_models"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_platform_local&subdirectory=idmtools_platform_local"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_test&subdirectory=idmtools_test"
```

To install a different github branch, change the *@dev* in each command to *@<branch name>* where *branch_name* is the name of branch you would like to install from. To install from a PR, see [Installing from a Pull Request](#installing-from-a-pull-request)

## Pre-requisites
- Python 3.6/3.7 x64
- Docker(Required for the local platform)
  On Windows, please use Docker Desktop 2.1.0.5 or 2.2.0.1

## Additional Resources

Private documentation is located at https://docs.idmod.org/projects/idmtools/en/latest/. Scroll to "Do you have a password? Access here" and use the password "IDM2020idmtools". 

# Development Environment Setup

When setting up your environment for the first time, you can use the following instructions

## First Time Setup
1) Clone the repository:
   ```bash
   > git clone https://github.com/InstituteforDiseaseModeling/idmtools.git
   ```
2) Create a virtualenv. On Windows, please use venv to create the environment
   `python -m venv idmtools`
   On Unix(Mac/Linux) you can use venv or virtualenv
3) Activate the virtualenv
4) If you are on windows, run `pip install py-make --upgrade --force-reinstall`
5) Run `docker login docker-staging.packages.idmod.org`
6) Then run `python dev_scripts/bootstrap.py`. This will install all the tools. 

## Installing from a Pull Request

Sometimes, like when testing a new feature, it is useful to install a development or early version. We can do this directly from GitHub PRs using the following commands

To install idmtools from a specific PR you can use the following script replacing 123 with the number of your PR

```bash
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools&subdirectory=idmtools_core"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_platform_comps&subdirectory=idmtools_platform_comps"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_cli&subdirectory=idmtools_cli"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_models&subdirectory=idmtools_models"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_platform_local&subdirectory=idmtools_platform_local"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_test&subdirectory=idmtools_test"
```

To install from a specific branch, see [Installing From Development Branch(or other specific branch)](#installing-from-development-branchor-other-specific-branch)

## General Use
After the first install almost everything you need as a developer is part of the makefiles. There is a Makefile is every project directory. There is also a makefile at the top-level of the project.

To use the makefiles you can explore the available commands by running `make help`. On Windows, use `pymake help` 

Here are a list of common commands

```bash
setup-dev   -   Setup dev environment(assumes you already have a virtualenv)
setup-dev-no-docker -   Setup dev environment(assumes you already have a virtualenv) exlcuding docker builds for the local platform
clean       -   Clean up temporary files
clean-all   -   Deep clean project
lint        -   Lint package and tests
test        -   Run Unit tests
test-all    -   Run Tests that require docker and external systems
coverage    -   Run tests and generate coverage report that is shown in browser
```

Some packages have unique build related commands, specifically the local platform. Use `make help` to identify specific commands

## Tips

* Use `dev-watch` make rule to autorun linter and tests in response to local changes
* When a specific test fails, you `test-failed` rule to run only previously failed tested
* Use 

## IDE/Runtime Setup

For source completion and indexing, set the package paths in your IDE. In PyCharm, select the following directories then right-click and select `Mark Directory as -> Source Root`.
![Mark Directory as Sources Root](docs/images/mark_directory_as_source.png)

The directories that should be added as source roots are
- `idmtools/idmtools_core`
- `idmtools/idmtools_cli`
- `idmtools/idmtools_platform_local`
- `idmtools/idmtools_platform_comps`
- `idmtools/idmtools_models`
- `idmtools/idmtools_test`

## Running smoke tests or all tests from Github Actions

To run smoke tests from Github Actions when push or pull request, put "Run smoke test!" in your commit message

To run all tests from Github Actions when push or pull request, put "Run all test!" in your commit message
```bash
git commit -m 'fix bug xxx, Run smoke test!'
git push
```

## Running specific tests from the command line

To run a select set of tests, you can use the `run_all.py` python script

For example to run all tests that tagged python but not tagged comps run 
```bash
python dev_scripts/run_all.py -sd 'tests' --exec "py.test -m 'not comps and python'"
```

You can also filter by test case name or method name. The below will run any test with batch in the name. 
```bash
python dev_scripts/run_all.py -sd 'tests' --exec "py.test -k 'batch'"
```

To run a specific test, cd to the project directories test folder and run
```bash
py.test test_emod.py::TestLocalPlatformEMOD::test_duplicated_eradication
```

In addition, you can rerun just the failed test using either the top-level `pymake test-failed` rule or by using the 
`--lf` switch on py.test

## WSL2 on Windows Setup(Experimental)

1. Enable Windows Features by running the following in a Windows Powershell
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```
2. Restart
3. 
   a. If you do a Linux istro installed already through WSL run the following command in a powershell windows
       ```powershell
       wsl --set-version <Distro> 2
       ```
       You most likely want to run the following command ss well to ensure wsl2 is default going forward
       ```powershell
       wsl --set-default-version 2
       ```
   b. If you do not yet have a copy of linux installed through WSL, see  https://docs.microsoft.com/en-us/windows/wsl/install-win10#install-your-linux-distribution-of-choice

## Troubleshooting the Development Environment

1. Docker Auth issues.

   Idmtools currently does not prompt users for docker credentials. Because of this you must login
   beforehand using `docker login docker-staging.packages.idmod.org`
2. Docker image not found
   Rerun the `pymake setup-dev`
3. Check build logs Detailed Build Logs are located within in package and tests directoery withing the package with the name make.buildlog. You can also increase the console log level to DEBUG by setting the environment variable BUILD_DEBUG to 1

# Reporting an Issue

You can report an issue directly on GitHub or by emailing [idmtools-issue@idmod.org](mailto:idmtools-issue@idmod.org). Please include steps to reproduce the issue

# Requesting a feature 

You can request a feature but opening a ticket on the repo or by emailing [idmtools-feature@idmod.org](mailto:idmtools-feature@idmod.org)