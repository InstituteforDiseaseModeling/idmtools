# IDM Modeling Tools

# Installation 
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

You can also install just the individual packages to create minimal environments

- `pip install idmtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Core package
- `pip install idmtools-cli --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Adds the idmtools cli commands
- `pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for COMPS
- `pip install idmtools-platform-local --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Support for Local Platform
- `pip install idmtools-models --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - Python and generic models
- `pip install idmtools-model-dtk --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple` - EMOD Model support

## Pre-requisites
- Python 3.6/3.7 x64
- Docker(Required for the local platform)
  On Windows, please use Docker Desktop 2.1.0.5 or 2.2.0.1

## Development Environment Setup

When setting up your environment for the first time, you can use the following instructions

### First Time Setup
1) Clone the repository:
   ```bash
   > git clone https://github.com/InstituteforDiseaseModeling/idmtools.git
   ```
2) Create a virtualenv. On Windows, please use venv to create the environment
   `python -m venv idmtools`
   On Unix(Mac/Linux) you can use venv or virtualenv
3) Activate the virtualenv
4) If you are on windows, run `pip install py-make --upgrade --force-reinstall`
5) Run `docker login docker-staging.idmod.org`
6) Then run `python dev_scripts/bootstrap.py`. This will install all the tools. 

### General Use
After the first install almost everything you need as a developer is part of the makefiles. There is a Makefile is every project directory. There is also a makefile at the top-level of the project.

To use the makefiles you can explore the available commands by running `make help`. On Windows, use `pymake help` 

Here are a list of common commands

```bash
setup-dev   -   Setup dev environment(assumes you already have a virtualenv)
clean       -   Clean up temporary files
clean-all   -   Deep clean project
lint        -   Lint package and tests
test        -   Run Unit tests
test-all    -   Run Tests that require docker and external systems
coverage    -   Run tests and generate coverage report that is shown in browser
```

Some packages have unique build related commands, specifically the local platform. Use `make help` to identify specific commands

### IDE/Runtime Setup

For source completion and indexing, set the package paths in your IDE. In PyCharm, select the following directories then right-click and select `Mark Directory as -> Source Root`.
![Mark Directory as Sources Root](documentation/images/mark_directory_as_source.png)

The directories that should be added as source roots are
- `idmtools/idmtools_core`
- `idmtools/idmtools_cli`
- `idmtools/idmtools_platform_local`
- `idmtools/idmtools_platform_comps`
- `idmtools/idmtools_model_emod`
- `idmtools/idmtools_models`
- `idmtools/idmtools_test`

### Running specific tests from the command line

To run a select set of tests, you can use the `run_all.py` python script

For example to run all tests that tagged emod but not tagged comps run 
```bash
python dev_scripts/run_all.py -sd 'tests' --exec "py.test -m 'not comps and emod'"
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

### WSL2 on Windows Setup(Experimental)

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

# Troubleshooting the Development Environment

1. Docker Auth issues.

   Idmtools currently does not prompt users for docker credentials. Because of this you must login
   beforehand using `docker login docker-staging.packages.idmod.org`
2. Docker image not found
   Rerun the `pymake setup-dev`
3. Check build logs Detailed Build Logs are located within in package and tests directoery withing the package with the name make.buildlog. You can also increase the console log level to DEBUG by setting the environment variable BUILD_DEBUG to 1