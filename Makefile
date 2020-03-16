.PHONY: clean lint test coverage release-local dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c
PY=python
PDS=$(PY) dev_scripts/
MAKEALL=$(PDS)run_pymake_on_all.py
PDR=$(PDS)run.py

help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean all our jobs
	$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	$(MAKEALL) --parallel clean

clean-all: ## Clean all our jobs
	$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	$(MAKEALL) --parallel clean-all

setup-dev:  ## Setup packages in dev mode
	python dev_scripts/bootstrap.py
	$(PDR) -w idmtools_platform_local -ex 'pymake docker-local'

lint: ## check style with flake8
	$(MAKEALL) --parallel lint
	flake8 --ignore=E501,W291 examples

test: ## Run our tests
	$(MAKEALL) --parallel test

test-all: ## Run all our tests
	$(MAKEALL) test-all

test-failed: ## Run only previously failed tests
	$(MAKEALL) test-failed

test-no-long: ## Run any tests that takes less than 30s on average
	$(MAKEALL) test-no-long

test-comps: ## Run our comps tests
	$(MAKEALL) test-comps

test-docker: ## Run our docker tests
	$(MAKEALL) test-docker

test-emod: ## Run our emod tests
	$(MAKEALL) test-emod

test-python: ## Run our python tests
	$(MAKEALL) test-python

coverage: ## Generate a code-coverage report
	$(MAKEALL) coverage-all
	coverage combine idmtools_cli/.coverage idmtools_core/.coverage idmtools_model_emod/.coverage idmtools_models/.coverage idmtools_platform_comps/.coverage idmtools_platform_local/.coverage
	coverage report -m
	coverage html -i
	$(PDS)launch_dir_in_browser.py htmlcov/index.html

release-local: ## package and upload a release to http://localhost:7171
	$(MAKEALL) --parallel release-local

dist: ## build our package
	$(MAKEALL) --parallel dist

release-staging: ## perform a release to staging
	@make clean-all
	$(MAKEALL) release-staging


packages-changes-since-last-verison: ## Get list of versions since last release that have changes
	git diff --name-only $(shell git tag -l --sort=-v:refname | grep -w '[0-9]\.[0-9]\.[0-9]' | head -n 1) HEAD | grep idmtools | cut -d "/" -f 1  | sort | uniq | grep -v ini | grep -v examples | grep -v dev_scripts

linux-dev-env: ## Runs docker dev env
	$(PDR) -w 'dev_scripts/linux-test-env' -ex 'docker-compose build linuxtst'
	$(PDR) -w 'dev_scripts/linux-test-env' -ex 'docker-compose run --rm linuxtst'


draft-change-log:
	git log $(shell git tag -l --sort=-v:refname | grep -w '[0-9]\.[0-9]\.[0-9]' | head -n 1) HEAD --pretty=format:'%s' --reverse --simplify-merges | uniq

bump-release: #bump the release version.
	$(MAKEALL) bump-release

# Use before release-staging-release-commit to confirm next version.
bump-release-dry-run: ## perform a release to staging and bump the minor version.
	$(MAKEALL) bump-release-dry-run

bump-patch: ## bump the patch version
	$(MAKEALL) bump-patch

bump-minor: ## bump the minor version
	$(MAKEALL) bump-minor

bump-major: ## bump the major version
	$(MAKEALL) bump-major

bump-patch-dry-run: ## bump the patch version(dry run)
	$(MAKEALL) bump-patch-dry-run

bump-minor-dry-run: ## bump the minor version(dry run)
	$(MAKEALL) bump-minor-dry-run

bump-major-dry-run: ## bump the minor version(dry run)
	$(MAKEALL) bump-major-dry-run