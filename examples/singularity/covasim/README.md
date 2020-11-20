<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
  - [Getting Started](#getting-started)
  - [Snakemake](#snakemake)
- [Development Scripts](#development-scripts)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Overview
========

This directory contains examples using contains and the covasim image, as well as driving those through a snakemake script.


Getting Started
---------------

1. It is recommended you create a virtualenv
2. After creating a virtualenv, run  `pip install -r requirements.txt`
3. You can then execute with `snakemake -j` or by running `python3 create_covasim_sif.py` then the `run_*` scripts.

Snakemake
---------

The snakefile demonstrated how to build a simple workflow. Here we are just executing a series of experiments when our base image changes.

We start the file with the rule `all`. Here we list all the files that must exist when we expect everything to be done.

We then define a list of rules that actually do the work. For these rules, we specify the inputs, output, and the command. Snakemake will determine
the execution order by building a directed acyclic graph(DAG) using of the work using the input and outputs to determine execution order. It then executes those items.
Snakemake also support change detection my checksums the inputs. Any inputs that have changed will cause a job to be re-ran. 


Development Scripts
===================
When you are developing with covasim and changing code within the covasim library, or often updating the package, you most likely would want to use the `run_covasim_dev.py` example. This example
by default get the latest Covasim package from github and then adds it the assets. This could be adapted to add a local github checkout as well. 