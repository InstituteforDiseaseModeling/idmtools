PACKAGE_NAME=idmtools_platform_comps
include $(abspath ../dev_scripts/package_general.mk)


help: 
	$(PDS)get_help_from_makefile.py -f ../dev_scripts/package_general.mk -f ./Makefile

# Release related rules
ssmt-image: ## Build SSMT Docker image
	$(MAKE) -C ssmt_image docker

ssmt-image-release: ## Push image to staging
	$(MAKE) -C ssmt_image  docker-release-staging
