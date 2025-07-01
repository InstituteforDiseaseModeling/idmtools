
HTML_TEST_REPORT ?= cli.test_results.html
# Enable only parallel testing since cli has no serial tests
PARALLEL_TESTING = 1
include $(abspath ../../dev_scripts/test_root.mk)

PACKAGE_NAME=idmtools_cli
COVERAGE_DEPS = idmtools
ALL_COV = $(PACKAGE_NAME) $(COVERAGE_DEPS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append $(foreach pkg,$(ALL_COV),--cov=$(pkg))