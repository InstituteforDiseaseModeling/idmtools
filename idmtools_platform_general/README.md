![Staging: idmtools-platform-file](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-file/badge.svg?branch=dev)

# idmtools-platform-general

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Development Tips](#development-tips)
- [Use Cases](#use-cases)
- [Feature Roadmap](#feature-roadmap)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-platform-general --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
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

# Use Cases

* Testing
  * Test core functionality
  * Performance Testing
* Integration with other systems
  * Other HPC Systems
  * Local Executions Systems
  * Jupyter notebooks
* Basis for future local platforms
  * Process
  * Thread
  * Dask
  * Asyncio

# Feature Roadmap

* First Version
  * Support for basic provisioning on a linux filesystem