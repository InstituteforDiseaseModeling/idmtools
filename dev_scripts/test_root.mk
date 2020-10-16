.PHONY: help clean test test-all test-failed test-long test-no-long test-comps test-docer test-docker test-python test-smoke test-report coverage-report coverage coverage-smoke coverage-all coverage-report-view merge-reports
.EXPORT_ALL_VARIABLES:
PY?=python
# Get dev scripts from any location
mkfile_path := $(lastword $(MAKEFILE_LIST))
mkfile_dir := $(dir $(mkfile_path))
# Platform Independent options for common commands
MV?=mv
RM?=rm
# Convience function for running dev scripts
PDS=$(PY) $(mkfile_dir)
# Where should we store our reports
REPORT_DIR?= reports
TEST_REPORT ?= test_results.xml
# Test Configuration
SERIAL_TESTING?=
PARALLEL_TESTING?=
TEST_EXTRA_OPTS?=
DOCKER_REPO?=docker-staging
NO_SPINNER?=1
PARALLEL_TEST_COUNT?=8
TEST_COMMAND =  py.test --timeout=360 --junitxml=$(REPORT_DIR)/$(TEST_REPORT) --html=$(REPORT_DIR)/$(HTML_TEST_REPORT) --self-contained-html $(TEST_EXTRA_OPTS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append --cov=idmtools --cov=idmtoools_cli --cov=idmtools_models --cov=idmtools_platform_comps --cov=idmtools_platform_local --cov=../../idmtools_cli/


help:  ## This help
	$(PDS)get_help_from_makefile.py -f $(mkfile_path)

clean:
	-$(RM) -rf .pytest_cache .test_platform reports assets *.log *.log* *.buildlog __pycache__ *.html *.xml .coverage

merge-reports: ## merge results from serial and parallel tests
	junitparser merge $(REPORT_DIR)/serial.test_results.xml $(REPORT_DIR)/$(TEST_REPORT) $(REPORT_DIR)/$(TEST_REPORT)

mv-serial-reports: ## Moves report to serial folder
	$(MV) $(REPORT_DIR)/$(TEST_REPORT) $(REPORT_DIR)/serial.$(TEST_REPORT)
	$(MV) $(REPORT_DIR)/$(HTML_TEST_REPORT) $(REPORT_DIR)/serial.$(HTML_TEST_REPORT)

test: ## Run default set of tests which exclude comps and docker tests
	-mkdir reports
	$(TEST_COMMAND) -m "not comps and not docker"

reports-exist:
	-mkdir reports

test-all: reports-exist ## Run all our tests
ifneq (1, $(PARALLEL_TESTING)) # Only run these tests if Parallel Only Testing is disabled
	-echo "Running Serial Tests"
	$(TEST_COMMAND) -m "serial"
	$(MAKE) mv-serial-reports
endif
ifneq (1, $(SERIAL_TESTING)) # Only run these tests if Serial Only Testing is disabled
	-echo "Running Parallel Tests"
	$(TEST_COMMAND) -n $(PARALLEL_TEST_COUNT) -m "not serial"
endif
ifneq (1, $(PARALLEL_TESTING))
ifneq (1, $(SERIAL_TESTING))
	$(MAKE) merge-reports
endif
endif

test-failed: reports-exist ## Run only previously failed tests
	$(TEST_COMMAND) --lf

test-long: reports-exist ## Run any tests that takes more than 30s
	$(TEST_COMMAND) -m "long"

test-no-long: reports-exist ## Run any tests that takes less than 30s
	$(TEST_COMMAND) -m "not long"

test-comps: reports-exist ## Run our comps tests
	$(TEST_COMMAND) -m "comps"

test-docker: reports-exist ## Run our docker tests
	$(TEST_COMMAND) -m "docker"

test-python: reports-exist ## Run our python tests
	$(TEST_COMMAND) -m "python"

test-smoke: reports-exist ## Run our smoke tests
ifneq (1, $(PARALLEL_TESTING)) # Only run these tests if Parallel Only Testing is disabled
	-echo "Running Serial Tests"
	$(TEST_COMMAND) -m "smoke and serial"
	$(MAKE) mv-serial-reports
endif
ifneq (1, $(SERIAL_TESTING)) # Only run these tests if Serial Only Testing is disabled
	-echo "Running Parallel Tests"
	$(TEST_COMMAND) -n $(PARALLEL_TEST_COUNT) -m "smoke and not serial"
endif
ifneq (1, $(PARALLEL_TESTING))
ifneq (1, $(SERIAL_TESTING))
	$(MAKE) merge-reports
endif
endif

test-report: ## Launch test report in browser
	$(PDS)/launch_dir_in_browser.py $(REPORT_DIR)/

coverage-report: ## Generate HTML report from coverage. Requires running coverage run first(coverage, coverage-smoke, coverage-all)
	coverage report -m
	coverage html -i --directory=$(REPORT_DIR)/coverage

coverage-report-view: coverage-report ## Launch coverage report. Require running coverage beforehand
	$(PDS)/launch_dir_in_browser.py $(REPORT_DIR)/coverage/index.html

coverage: clean ## Generate a code-coverage report
	$(TEST_COMMAND) $(COVERAGE_OPTS) -m "not comps and not docker"

coverage-smoke: clean ## Generate a code-coverage report
ifneq (1, $(PARALLEL_TESTING)) # Only run these tests if Parallel Only Testing is disabled
	-echo "Running Serial Tests"
	$(TEST_COMMAND) $(COVERAGE_OPTS) -m "smoke and serial"
endif
ifneq (1, $(SERIAL_TESTING)) # Only run these tests if Serial Only Testing is disabled
	-echo "Running Parallel Tests"
	$(TEST_COMMAND) $(COVERAGE_OPTS) -n $(PARALLEL_TEST_COUNT) -m "smoke and not serial"
endif

coverage-all: ## Generate a code-coverage report using all tests
ifneq (1, $(PARALLEL_TESTING)) # Only run these tests if Parallel Only Testing is disabled
	-echo "Running Serial Tests"
	$(TEST_COMMAND) $(COVERAGE_OPTS) -m "serial"
endif
ifneq (1, $(SERIAL_TESTING)) # Only run these tests if Serial Only Testing is disabled
	-echo "Running Parallel Tests"
	$(TEST_COMMAND) $(COVERAGE_OPTS) -n $(PARALLEL_TEST_COUNT) -m "not serial"
endif