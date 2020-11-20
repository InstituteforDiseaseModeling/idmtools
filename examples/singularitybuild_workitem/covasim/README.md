<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
- [Development Scripts](#development-scripts)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Overview
========

This directory contains examples using contains and the covasim image, as well as driving those through a snakemake script.


To run you should first run `pip install -r requirements.txt`

After that, you can execute the snakemake workflow using

```bash
snakemake -j
````

Development Scripts
===================
When you are developing with covasim and changing code within the covasim library, or often updating the package, you most likely would want to use the `run_covasim_dev_comps.py` example. This example
by default get the latest Covasim package from github and then adds it the assets. This could be adapted to add a local github checkout as well. 