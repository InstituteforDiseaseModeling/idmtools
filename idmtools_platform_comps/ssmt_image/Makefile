.PHONY: clean lint test coverage dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c
BASE_PIP_URL="packages.idmod.org/api/pypi/idm-pypi-"
STAGING_PIP_URL?="https://$(BASE_PIP_URL)staging/simple"
PRODUCTION_PIP_URL?="https://$(BASE_PIP_URL)production/simple"
PY?=python
PDS=$(PY) ../../dev_scripts/
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py
CWD=$($(IPY) "import os; print(os.getcwd())")
TEST_COMMAND=py.test --durations=10 -v --junitxml=test_results.xml
TEST_RUN_OPTS=-e DOCKER_REPO=idm-docker-staging NO_SPINNER=1
FULL_TEST_CMD=$(PDR) -w 'tests' $(TEST_RUN_OPTS) -ex '$(TEST_COMMAND)
COVERAGE_CMD=$(PDR) -w 'tests' $(TEST_RUN_OPTS) -p . ../ -ex 'coverage run --omit="*/test*,*/setup.py" --source ../,../../idmtools_core,../../idmtools_models -m pytest
DOCKER_VERSION=$($(IPY) "print(")
help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean most of the temp-data from the project
	$(CLDIR) --file-patterns "*.py[co],*.done,*.log,**/.coverage" \
		--dir-patterns "**/__pycache__,**/htmlcov,**/.pytest_cache" --directories "dist,build,idmtools_webui/build"

clean-all:  ## Deleting package info hides plugins so we only want to do that for packaging
	@make clean
	$(CLDIR) --dir-patterns "**/*.egg-info/"
	docker rmi idmtools_comps_ssmt_worker

docker: ## Build our docker image using the local pypi
	# ensure our packages are built
	$(PDR) -w '../../idmtools_core' -ex 'pymake dist'
	$(PDR) -w '../../idmtools_models' -ex 'pymake dist'
	$(PDR) -w '../../idmtools_platform_comps' -ex 'pymake dist'
	python build_docker_image.py

docker-release-staging:
	@make docker
	python push_docker_image.py
