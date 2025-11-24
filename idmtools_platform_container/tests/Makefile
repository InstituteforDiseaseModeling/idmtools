HTML_TEST_REPORT ?= container.test_results.html
PARALLEL_TEST_COUNT = 2
include $(abspath ../../dev_scripts/test_root.mk)

PACKAGE_NAME=idmtools_platform_container
COVERAGE_DEPS=idmtools idmtools_cli idmtools_models idmtools_platform_general
ALL_COV = $(PACKAGE_NAME) $(COVERAGE_DEPS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append $(foreach pkg,$(ALL_COV),--cov=$(pkg))