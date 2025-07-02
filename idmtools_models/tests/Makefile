
HTML_TEST_REPORT ?= models.test_results.html
include $(abspath ../../dev_scripts/test_root.mk)

PACKAGE_NAME=idmtools_models
COVERAGE_DEPS = idmtools idmtools_cli
ALL_COV = $(PACKAGE_NAME) $(COVERAGE_DEPS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append $(foreach pkg,$(ALL_COV),--cov=$(pkg))
