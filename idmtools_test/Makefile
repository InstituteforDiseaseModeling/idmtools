.PHONY: clean lint test coverage dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c
PACKAGE_NAME=idmtools_test
PY?=python
PDS=$(PY) ../dev_scripts/
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py
CWD=$($(IPY) "import os; print(os.getcwd())")
help:
	help-from-makefile -f ./Makefile

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build"

clean-all: clean ## Deleting package info hides plugins so we only want to do that for packaging
	$(CLDIR) --dir-patterns "**/*.egg-info/"
# Dev and test related rules

lint: ## check style with flake8
	@+$(IPY) "import os; os.chdir('..'); os.system('flake8 --ignore=E501,W291 idmtools_test')"

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

test-smoke: ## Run our smoke tests
	@+$(IPY) "print('No Tests')"

coverage: ## Generate a code-coverage report
	@+$(IPY) "print('No Tests')"

coverage-all: ## Generate a code-coverage report
	@+$(IPY) "print('No Tests')"

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