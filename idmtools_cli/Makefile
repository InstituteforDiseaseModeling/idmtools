.PHONY: clean lint test coverage release-local dist release-staging release-staging-minor-commit release-staging-minor
IPY=python -c

clean: ## Clean all our jobs
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.py[co]', recursive=True)]"
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.done', recursive=True)]"
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.log', recursive=True)]"
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.coverage', recursive=True)]"
	@$(IPY) "import os, shutil, glob; [shutil.rmtree(i) for i in [k for k in glob.glob('*.egg-info/', recursive=True) if os.path.isdir(k)]]"
	@$(IPY) "import shutil; shutil.rmtree('htmlcov', True)"
	@$(IPY) "import shutil; shutil.rmtree('.pytest_cache', True)"
	@$(IPY) "import shutil; shutil.rmtree('dist', True)"


lint: ## check style with flake8
	flake8 --ignore=E501 idmtools_cli tests

test: ## Run our tests
	@$(IPY) "import os, sys; sys.path.append(os.getcwd()); os.system('py.test')"

test-all: ## Run our  docker tests as well
	@+$(IPY) "import os; os.environ['DOCKER_TESTS'] = '1'; \
	os.environ['COMPS_TESTS'] = '1'; os.chdir('tests'); os.system('py.test -p no:warnings')"

coverage: ## Generate a code-coverage report
	coverage run --source idmtools_cli -m pytest
	coverage report -m
	coverage html
	python ../dev_scripts/launch_dir_in_browser.py htmlcov/index.html

release-local: ## package and upload a release to http://localhost:7171
	@make dist
	twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*

dist: ## build our package
	@make clean
	python setup.py sdist bdist

release-staging: ## perform a release to staging
	bump2version --config-file .bumpversion.nightly.cfg build --allow-dirty
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*

# Use before release-staging-minor-commit to confirm next version.
release-staging-minor-dry-run: ## perform a release to staging and bump the minor version.
	bump2version minor --dy-run --allow-dirty

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-minor-commit: ## perform a release to staging and commit the version.
	bump2version minor --commit
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*