.PHONY: clean lint test coverage release-local dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c
PACKAGE_NAME=idmtools_test
PY?=python
PDS=$(PY) ../dev_scripts/
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py
CWD=$($(IPY) "import os; print(os.getcwd())")
help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build"

clean-all:  ## Deleting package info hides plugins so we only want to do that for packaging
	@make clean
	$(CLDIR) --dir-patterns "**/*.egg-info/"
# Dev and test related rules

lint: ## check style with flake8
	@+$(IPY) "import os; os.chdir('..'); os.system('flake8 --ignore=E501 idmtools_test')"

test: ## Run our tests
	@+$(IPY) "print('No Tests')"

test-failed: ## Run only previously failed tests
	@+$(IPY) "print('No Tests')"

test-long: ## Run our tests
	@+$(IPY) "print('No Tests')"

test-no-long: ## Run our tests
	@+$(IPY) "print('No Tests')"

test-no-comps: ## Run our tests
	@+$(IPY) "print('No Tests')"

test-all: ## Run our  docker tests as well
	@+$(IPY) "print('No Tests')"

coverage: ## Generate a code-coverage report
	@+$(IPY) "print('No Tests')"

coverage-all: ## Generate a code-coverage report
	@+$(IPY) "print('No Tests')"

# Release related rules

release-local: ## package and upload a release to http://localhost:7171
	@make dist
	twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*

dist: ## build our package
	@make clean
	python setup.py sdist

release-staging: ## perform a release to staging
	bump2version build --allow-dirty
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/idm-pypi-staging/ dist/*

# Use before release-staging-release-commit to confirm next version.
release-staging-release-dry-run: ## perform a release to staging and bump the minor version.
	bump2version patch --dry-run --allow-dirty

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-release-commit: ## perform a release to staging and commit the version.
	bump2version release --commit
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/idm-pypi-staging/ dist/*

bump-patch:
	bump2version patch --commit

bump-minor: ## bump the minor version
	bump2version minor --commit