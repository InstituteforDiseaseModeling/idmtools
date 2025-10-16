.PHONY: help clean lint test test-all test-failed test-long test-no-long test-comps test-docer test-docker test-python test-smoke test-report coverage-report coverage coverage-smoke coverage-all coverage-report-view merge-reports dist release-staging bump-release bump-release-dry-run bump-minor bump-minor-dry-run bump-major bump-major-dry-run bump-patch bump-patch-dry-run
.EXPORT_ALL_VARIABLES:
# Get dev scripts from any location
mkfile_path := $(lastword $(MAKEFILE_LIST))
mkfile_dir := $(dir $(mkfile_path))
# Platform Independent options for common commands
MV?=mv
RM?=rm
# Convience function for running dev scripts
PDS=$(PY) $(mkfile_dir)
PY?=python
IPY=python -c
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py
PYPI_URL?=https://packages.idmod.org/api/pypi/idm-pypi-staging/

help: 
	help-from-makefile -f $(mkfile_path)

clean: ## Clean most of the temp-data from the project
	$(MAKE) -C tests clean
	-rm -rf *.pyc *.pyo *.done *.log .coverage dist build **/__pycache__

clean-all: clean ## Deleting package info hides plugins so we only want to do that for packaging
	-rm -rf **/*.egg-info/

lint: ## check style with flake8
	flake8 $(abspath ../$(PACKAGE_NAME))

test: ## Run our tests
	$(MAKE) -C tests $@

test-all: ## Run all our tests
	$(MAKE) -C tests $@

test-failed: ## Run only previously failed tests
	$(MAKE) -C tests $@

test-all-no-ssmt: ## Run all our tests without ssmt tests
	$(MAKE) -C tests $@

test-long: ## Run any tests that takes more than 30s
	$(MAKE) -C tests $@

test-no-long: ## Run any tests that takes less than 30s
	$(MAKE) -C tests $@

test-comps: ## Run our comps tests
	$(MAKE) -C tests $@

test-docker: ## Run our docker tests
	$(MAKE) -C tests $@

test-python: ## Run our python tests
	$(MAKE) -C tests $@

test-smoke: ## Run our smoke tests
	$(MAKE) -C tests $@

test-ssmt: ## Run our ssmt tests
	$(MAKE) -C tests $@

test-report: ## Launch test report in browser
	$(MAKE) -C tests $@

coverage-report: coverage ## Generate HTML report from coverage. Requires running coverage run first(coverage, coverage-smoke, coverage-all)
	$(MAKE) -C tests $@

coverage-report-view: coverage-report
	$(MAKE) -C tests $@

coverage: clean ## Generate a code-coverage report
	$(MAKE) -C tests $@

coverage-smoke: clean ## Generate a code-coverage report
	$(MAKE) -C tests $@

coverage-all: ## Generate a code-coverage report using all tests
	$(MAKE) -C tests $@

# Release related rules
#######################

dist: clean ## build our package
	python -m build --sdist

release-staging: dist ## perform a release to staging
	twine upload --verbose --repository-url $(PYPI_URL) dist/*

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
