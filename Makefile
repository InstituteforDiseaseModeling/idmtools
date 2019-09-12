.PHONY: clean lint test coverage release-local dist release-staging release-staging-release-commit release-staging-minor


clean: ## Clean all our jobs
	python -c "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	python dev_scripts/run_pymake_on_all.py clean p

clean-all: ## Clean all our jobs
	python -c "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	python dev_scripts/run_pymake_on_all.py clean-all p

setup-dev:  ## Setup packages in dev mode
	python dev_scripts/bootstrap.py
	@python -c "import os; os.chdir('idmtools_platform_local'); os.system('pymake docker-local')"

lint: ## check style with flake8
	python dev_scripts/run_pymake_on_all.py lint p

test: ## Run our tests
	python dev_scripts/run_pymake_on_all.py test p

test-all: ## Run our tests. We cannot run in parallel
	python dev_scripts/run_pymake_on_all.py test-all

coverage: ## Generate a code-coverage report
	python dev_scripts/run_pymake_on_all.py coverage-all
	coverage combine idmtools_cli/.coverage idmtools_core/.coverage idmtools_model_dtk/.coverage idmtools_models/.coverage idmtools_platform_comps/.coverage idmtools_platform_local/.coverage
	coverage report -m
	coverage html -i
	python dev_scripts/launch_dir_in_browser.py htmlcov/index.html

release-local: ## package and upload a release to http://localhost:7171
	python dev_scripts/run_pymake_on_all.py release-local p

dist: ## build our package
	python dev_scripts/run_pymake_on_all.py dist p

release-staging: ## perform a release to staging
	@make clean-all
	python dev_scripts/run_pymake_on_all.py release-staging

# Use before release-staging-release-commit to confirm next version.
release-staging-release-dry-run: ## perform a release to staging and bump the minor version.
	python dev_scripts/run_pymake_on_all.py release-staging-release-dry-run

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-release-commit: ## perform a release to staging and commit the version.
	python dev_scripts/run_pymake_on_all.py release-staging-release-commit

start-webui: ## start the webserver
	python -c "import os; os.chdir(os.path.join('idmtools_platform_local', 'idmtools_webui')); os.system('yarn'); os.system('yarn start')"

bump-patch:
	python dev_scripts/run_pymake_on_all.py bump-patch