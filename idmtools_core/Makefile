.PHONY: clean lint test coverage dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c
PACKAGE_NAME=idmtools_core
PY?=python
PDS=$(PY) ../dev_scripts/
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py
TEST_EXTRA_OPTS?=
TEST_REPORT ?= test_results.xml
HTML_TEST_REPORT ?= core.test_results.html
TEST_COMMAND = DOCKER_REPO=docker-staging NO_SPINNER=1 cd tests && py.test --junitxml=$(TEST_REPORT) --html=$(HTML_TEST_REPORT) --self-contained-html $(TEST_EXTRA_OPTS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append --cov=idmtools --cov=idmtoools_cli --cov=idmtools_models --cov=idmtools_platform_comps

help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build"

clean-all: clean ## Deleting package info hides plugins so we only want to do that for packaging
	$(CLDIR) --dir-patterns "**/*.egg-info/"

lint: ## check style with flake8
	flake8 --ignore=E501,W291 $(PACKAGE_NAME) tests

test: ## Run our tests
	$(TEST_COMMAND) -m "not comps and not docker"

test-all: ## Run all our tests
	$(TEST_COMMAND) -m "serial"
	mv tests/test_results.xml tests/serial.test_results.xml
	mv tests/$(HTML_TEST_REPORT) tests/core.serial.test_results.html
	$(TEST_COMMAND) -n 8 -m "not serial"
	junitparser merge tests/serial.test_results.xml tests/$(TEST_REPORT) tests/$(TEST_REPORT)

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

test-smoke: ## Run our smoke tests
	$(TEST_COMMAND) -n 4 -m "smoke and not serial"
	mv tests/$(TEST_REPORT)tests/serial.test_results.xml
	mv tests/$(HTML_TEST_REPORT) tests/core.serial.test_results.html
	$(TEST_COMMAND) -m "smoke and serial"
	junitparser merge tests/serial.test_results.xml tests/$(TEST_REPORT) tests/$(TEST_REPORT)

test-report: ## Launch test report in browser
	$(PDS)/launch_dir_in_browser.py tests/core.test_results.html

coverage-report: coverage ## Generate HTML report from coverage. Requires running coverage run first(coverage, coverage-smoke, coverage-all)
	coverage report -m
	coverage html -i

coverage-report-view: coverage-report
	$(PDS)/launch_dir_in_browser.py htmlcov/index.html

coverage: clean ## Generate a code-coverage report
	# We have to run in our tests folder to use the proper config
	$(TEST_COMMAND) $(COVERAGE_OPTS) -m "not comps and not docker"
	mv tests/.coverage .coverage

coverage-smoke: clean ## Generate a code-coverage report
	# We have to run in our tests folder to use the proper config
	$(TEST_COMMAND) $(COVERAGE_OPTS) -m "smoke"
	mv tests/.coverage .coverage

coverage-all: ## Generate a code-coverage report using all tests
	# We have to run in our tests folder to use the proper config
	$(TEST_COMMAND) $(COVERAGE_OPTS)
	mv tests/.coverage .coverage

# Release related rules

dist: clean ## build our package
	python setup.py sdist

release-staging: dist ## perform a release to staging
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/idm-pypi-staging/ dist/*

bump-release: ## bump the release version.
	bump2version release --commit

# Use before release-staging-release-commit to confirm next version.
bump-release-dry-run: ## bump the release version. (dry run)
	bump2version release --dry-run --allow-dirty --verbose

bump-patch: ## bump the patch version
	bump2version patch --commit

bump-minor: ## bump the minor version
	bump2version minor --commit

bump-major: ## bump the major version
	bump2version major --commit

bump-patch-dry-run: ## bump the patch version(dry run)
	bump2version patch --dry-run --allow-dirty --verbose

bump-minor-dry-run: ## bump the minor version(dry run)
	bump2version minor --dry-run --allow-dirty --verbose

bump-major-dry-run: ## bump the major version(dry run)
	bump2version major --dry-run --allow-dirty --verbose

update-dependent-libraries: ## update any libraries in repo that depend on core
	$(PDS)update_core_version.py