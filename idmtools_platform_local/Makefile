.PHONY: clean lint test coverage dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c
BASE_PIP_URL="packages.idmod.org/api/pypi/idm-pypi-"
STAGING_PIP_URL?="https://$(BASE_PIP_URL)staging/simple"
PRODUCTION_PIP_URL?="https://$(BASE_PIP_URL)production/simple"
PACKAGE_NAME=idmtools_platform_local
PY?=python
PDS=$(PY) ../dev_scripts/
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py
CWD=$($(IPY) "import os; print(os.getcwd())")
TEST_EXTRA_OPTS?=
TEST_REPORT ?= test_results.xml
HTML_TEST_REPORT ?= models.test_results.html
TEST_COMMAND = DOCKER_REPO=docker-staging NO_SPINNER=1 cd tests && py.test --junitxml=$(TEST_REPORT) --html=$(HTML_TEST_REPORT) --self-contained-html $(TEST_EXTRA_OPTS)
COVERAGE_OPTS := --cov-config=.coveragerc --cov-branch --cov-append --cov=idmtools --cov=idmtoools_cli --cov=idmtools_models --cov=idmtools_platform_comps

help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build,idmtools_webui/build"

clean-all: clean  ## Deleting package info hides plugins so we only want to do that for packaging
	$(CLDIR) --dir-patterns "**/*.egg-info/"
	@+$(IPY) "import os; os.chdir('idmtools_webui'); os.system('python build.py clean')"

dev:
	echo $(CWD)

# Dev and test related rules
lint: ## check style with flake8
	$(PDR) -w '..' -ex 'flake8 --ignore=E501,W291 $(PACKAGE_NAME)'

test: ## Run our tests
	$(TEST_COMMAND) -m "not comps and not docker"'

test-all: ## Run all our tests
	$(TEST_COMMAND) -m "serial"
	# $(FULL_TEST_CMD) -n 8 -m "not serial"' # Currently all local is serial

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
	$(TEST_COMMAND) -m "smoke and serial"

coverage-report:  ## Generate HTML report from coverage. Requires running coverage run first(coverage, coverage-smoke, coverage-all)
	coverage report -m
	coverage html -i

## View coverage report (Comment out https://github.com/tqdm/py-make/issues/11)
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

docker-cleanup:
	docker stop idmtools_workers idmtools_postgres idmtools_redis
	docker rm idmtools_workers idmtools_postgres idmtools_redis

docker: ## Build our docker image using the local pypi without versioning from artifactory
	# This job is most useful when actively developing changes to the local_platform internals(tasks, api, cli) or
	# upstream changes that effect those areas(models and core). Otherwise, installing from latest in the nightly
	# should suffice for development
	# ensure pypi local is up
	cd ../idmtools_core && $(MAKE) dist
	$(MAKE) dist
	cd ../idmtools_platform_local && python build_docker_image.py

docker-proper: ## This job gets version data from artifactory. Should be used for production releases
	cd ../idmtools_core && $(MAKE) dist
	$(MAKE) dist
	$(PY) build_docker_image.py --proper

docker-only: ## Assumes you have made the local package already
	cd ../idmtools_core && $(MAKE) dist
	cd ../idmtools_platform_local && python build_docker_image.py

docker-only-proper: ## Assumes you have made the local package already without versioning from artifactory
	cd ../idmtools_core && $(MAKE) dist
	$(PY) build_docker_image.py --proper


# Release related rules
dist: build-ui clean ## build our package
	$(PY) setup.py sdist

start-webui: ## start the webserver
	cd idmtools_webui && yarn
	cd idmtools_webui && yarn start

ui-yarn-upgrade:
	@+$(IPY) "import os; os.chdir('idmtools_webui'); os.system('python build.py upgrade')"

build-ui: ## build ui
	$(CLDIR) --directories "idmtools_platform_local/internals/ui/static,idmtools_webui/build"
	cd webui && python build.py
	@$(IPY) "import shutil; shutil.copytree('idmtools_webui/build', 'idmtools_platform_local/internals/ui/static')"

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
