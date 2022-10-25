PY?=python
PDS=$(PY) ../../dev_scripts/
IPY=python -c
PDR=$(PDS)run.py
RM?=rm

help:
	help-from-makefile -f ./Makefile

clean: ## Clean most of the temp-data from the project
	$(RM) -rf idmtools_webui/build

clean-all:
	python build.py clean

start-webui: ## start the webserver
	yarn
	yarn start

ui-yarn-upgrade: ## Upgrade UI
	python build.py upgrade

build-ui: clean ## build ui
	-$(RM) -rf ../idmtools_platform_local/internals/ui/static
	python build.py
	-echo "Copying Build"
	@$(IPY) "import shutil; shutil.copytree('build', '../idmtools_platform_local/internals/ui/static')"