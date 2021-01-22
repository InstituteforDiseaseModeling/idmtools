PACKAGE_NAME=idmtools_core
include $(abspath ../dev_scripts/package_general.mk)

help: 
	$(PDS)get_help_from_makefile.py -f ../dev_scripts/package_general.mk -f ./Makefile

update-dependent-libraries: ## update any libraries in repo that depend on core
	$(PDS)update_core_version.py
