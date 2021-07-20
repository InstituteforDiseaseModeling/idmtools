PACKAGE_NAME=idmtools_platform_local
BASE_PIP_URL="packages.idmod.org/api/pypi/idm-pypi-"
STAGING_PIP_URL?="https://$(BASE_PIP_URL)staging/simple"
PRODUCTION_PIP_URL?="https://$(BASE_PIP_URL)production/simple"

include $(abspath ../dev_scripts/package_general.mk)


help: 
	help-from-makefile -f ../dev_scripts/package_general.mk -f ./Makefile


clean: ## Clean most of the temp-data from the project
	$(MAKE) -C tests clean
	$(MAKE) -C idmtools_webui clean
	-$(RM) -rf *.pyc *.pyo *.done *.log .coverage dist build **/__pycache__

clean-all: clean docker-cleanup ## Deleting package info hides plugins so we only want to do that for packaging
	$(CLDIR) --dir-patterns "**/*.egg-info/"
	$(MAKE) -C idmtools_webui clean-all

# Release related rules
dist: clean ## build our package
	$(MAKE) -C idmtools_webui build-ui
	$(PY) setup.py sdist

docker-cleanup: # Removes docker containers
	-docker stop idmtools_workers idmtools_postgres idmtools_redis
	-docker rm idmtools_workers idmtools_postgres idmtools_redis

# This job is most useful when actively developing changes to the local_platform internals(tasks, api, cli) or
# upstream changes that effect those areas(models and core). Otherwise, installing from latest in the nightly
# should suffice for development
# ensure pypi local is up
docker: ## Build our docker image using the local pypi without versioning from artifactory
	$(MAKE) -C ../idmtools_core dist
	$(MAKE) dist
	python build_docker_image.py

docker-proper: ## This job gets version data from artifactory. Should be used for production releases
	$(MAKE) -C ../idmtools_core dist
	$(MAKE) dist
	$(PY) build_docker_image.py --proper

docker-only: ## Assumes you have made the local package already
	$(MAKE) -C ../idmtools_core dist
	python build_docker_image.py

docker-only-proper: ## Assumes you have made the local package already without versioning from artifactory
	$(MAKE) -C ../idmtools_core dist
	$(PY) build_docker_image.py --proper




