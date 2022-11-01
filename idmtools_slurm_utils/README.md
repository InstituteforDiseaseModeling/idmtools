![Staging: idmtools-slurm-utils](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-slurm-utils/badge.svg?branch=dev)

# idmtools-slurm-utils

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Development Tips](#development-tips)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`
