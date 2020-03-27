![Upload idmtools-platform-comps to Staging](https://github.com/devclinton/idmtools/workflows/Upload%20idmtools-platform-comps%20to%20Staging/badge.svg)

# idmtools-platform-comps

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Development Tips](#development-tips)
- [Building SSMT Docker Image](#building-ssmt-docker-image)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
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

# Building SSMT Docker Image

To build the SSMT Docker image, follow these steps

1. ```bash
   docker login docker-production.packages.idmod.org
   ```
2. ```bash
   make ssmt-image-local
   ```
3. When prompted, enter your idm username and password
