.PHONY: help clean clean-all docker docker-release-staging
IPY=python -c
PY?=python
PDS=$(PY) ../../dev_scripts/
PDR=$(PDS)run.py

help:
	$(PDS)get_help_from_makefile.py

clean-all: clean ## Deleting package info hides plugins so we only want to do that for packaging
	$(CLDIR) --dir-patterns "**/*.egg-info/"
	docker rmi idmtools_comps_ssmt_worker

docker: ## Build our docker image using the local pypi
	$(PDR) -w '../../idmtools_core' -ex 'pymake dist'
	$(PDR) -w '../../idmtools_models' -ex 'pymake dist'
	$(PDR) -w '../../idmtools_platform_comps' -ex 'pymake dist'
	python build_docker_image.py

docker-release-staging: docker
	python push_docker_image.py
