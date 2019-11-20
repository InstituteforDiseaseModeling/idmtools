.PHONY: clean lint test coverage release-local dist release-staging release-staging-release-commit release-staging-minor
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
TEST_COMMAND=py.test --durations=10 -v --junitxml=test_results.xml
TEST_RUN_OPTS=-e DOCKER_REPO=idm-docker-staging NO_SPINNER=1
FULL_TEST_CMD=$(PDR) -w 'tests' $(TEST_RUN_OPTS) -ex '$(TEST_COMMAND)
COVERAGE_CMD=$(PDR) -w 'tests' $(TEST_RUN_OPTS) -p . ../ -ex 'coverage run --omit="*/test*,*/setup.py" --source ../,../../idmtools_core,../../idmtools_models,../../idmtools_model_emod -m pytest

help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build,idmtools_webui/build"

clean-all:  ## Deleting package info hides plugins so we only want to do that for packaging
	@make clean
	$(CLDIR) --dir-patterns "**/*.egg-info/"

# Dev and test related rules
lint: ## check style with flake8
	$(PDR) -w '..' -ex 'flake8 --ignore=E501 $(PACKAGE_NAME)'

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

test-emod: ## Run our emod tests
	$(FULL_TEST_CMD) -m "emod"'

test-python: ## Run our python tests
	$(FULL_TEST_CMD) -m "python"'

coverage: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	$(COVERAGE_CMD) -m "not comps and not docker"'
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"
	coverage report -m
	coverage html -i
	$(PDS)/launch_dir_in_browser.py htmlcov/index.html

coverage-all: ## Generate a code-coverage report
	# We have to run in our tests folder to use the proper config
	$(COVERAGE_CMD)
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"
	coverage report -m
	coverage html -i
	$(PDS)/launch_dir_in_browser.py htmlcov/index.html

docker-cleanup:
	docker stop  idmtools_workers idmtools_postgres idmtools_redis
	docker rm  idmtools_workers idmtools_postgres idmtools_redis

docker-local: ## Build our docker image using the local pypi
	# This job is most useful when actively developing changes to the local_platform internals(tasks, api, cli) or
	# upstream changes that effect those areas(models and core). Otherwise, installing from latest in the nightly
	# should suffice for development
	# ensure pypi local is up
	$(PDR) -w '../dev_scripts/local_pypi' -ex 'docker-compose up -d'
	$(PDR) -w '../idmtools_core' -ex 'pymake release-local'
	@pymake release-local
	docker-compose build --build-arg PYPIURL=http://172.17.0.1:7171/ --build-arg PYPIHOST=172.17.0.1 workers

docker-local-no-cache:## Build our docker image using the local pypi
	# This job is most useful when actively developing changes to the local_platform internals(tasks, api, cli) or
	# upstream changes that effect those areas(models and core). Otherwise, installing from latest in the nightly
	# should suffice for development
	# ensure pypi local is up
	$(PDR) -w '../dev_scripts/local_pypi' -ex 'docker-compose up -d'
	$(PDR) -w '../idmtools_core' -ex 'pymake release-local'
	@pymake release-local
	docker-compose build --no-cache --build-arg PYPIURL=http://172.17.0.1:7171/ --build-arg PYPIHOST=172.17.0.1 workers

docker-staging: ## Build our docker image using staging pypi
	$(PDR) -w '../dev_scripts/local_pypi' -ex 'docker-compose up -d'
	# rebuild local package at moment since we install local platform package from there
	docker-compose build --build-arg PYPIURL=$(STAGING_PIP_URL) workers

docker-release-staging:
	@make docker-staging
	docker-compose push workers

# Release related rules

release-local: ## package and upload a release to http://localhost:7171
	@pymake dist
	twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*

dist: ## build our package
	@make build-ui
	@make clean
	python setup.py sdist

release-staging: ## perform a release to staging
	bump2version build --allow-dirty
	@pymake dist
	twine upload --verbose --repository-url $(STAGING_PIP_URL) dist/*
	@make docker-release-staging

# Use before release-staging-release-commit to confirm next version.
release-staging-release-dry-run: ## perform a release to staging and bump the minor version.
	bump2version release --dry-run --allow-dirty --verbose

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-release-commit: ## perform a release to staging and commit the version.
	bump2version release --commit
	@make dist
	twine upload --verbose --repository-url $(STAGING_PIP_URL) dist/*
	@make docker-release-staging

start-webui: ## start the webserver
	$(PDR) -w 'idmtools_webui' -ex yarn
	$(PDR) -w 'idmtools_webui' -ex 'yarn start'

build-ui: ## build ui
	$(CLDIR) --directories "idmtools_platform_local/internals/ui/static,idmtools_webui/build"
	@+$(IPY) "import os; os.chdir('idmtools_webui'); os.system('python build.py')"
	@$(IPY) "import shutil; shutil.copytree('idmtools_webui/build', 'idmtools_platform_local/internals/ui/static')"

bump-patch: ## bump the patch version
	bump2version patch --commit