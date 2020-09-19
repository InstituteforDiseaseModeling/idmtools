.PHONY: clean lint test coverage dist release-staging release-staging-release-commit release-staging-minor changelog

IPY=python -c
PY=python
PDS=$(PY) dev_scripts/
MAKEALL=$(PDS)run_pymake_on_all.py
PDR=$(PDS)run.py
CLDIR=$(PDS)clean_dir.py

help:
	$(PDS)get_help_from_makefile.py

clean: ## Clean all our jobs
	$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	$(MAKEALL) --parallel clean
	$(CLDIR) --file-patterns "**/*.log"
	$(PDR) -wd "docs" -ex "make clean"

clean-all: ## Clean all our jobs
	$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	$(MAKEALL) --parallel clean-all
	$(CLDIR) --file-patterns "**/*.buildlog"

setup-dev: ## Setup packages in dev mode
	python dev_scripts/bootstrap.py
	$(PDR) -w idmtools_platform_local -ex 'pymake docker'

setup-dev-no-docker: ## Setup packages in dev mode minus docker
	python dev_scripts/bootstrap.py

lint: ## check style with flake8
	flake8 --ignore=E501,W291 --exclude="venv**/**,examples/**,workflow/**,docs/**,*/tests/**,idmtools_test/**, idmtools_platform_comps/prototypes/**"


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

test-python: ## Run our python tests
	$(MAKEALL) test-python

test-smoke: ## Run our smoke tests
	$(MAKEALL) test-smoke

coverage: ## Generate a code-coverage report
	$(MAKEALL) coverage-all
	coverage combine idmtools_cli/.coverage idmtools_core/.coverage idmtools_models/.coverage idmtools_platform_comps/.coverage idmtools_platform_local/.coverage
	coverage report -m
	coverage html -i
	$(PDS)launch_dir_in_browser.py htmlcov/index.html

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


changelog: ## Generate partial changelog
	$(PDS)changelog.py

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

build-docs: ## build docs(only works on linux at moment due to make.bat not running by default)
	$(PDR) -wd 'docs' -ex 'make html'

build-docs-server: build-docs ## builds docs and launch a webserver
	$(PDS)serve_docs.py

dev-watch: ## Run lint on any python code changes
	$(PDS)run_commands_and_wait.py --command 'watchmedo shell-command --drop --wait --interval 10 --patterns="*.py" --ignore-pattern="*/tests/.test_platform/*" --recursive --command="pymake lint"' \
        --command 'watchmedo shell-command --patterns="*.py" --ignore-pattern="*/tests/.test_platform/*" --drop --interval 10 --recursive --command="pymake test-smoke";;;idmtools_core' \
        --command 'watchmedo shell-command --patterns="*.py" --ignore-pattern="*/tests/.test_platform/*" --drop --interval 10 --recursive --command="pymake test-smoke";;;idmtools_models' \
        --command 'watchmedo shell-command --patterns="*.py" --ignore-pattern="*/tests/.test_platform/*" --drop --interval 10 --recursive --command="pymake test-smoke";;;idmtools_platform_comps' \
        --command 'watchmedo shell-command --patterns="*.py" --ignore-pattern="*/tests/.test_platform/*" --drop --interval 10 --recursive --command="pymake test-smoke";;;idmtools_platform_local' \
        --command 'watchmedo shell-command --patterns="*.py" --ignore-pattern="*/tests/.test_platform/*" --drop --interval 10 --recursive --command="pymake test-smoke";;;idmtools_cli'

generate-stubs: ## Generate pything interfaces. Useful to identify what the next version should be by comparing to previous runs
	$(PDS)make_stub_files.py  -c dev_scripts/stub.cfg
	$(PDS)process_interfaces.py