# User guide

Complete guide to using idmtools for disease modeling workflows.

## Overview

This guide covers all aspects of using idmtools:

- Creating and running simulations
- Managing experiments
- Working with different platforms
- Analyzing results
- Best practices

## Key concepts
- Task — Defines *what* to run. A task wraps your model script, its parameters, and any assets it needs.
- Simulation — A single run of a task with a specific set of parameters.
- Experiment — A collection of simulations, typically created from a parameter sweep.
- Suite - A collection of experiments, it is optional for most of the cases.
- Platform — Where your experiment runs (COMPS, Slurm, Container, Process).
- Assets — Files your simulations need (scripts, data files, config files, container images).
- Analyzer — Post-processing logic that runs after simulations complete.

## Basic workflow
- Write your model — Create a script that accepts parameters and produces output.
- Define a task — Wrap your model in an idmtools Task.
- Build simulations — Use a `SimulationBuilder` to sweep over parameters.
- Create an experiment — Group your simulations into an experiment.
- Run — Submit the experiment to a platform.
- Analyze — Use an Analyzer to aggregate results.

## Topics

### Core concepts

- [Creating Simulations & Experiments](creating-simulations.md) - Build simulations and organize them into experiments
- [Asset Management](assets.md) - Handle files and resources
- [Parameter Sweeps](../tutorials/parameter-sweeps.md) - Run parameter variations
- [Data Analysis](../data-analysis/index.md) - Process simulation outputs with Analyzers, AnalyzeManager, and PlatformAnalysis

### Quick navigation

<div class="grid cards" markdown>

-   __Simulations & Experiments__

    Create simulations and organize them into experiments

    [Go to guide →](creating-simulations.md)

-   __Parameter Sweeps__

    Run systematic parameter variations

    [Go to guide →](../tutorials/parameter-sweeps.md)

-   __Analysis__

    Process and analyze simulation results

    [Go to guide →](../data-analysis/index.md)

</div>

## Getting help

- Check the [FAQ](../faq/index.md)
- See [Tutorials](../tutorials/index.md) for examples
- Browse [API Reference](../api/index.md) for details
