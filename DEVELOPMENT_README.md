<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [How to contribute to idmtools](#how-to-contribute-to-idmtools)
- [Development Guide](#development-guide)
  - [Submitting patches](#submitting-patches)
  - [First time setup](#first-time-setup)
  - [Start coding](#start-coding)
  - [Overview of Development Environment](#overview-of-development-environment)
  - [Run test/linting on code change](#run-testlinting-on-code-change)
  - [IDE/Runtime Setup](#ideruntime-setup)
  - [WSL2 on Windows Setup(Experimental)](#wsl2-on-windows-setupexperimental)
  - [Troubleshooting the Development Environment](#troubleshooting-the-development-environment)
- [Documentation](#documentation)
  - [Editing the Documentation](#editing-the-documentation)
  - [Reload Documentation on change](#reload-documentation-on-change)
- [Test](#test)
  - [Test Reports](#test-reports)
  - [Running smoke tests or all tests from Github Actions](#running-smoke-tests-or-all-tests-from-github-actions)
  - [Running specific tests from the command line](#running-specific-tests-from-the-command-line)
  - [Installing from a Pull Request](#installing-from-a-pull-request)
  - [Installing From Development Branch(or other specific branch)](#installing-from-development-branchor-other-specific-branch)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# How to contribute to idmtools

Thank you for considering contributing to idmtools!

# Development Guide

This section is intended for developers who would like to contribute to idmtools. It is also applicable to testing idmtools. 

*Any references to the `make` command should be replaced with the `pymake` command on Windows*

## Submitting patches

If there is not an open issue for what you want to submit, prefer opening one for discussion before working on a PR. You can work on any issue that doesn't have an open PR linked to it or a maintainer assigned
to it. These show up in the sidebar. No need to ask if you can work on an issue that interests you.

Include the following in your patch:

-   Include tests if your patch adds or changes code. Make sure the test
    fails without your patch.
-   Update any relevant docs pages and docstrings.
-   Open a Issue with clear title of the new feature/bug fix and link to the PR

## First time setup

1) Clone the repository:
   ```bash
   > git clone https://github.com/InstituteforDiseaseModeling/idmtools.git
   ```
2) Create a virtualenv. On Windows, please use venv to create the environment
   `python -m venv idmtools`
   On Unix(Mac/Linux) you can use venv or virtualenv
3) Activate the virtualenv
4) Run `docker login docker-staging.packages.idmod.org`
5) Then run `python dev_scripts/bootstrap.py`. This will install all the tools.

## Start coding

-   Create a branch to identify the issue you would like to work on. If you're submitting a bug or documentation fix, branch off of the latest ".x" branch.

    ```bash
    $ git fetch origin
    $ git checkout -b your-branch-name origin/1.1.x
    ```
    If you're submitting a feature addition or change, branch off of the "dev" branch.

    ```bash
    $ git fetch origin
    $ git checkout -b your-branch-name origin/dev
    ```
-   Using your favorite editor, make your changes, `committing as you go`.
-   Include tests that cover any code changes you make. Make sure the test fails without your patch. Run the tests as described below.
-   Push your commits to your fork on GitHub and `create a pull request`. Link to the issue being addressed with
    ``fixes #123`` in the pull request.

    ```bash
    git push --set-upstream fork your-branch-name
    ```

- [Committing as you go](https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes)
- Run `pymake lint` or `make lint` before opening a PR and fix all linting errors
- [Create a pull request](https://help.github.com/en/articles/creating-a-pull-request)

## Overview of Development Environment

After the first install almost everything you need as a developer is part of the makefiles. Within each project directory, there is a Makefile that contains all the development related tasks. There is also a makefile at the top-level of the project.

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

## Run test/linting on code change

There is a utility command to run linting and tests on code changes. It runs within each package directory. For example, changes to
files in `idmtools_core` will run the `make lint` and `make test-smoke` tests within the idmtools_core directory. The jobs run at most once every 10 seconds. This limits how often the jobs will be executed.

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

## WSL2 on Windows Setup(Experimental)

1. Enable Windows Features by running the following in a Windows Powershell
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```
2. Restart
3.
   a. If you do a Linux Distro installed already through WSL run the following command in a powershell windows
       ```powershell
       wsl --set-version <Distro> 2
       ```
       You most likely want to run the following command as well to ensure wsl2 is default going forward
       ```powershell
       wsl --set-default-version 2
       ```
   b. If you do not yet have a copy of linux installed through WSL, see https://docs.microsoft.com/en-us/windows/wsl/install-win10#install-your-linux-distribution-of-choice


## Troubleshooting the Development Environment

1. Docker Auth issues.
   Idmtools currently does not prompt users for docker credentials. Because of this you must login
   beforehand using `docker login docker-staging.packages.idmod.org`
2. Docker image not found
   Rerun the `pymake setup-dev` or `make setup-dev` on unix systems
  
# Documentation

The following section documents how to build and edit the documentation.

## Editing the Documentation

The documentation is built using Sphinx from the rst files in the `docs` folder. The documentation is a series of linked
documents and generated documents from the python code. `index.rst` is the entry point into the documentation. For details
on the formatting of documentation, see the [Sphinx](https://www.sphinx-doc.org/en/stable/) docs

## Reload Documentation on change

You can use the `make build-docs-server` feature to automatically. This runs a local python documentation server running at
http://localhost:8000. Any changes you make to the python files or rst files, the documentation will be reloaded in the browser.

```bash
make serve-docs
```

# Test

The following section is an overview of test for idmtools. All tests are located under the `tests` folder in each package folder. 
Test are written to be ran my `py.test`. The test are partially configured through the pytest.ini. Additional test configuration happens
dynamically through the `make test` commands. 

Here are a list of jobs related to test from the makefile.

```bash
coverage-report     :Generate HTML report from coverage. Requires running coverage run first(coverage, coverage-smoke, coverage-all)
coverage-smoke      :Generate a code-coverage report
test                :Run default set of tests which exclude comps and docker tests
test-all            :Run all our tests
test-comps          :Run our comps tests
test-docker         :Run our docker tests
test-failed         :Run only previously failed tests
test-long           :Run any tests that takes more than 30s
test-no-long        :Run any tests that takes less than 30s
test-python         :Run our python tests
test-report         :Launch test report in browser
test-smoke          :Run our smoke tests
```

The jobs can be ran at the root of the project or the within each package.

The root also has additional jobs at the root. Those jobs are
```
aggregate-html-reports:Aggregate html test reports into one directory
allure-report       :Download report as zip
start-allure        :start the allue docker report server
stop-allure         :Stop Allure
test-all-allure     :Run all tests and enable allure
test-smoke-allure   :Run smoke tests and enable allure
```

## Test Reports

Allure is a test visualization utility. It can be accessed after running `make test-all-allure` or `make test-smoke-allure` at http://localhost:5050/allure-docker-service/latest-report in the root of the repo.

There is also an html report available after running any tests http://localhost:8001. There will be multiple html files. Each file represents a specific run of tests for a package. 
Some packages, the ones that have both serial and parallel tests, will have two files. The file generated by serial tests will have the prefix `serial.`.

## Running smoke tests or all tests from Github Actions

To run smoke tests from Github Actions when push or pull request, put "Run smoke test!" in your commit message

To run all tests from Github Actions when push or pull request, put "Run all test!" in your commit message

```bash
$ git commit -m 'fix bug xxx, ran smoke test, linted'
$ git push
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

In addition, you can rerun just the failed test using either the top-level `pymake test-failed` rule or by using the `--lf` switch on py.test

## Installing from a Pull Request

Sometimes, like when testing a new feature, it is useful to install a development or early version. We can do this directly from GitHub PRs using the following commands

To install idmtools from a specific PR you can use the following script replacing 123 with the number of your PR

```
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools&subdirectory=idmtools_core"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_platform_comps&subdirectory=idmtools_platform_comps"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_cli&subdirectory=idmtools_cli"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_models&subdirectory=idmtools_models"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_platform_local&subdirectory=idmtools_platform_local"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@refs/pull/123/head#egg="idmtools_test&subdirectory=idmtools_test"
```

To install from a specific branch, see [Installing From Development Branch(or other specific branch)](#installing-from-development-branchor-other-specific-branch)

You can use either *git+https://* or *git+ssh://git@*

## Installing From Development Branch(or other specific branch)

To install from the development branch, use the following commands

```
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools&subdirectory=idmtools_core"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_platform_comps&subdirectory=idmtools_platform_comps"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_cli&subdirectory=idmtools_cli"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_models&subdirectory=idmtools_models"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_platform_local&subdirectory=idmtools_platform_local"
pip install git+https://github.com/InstituteforDiseaseModeling/idmtools.git@dev#egg="idmtools_test&subdirectory=idmtools_test"
```

To install a different github branch, change the *@dev* in each command to *@<branch name>* where *branch_name* is the name of branch you would like to install from. To install from a PR, see [Installing from a Pull Request](#installing-from-a-pull-request)

You can use either *git+https://* or *git+ssh://git@*