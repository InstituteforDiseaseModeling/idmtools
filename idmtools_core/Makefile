.PHONY: clean lint test coverage release-local dist release-staging release-staging-release-commit release-staging-minor
IPY=python -c

clean: ## Clean all our jobs
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.py[co]', recursive=True)]"
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.done', recursive=True)]"
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('*.log', recursive=True)]"
	@$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/.coverage', recursive=True)]"
	@$(IPY) "import os, glob, shutil; [shutil.rmtree(i, True) for i in glob.glob('**/__pycache__', recursive=True)]"
	@$(IPY) "import os, glob, shutil; [shutil.rmtree(i, True) for i in glob.glob('**/htmlcov', recursive=True)]"
	@$(IPY) "import os, glob, shutil; [shutil.rmtree(i) for i in glob.glob('**/.pytest_cache', recursive=True)]"
	@$(IPY) "import shutil; shutil.rmtree('dist', True)"
	@$(IPY) "import shutil; shutil.rmtree('build', True)"

clean-all:  ## Deleting package info hides plugins so we only want to do that for packaging
	@make clean
	@+$(IPY) "import os, shutil, glob; [shutil.rmtree(i) for i in [k for k in glob.glob('**/*.egg-info/', recursive=True) if os.path.isdir(k)]]"
# Dev and test related rules

lint: ## check style with flake8
	@+$(IPY) "import os; os.chdir('..'); os.system('flake8 --ignore=E501 idmtools_core')"

test: ## Run our tests
	@+$(IPY) "import os; os.chdir('tests'); \
	os.environ['DOCKER_REPO'] = 'idm-docker-staging'; \
	os.system('py.test -p no:warnings -m \"not comps and not docker\" --durations=3 --junitxml=test_results.xml')"

test-no-comps: ## Run our tests
	@+$(IPY) "import os; os.chdir('tests'); \
	os.environ['DOCKER_REPO'] = 'idm-docker-staging'; \
	os.system('py.test -v -p no:warnings -m \"not comps\" --durations=3 --junitxml=test_results.xml')"

test-all: ## Run our  docker tests as well
	@+$(IPY) "import os; os.chdir('tests'); \
	os.environ['DOCKER_REPO'] = 'idm-docker-staging'; os.environ['NO_SPINNER'] = '1' ;\
	os.system('py.test -v --durations=3 -p no:warnings --junitxml=test_results.xml')"

coverage: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	@+$(IPY) "import os; os.chdir('tests'); os.system('coverage run --source ../idmtools -m pytest')"
	# move our stuff back to the top
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"
	coverage report -m
	coverage html -i
	python ../dev_scripts/launch_dir_in_browser.py htmlcov/index.html

coverage-all: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	@+$(IPY) "os.chdir('tests'); os.environ['DOCKER_REPO'] = 'idm-docker-staging'; \
	os.system('coverage run -p no:warnings --source ../idmtools -m pytest -m \"not comps and not docker\" ')"
	# move our stuff back to the top
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"

watch: ## Automate running of tests and linting of this project using watchdog. Useful for development
	watchmedo tricks-from dev.yml

# Release related rules

release-local: ## package and upload a release to http://localhost:7171
	@make dist
	twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*

dist: ## build our package
	@make clean
	python setup.py sdist

release-staging: ## perform a release to staging
	bump2version build --allow-dirty
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/idm-pypi-staging/ dist/*

# Use before release-staging-release-commit to confirm next version.
release-staging-release-dry-run: ## perform a release to staging and bump the minor version.
	bump2version release --dry-run --allow-dirty --verbose

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-release-commit: ## perform a release to staging and commit the version.
	bump2version release --commit
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/idm-pypi-staging/ dist/*

bump-patch:
	bump2version patch --commit