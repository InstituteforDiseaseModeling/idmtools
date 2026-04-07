PACKAGE_NAME=idmtools_platform_comps
include $(abspath ../dev_scripts/package_general.mk)


help: 
	help-from-makefile -f ../dev_scripts/package_general.mk -f ./Makefile

# Release related rules
ssmt-image: ## Build SSMT Docker image  --deprecated
	$(MAKE) -C ssmt_image docker

ssmt-image-release: ## Push image to staging  --deprecated
	$(MAKE) -C ssmt_image  docker-release-staging

ssmt-image-docker-build:  ## Build ssmt docker image
	$(MAKE) -C ssmt_image  docker-build

ssmt-image-release-new: ## Build and publish ssmt docker image to github container registry
	$(MAKE) -C ssmt_image  docker-build-publish