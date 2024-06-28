![Staging: idmtools-core](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-core/badge.svg?branch=dev)

# idmtools-core

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
- [Installing](#installing)
- [Development Tips](#development-tips)
- [Future Work](#future-work)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Overview

idmtools provides the APIS, logic, and other operations to provision, execute, analysis, and manage jobs running on an HPC cluster

To see the full API documentation, see https://institutefordiseasemodeling.github.io/idmtools/idmtools_index.html


# Installing

```bash
pip install idmtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
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

# Future Work

* Add new analyze api to platform
    * Where does this go?
    * Move current code to Comps
    * Add support for platform specific bootstrap scripts

