![Upload idmtools-test to Staging](https://github.com/devclinton/idmtools/workflows/Upload%20idmtools-test%20to%20Staging/badge.svg)

# idmtools-test

<!-- START doctoc -->
<!-- END doctoc -->

## Installing

```bash
pip install idmtools-test --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

# Testing tips

Most project have markers defined for tests. You can run select test at the command line using marker filter

For example to run just docker related tests, you can user
`pytest -m "docker"`

The local runner tests make