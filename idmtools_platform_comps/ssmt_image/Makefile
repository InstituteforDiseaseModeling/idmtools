.PHONY: help clean clean-all docker docker-release-staging
IPY=python -c
PY?=python
PDS=$(PY) ../../dev_scripts/
PDR=$(PDS)run.py

help:
	help-from-makefile -f ./Makefile

clean-all: clean ## Deleting package info hides plugins so we only want to do that for packaging
	$(CLDIR) --dir-patterns "**/*.egg-info/"
	docker rmi idmtools_comps_ssmt_worker

docker: ## Build our docker image using the local pypi
	$(MAKE) -C ../../idmtools_core dist
	$(MAKE) -C ../../idmtools_models dist
	$(MAKE) -C ../../idmtools_platform_comps dist
	python build_docker_image.py

docker-release-staging: docker
	python push_docker_image.py

docker-build: ## Build our docker image using the local pypi
	$(MAKE) -C ../../idmtools_core dist
	$(MAKE) -C ../../idmtools_models dist
	$(MAKE) -C ../../idmtools_platform_comps dist
	python build_ssmt_image.py --production

docker-build-publish: ## Build and publish  image using the local pypi
	$(MAKE) -C ../../idmtools_core dist
	$(MAKE) -C ../../idmtools_models dist
	$(MAKE) -C ../../idmtools_platform_comps dist
	python build_ssmt_image.py --production --push
