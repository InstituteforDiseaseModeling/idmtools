# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Development Setup](#development-setup)
  - [Initial Setup](#initial-setup)
  - [IDE Configuration (PyCharm)](#ide-configuration-pycharm)
- [Common Development Commands](#common-development-commands)
  - [Top-Level Commands (run from repo root)](#top-level-commands-run-from-repo-root)
  - [Package-Level Commands (run from individual package directories)](#package-level-commands-run-from-individual-package-directories)
  - [Running Specific Tests](#running-specific-tests)
- [Test Markers](#test-markers)
- [Architecture](#architecture)
  - [Plugin System](#plugin-system)
  - [Core Entity Hierarchy](#core-entity-hierarchy)
  - [Platform Interface (IPlatform)](#platform-interface-iplatform)
- [Linting Configuration](#linting-configuration)
- [Version Management](#version-management)
- [Installation Extras](#installation-extras)
- [Important Notes](#important-notes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Project Overview

idmtools is a collection of Python tools for streamlining interactions with disease modeling workflows on HPC clusters and various compute platforms (COMPS, Slurm, Docker containers). This is a **monorepo** containing multiple related packages.

## Repository Structure

This is a monorepo with the following packages:

- **idmtools_core**: Core APIs, logic, and platform interface definitions
- **idmtools_cli**: Command-line interface tools
- **idmtools_models**: Python, R, and generic model implementations
- **idmtools_platform_comps**: COMPS platform support
- **idmtools_platform_container**: Docker container platform support
- **idmtools_platform_general**: File and Process platforms
- **idmtools_platform_slurm**: Slurm cluster platform support
- **idmtools_test**: Testing utilities and fixtures

Each package has its own:
- `pyproject.toml` for package configuration
- `Makefile` for development tasks (use `pymake` on Windows)
- `tests/` directory with pytest configuration
- `README.md` with package-specific details

## Development Setup

### Initial Setup
```bash
# Create and activate virtual environment
python -m venv idmtools
idmtools\Scripts\activate  # Windows

# Install all packages in development mode
python dev_scripts/bootstrap.py
```

The bootstrap script installs all packages with development extras and configures examples to use staging environments.

### IDE Configuration (PyCharm)
Mark these directories as "Source Root" for proper indexing:
- `idmtools_cli`
- `idmtools_core`
- `idmtools_models`
- `idmtools_platform_comps`
- `idmtools_platform_container`
- `idmtools_platform_general`
- `idmtools_platform_slurm`
- `idmtools_test`

## Common Development Commands

### Top-Level Commands (run from repo root)
```bash
# Setup
make setup-dev              # Full dev setup with Docker builds
make setup-dev-no-docker    # Dev setup without Docker builds

# Testing
make test                   # Run tests excluding COMPS and Docker
make test-smoke             # Run smoke tests (fastest)
make test-all               # Run all tests (serial + parallel)
make test-failed            # Rerun only failed tests
make test-comps             # Run COMPS platform tests
make test-docker            # Run Docker platform tests

# Code Quality
make lint                   # Run flake8 on all packages
make clean                  # Clean temporary files
make clean-all              # Deep clean (requires re-running setup-dev)

# Coverage
make coverage               # Generate coverage report
make coverage-report        # View coverage in browser

# Documentation
make build-docs             # Build documentation
make build-docs-server      # Build docs with auto-reload at localhost:8000
```

### Package-Level Commands (run from individual package directories)
```bash
cd idmtools_core  # or any other package

# Testing
make test                   # Run package tests (excludes comps/docker)
make test-smoke             # Run smoke tests
make test-all               # Run all tests for this package
make coverage               # Generate coverage for this package

# Code Quality
make lint                   # Lint this package only
make clean                  # Clean this package
```

### Running Specific Tests
```bash
# From a package's tests directory:
cd idmtools_core/tests
py.test test_templated_simulation.py::TestTemplatedSimulation::test_generator

# Using the run_all.py script for filtered tests:
python dev_scripts/run_all.py -sd 'tests' --exec "py.test -m 'not comps and python'"
python dev_scripts/run_all.py -sd 'tests' --exec "py.test -k 'batch'"
```

## Test Markers

Tests use pytest markers to categorize functionality:
- `smoke`: Quick smoke tests (run these first)
- `comps`: COMPS platform tests (require COMPS access)
- `docker`: Docker platform tests (require Docker)
- `python`: Python model tests
- `serial`: Tests requiring serial execution
- `long`: Tests taking >30s
- `performance`: Performance benchmarks
- `ssmt`: SSMT-specific tests
- `cli`: CLI tests

## Architecture

### Plugin System
idmtools uses a plugin architecture based on Python entry points:

- **Platform plugins** (`idmtools_platform`): Register new compute platforms
- **Task plugins** (`idmtools_task`): Register new task types (models)
- **Experiment plugins** (`idmtools_experiment`): Register experiment types
- **Hook plugins** (`idmtools_hooks`): Register lifecycle hooks
- **CLI plugins** (`idmtools_cli.cli_plugins`): Extend CLI commands

Platforms are discovered and instantiated via the `Platform` factory from plugin specifications.

### Core Entity Hierarchy
- **IEntity**: Base interface for all entities
- **IItem**: Items that can be persisted
- **ITask**: Tasks that run simulations (CommandTask, PythonTask, DockerTask, etc.)
- **Simulation**: Individual simulation runs
- **Experiment**: Collection of simulations with shared configuration
- **Suite**: Collection of experiments
- **IWorkflowItem**: Platform-specific workflow items (e.g., SSMTWorkItem)
- **AssetCollection**: File assets for entities

### Platform Interface (IPlatform)
All platforms implement `IPlatform`, which provides:
- Operations interfaces for experiments, simulations, suites, workflow items, and assets
- Platform-specific entity creation and commissioning
- File handling and asset management
- Translation between idmtools objects and platform-specific objects

Platform implementations handle the actual job submission, monitoring, and data retrieval for their respective compute environments.

## Linting Configuration

Flake8 settings (`.flake8`):
- Enforces Google-style docstrings
- Ignores: E501 (line length), W291, D205, D212, D200, D411, D105, E722
- Excludes: tests, docs, examples, prototypes, idmtools_test

Always run `make lint` before opening a PR and fix all linting errors.

## Version Management

Versions are managed using `setuptools-scm` from git tags. Each package's version is derived from the git repository state.

## Installation Extras

The core package (`idmtools`) supports multiple installation profiles:
- `pip install idmtools[full]`: All packages except idmtools-test
- `pip install idmtools[idm]`: Core + CLI + models + COMPS
- `pip install idmtools[slurm]`: Core + CLI + models + Slurm
- `pip install idmtools[container]`: Core + CLI + models + General + Container
- `pip install idmtools[test]`: Development/testing dependencies

## Important Notes

- **Docker authentication**: Login with `echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin` before running Docker-related commands
- Tests run with a 600-second timeout by default
- Serial tests and parallel tests are run separately; parallel tests use 8 workers by default
- The `bootstrap.py` script configures examples to use staging environments for testing
