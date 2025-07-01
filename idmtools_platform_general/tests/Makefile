HTML_TEST_REPORT ?= general.test_results.html
# slurm only has serial tests
PARALLEL_TEST_COUNT = 1
include $(abspath ../../dev_scripts/test_root.mk)

PACKAGE_NAME=idmtools_platform_general
COVERAGE_DEPS = idmtools idmtools_cli idmtools_models idmtools_platform_file idmtools_platform_process
ALL_COV = $(PACKAGE_NAME) $(COVERAGE_DEPS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append $(foreach pkg,$(ALL_COV),--cov=$(pkg))


