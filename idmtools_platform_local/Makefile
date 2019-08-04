.PHONY: clean lint test coverage release-local dist release-staging release-staging-minor-commit release-staging-minor
IPY=python -c

clean: ## Clean all our jobs
	@+$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.py[co]', recursive=True)]"
	@+$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.log', recursive=True)]"
	@+$(IPY) "import os, glob; [os.remove(i) for i in glob.glob('**/*.coverage', recursive=True)]"
	@+$(IPY) "import os, shutil, glob; [shutil.rmtree(i) for i in [k for k in glob.glob('**/*.egg-info/', recursive=True) if os.path.isdir(k)]]"
	@+$(IPY) "import shutil; shutil.rmtree('**/htmlcov', True)"
	@+$(IPY) "import shutil; shutil.rmtree('**/.pytest_cache', True)"
	@+$(IPY) "import shutil; shutil.rmtree('**/dist', True)"

# Dev and test related rules

lint: ## check style with flake8
	@+$(IPY) "import os; os.chdir('..'); os.system('flake8 --ignore=E501 idmtools_platform_local')"

test: ## Run our tests
	@+$(IPY) "import os; os.environ['SQLALCHEMY_DATABASE_URI']='sqlite://'; \
		os.environ['UNIT_TESTS']='1'; \
		os.environ['DATA_PATH'] = os.path.join(os.getcwd(), 'test_data'); \
		os.chdir('tests'); os.system('py.test -p no:warnings')"

test-docker: ## Run our  docker tests as well
	@+$(IPY) "import os; os.environ['DOCKER_TESTS'] = '1'; os.chdir('tests'); os.system('py.test -p no:warnings')"


docker-cleanup:
	docker stop  idmtools_workers idmtools_postgres idmtools_redis
	docker rm  idmtools_workers idmtools_postgres idmtools_redis

docker-local: ## Build our docker image using the local pypi
	# This job is most useful when actively developing changes to the local_platform internals(tasks, api, cli) or
	# upstream changes that effect those areas(models and core). Otherwise, installing from latest in the nightly
	# should suffice for development
	# ensure pypi local is up
	@+$(IPY) "import os; os.chdir('../dev_scripts/local_pypi'); os.system('docker-compose up -d')"
	@+$(IPY) "import os; os.chdir('../'); os.system('pymake release-local')"

	docker-compose build --build-arg PYPIURL=http://172.17.0.1:7171/ --build-arg PYPIHOST=172.17.0.1 workers

docker-staging: ## Build our docker image using staging pypi
	@+$(IPY) "import os; os.environ['REGISTRY'] = 'idm-docker-staging.packages.idmod.org'; \
		os.system(f'docker-compose build --build-arg PYPIURL=https://packages.idmod.org/api/pypi/pypi-staging/simple workers')"

docker-release-staging:
	@make docker-staging
	docker-compose push workers

coverage: ## Generate a code-coverage report
	@make clean
	# We have to run in our tests folder to use the proper config
	@+$(IPY) "import os; os.chdir('tests'); os.system('coverage run --source ../idmtools_platform_local -m pytest')"
	# move our stuff back to the top
	@+$(IPY) "import shutil as s; s.move('tests/.coverage','.coverage')"
	coverage report -m
	coverage html -i
	python ../dev_scripts/launch_dir_in_browser.py htmlcov/index.html

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
	bump2version --config-file .bumpversion.nightly.cfg build --allow-dirty
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*
	@make docker-release-staging

# Use before release-staging-minor-commit to confirm next version.
release-staging-minor-dry-run: ## perform a release to staging and bump the minor version.
	bump2version minor --dy-run --allow-dirty

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-minor-commit: ## perform a release to staging and commit the version.
	bump2version minor --commit
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*
	@make docker-release-staging
