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

idmtools-core provides the foundational APIs, core logic, and essential utilities for provisioning, executing, analyzing, and managing jobs across multiple platforms.

To see the full documentation, see https://institutefordiseasemodeling.github.io/idmtools/index.html


# Installing

```bash
pip install idmtools
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

