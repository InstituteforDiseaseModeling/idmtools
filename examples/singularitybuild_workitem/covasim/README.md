<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
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



Development Scripts
===================
When you are developing with covasim and changing code within the covasim library, or often updating the package, you most likely would want to use the `run_covasim_dev_comps.py` example. This example
by default get the latest Covasim package from github and then adds it the assets. This could be adapted to add a local github checkout as well. 