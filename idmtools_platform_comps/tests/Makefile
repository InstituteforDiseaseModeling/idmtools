HTML_TEST_REPORT ?= comps.test_results.html
# Set comps to high because we mostly just wait on COMPS to finish
PARALLEL_TEST_COUNT ?= 12
include $(abspath ../../dev_scripts/test_root.mk)

PACKAGE_NAME=idmtools_platform_comps
COVERAGE_DEPS = idmtools idmtools_cli idmtools_models
ALL_COV = $(PACKAGE_NAME) $(COVERAGE_DEPS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append $(foreach pkg,$(ALL_COV),--cov=$(pkg))