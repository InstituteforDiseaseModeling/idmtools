![Staging: idmtools-test](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-test/badge.svg?branch=dev)

# idmtools-test

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Testing tips](#testing-tips)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-test --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

# Testing tips

Most project have markers defined for tests. You can run select test at the command line using marker filter

For example to run just docker related tests, you can user
`pytest -m "docker"`

The local runner tests make
