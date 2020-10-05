TEST_EXTRA_OPTS?=
TEST_REPORT ?= test_results.xml
HTML_TEST_REPORT ?= comps.test_results.html
TEST_COMMAND = DOCKER_REPO=docker-staging NO_SPINNER=1 py.test --junitxml=$(TEST_REPORT) --html=$(HTML_TEST_REPORT) --self-contained-html $(TEST_EXTRA_OPTS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append --cov=idmtools --cov=idmtoools_cli --cov=idmtools_models --cov=idmtools_platform_comps


test: ## Run our tests
	$(TEST_COMMAND) -m "not comps and not docker"

test-all: ## Run all our tests
	$(TEST_COMMAND) -n 8 -m "not serial"
	# $(FULL_TEST_CMD) -m "serial"' # No serial tests at moment

test-failed: ## Run only previously failed tests
	$(TEST_COMMAND) --lf

test-long: ## Run any tests that takes more than 30s
	$(TEST_COMMAND) -m "long"

test-no-long: ## Run any tests that takes less than 30s
	$(TEST_COMMAND) -m "not long"

test-comps: ## Run our comps tests
	$(TEST_COMMAND) -m "comps"

test-docker: ## Run our docker tests
	$(TEST_COMMAND) -m "docker"

test-python: ## Run our python tests
	$(TEST_COMMAND) -m "python"

test-smoke: ## Run smoke tests
	$(TEST_COMMAND) -n 8 -m "smoke and not serial"

test-ssmt: ## Run our ssmt tests
	$(TEST_COMMAND) -m "ssmt"