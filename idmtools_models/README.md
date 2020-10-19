![Staging: idmtools-models](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-models/badge.svg?branch=dev)

# idmtools-models

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Development Tips](#development-tips)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-models --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
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

