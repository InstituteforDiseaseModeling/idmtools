PACKAGE_NAME=idmtools_platform_container
include $(abspath ../dev_scripts/package_general.mk)

PARALLEL_TESTING = 1

help: 
	help-from-makefile -f ../dev_scripts/package_general.mk -f ./Makefile

# Release related rules
container-image: ## Build container Docker image
	$(MAKE) -C docker_image docker

container-image-release: ## Push image to staging
	$(MAKE) -C docker_image  docker-release-staging
