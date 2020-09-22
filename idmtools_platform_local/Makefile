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
TEST_RUN_OPTS=-e DOCKER_REPO=idm-docker-staging NO_SPINNER=1
TEST_EXTRA_OPTS?=
TEST_COMMAND := py.test --durations=3 -v --junitxml=test_results.xml --html=local.test_results.html $(TEST_EXTRA_OPTS)
TEST_RUN_OPTS = -e DOCKER_REPO=docker-staging NO_SPINNER=1
FULL_TEST_CMD := $(PDR) -w 'tests' $(TEST_RUN_OPTS) -ex '$(TEST_COMMAND)
COVERAGE_CMD := $(PDR) -w 'tests' $(TEST_RUN_OPTS) -p . ../ -ex 'coverage run --omit="*/test*,*/setup.py" --source ../,../../idmtools_core,../../idmtools_models -m pytest $(COVERAGE_CMD_OPTS)'
COVERAGE_CMD_OPTS?=
help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build,idmtools_webui/build"

clean-all:  ## Deleting package info hides plugins so we only want to do that for packaging
	@make clean
	$(CLDIR) --dir-patterns "**/*.egg-info/"
	@+$(IPY) "import os; os.chdir('idmtools_webui'); os.system('python build.py clean')"

dev:
	echo $(CWD)

# Dev and test related rules
lint: ## check style with flake8
	$(PDR) -w '..' -ex 'flake8 --ignore=E501,W291 $(PACKAGE_NAME)'

test: ## Run our tests
	$(FULL_TEST_CMD) -m "not comps and not docker"'

test-all: ## Run all our tests
	$(FULL_TEST_CMD)'

test-failed: ## Run only previously failed tests
	$(FULL_TEST_CMD) --lf'

test-long: ## Run any tests that takes more than 30s
	$(FULL_TEST_CMD) -m "long"'

test-no-long: ## Run any tests that takes less than 30s
	$(FULL_TEST_CMD) -m "not long"'

test-comps: ## Run our comps tests
	$(FULL_TEST_CMD) -m "comps"'

test-docker: ## Run our docker tests
	$(FULL_TEST_CMD) -m "docker"'

test-python: ## Run our python tests
	$(FULL_TEST_CMD) -m "python"'

test-smoke: ## Run our smoke tests
	$(FULL_TEST_CMD) -m "smoke"'

coverage-report:  ## Generate HTML report from coverage. Requires running coverage run first(coverage, coverage-smoke, coverage-all)
	coverage report -m
	coverage html -i

## View coverage report (Comment out https://github.com/tqdm/py-make/issues/11)
coverage-report-view: coverage-report
	$(PDS)/launch_dir_in_browser.py htmlcov/index.html

coverage: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	$(COVERAGE_CMD) -m "not comps and not docker"'
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"

coverage-smoke: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	$(COVERAGE_CMD) -m "smoke"'
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"

coverage-all: ## Generate a code-coverage report using all tests
	# We have to run in our tests folder to use the proper config
	$(COVERAGE_CMD)'
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"

docker-cleanup:
	docker stop idmtools_workers idmtools_postgres idmtools_redis
	docker rm idmtools_workers idmtools_postgres idmtools_redis

docker: ## Build our docker image using the local pypi without versioning from artifactory
	# This job is most useful when actively developing changes to the local_platform internals(tasks, api, cli) or
	# upstream changes that effect those areas(models and core). Otherwise, installing from latest in the nightly
	# should suffice for development
	# ensure pypi local is up
	$(PDR) -w '../idmtools_core' -ex 'pymake dist'
	@pymake dist
	$(PDR) -w '../idmtools_platform_local' -ex 'python build_docker_image.py'

docker-proper: ## This job gets version data from artifactory. Should be used for production releases
	$(PDR) -w '../idmtools_core' -ex 'pymake dist'
	@pymake dist
	$(PY) build_docker_image.py --proper

docker-only: ## Assumes you have made the local package already
	$(PDR) -w '../idmtools_core' -ex 'pymake dist'
	$(PDR) -w '../idmtools_platform_local' -ex 'python build_docker_image.py'

docker-only-proper: ## Assumes you have made the local package already without versioning from artifactory
	$(PDR) -w '../idmtools_core' -ex 'pymake dist'
	$(PY) build_docker_image.py --proper


# Release related rules
dist: ## build our package
	@make build-ui
	@make clean
	$(PY) setup.py sdist

start-webui: ## start the webserver
	$(PDR) -w 'idmtools_webui' -ex yarn
	$(PDR) -w 'idmtools_webui' -ex 'yarn start'

ui-yarn-upgrade:
	@+$(IPY) "import os; os.chdir('idmtools_webui'); os.system('python build.py upgrade')"

build-ui: ## build ui
	$(CLDIR) --directories "idmtools_platform_local/internals/ui/static,idmtools_webui/build"
	@+$(IPY) "import os; os.chdir('idmtools_webui'); os.system('python build.py')"
	@$(IPY) "import shutil; shutil.copytree('idmtools_webui/build', 'idmtools_platform_local/internals/ui/static')"

release-staging: ## perform a release to staging
	@make dist
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
