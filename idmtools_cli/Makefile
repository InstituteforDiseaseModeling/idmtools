.PHONY:
    clean
    lint
    test
    coverage
    release-local
    dist


clean: ## Clean all our jobs
	@+python -c "import os, glob; [os.remove(i) for i in glob.glob('*.py[co]', recursive=True)]"
	@+python -c "import os, glob; [os.remove(i) for i in glob.glob('*.done', recursive=True)]"
	@+python -c "import os, glob; [os.remove(i) for i in glob.glob('*.log', recursive=True)]"
	@+python -c "import os, glob; [os.remove(i) for i in glob.glob('*.coverage', recursive=True)]"
	@+python -c "import os, shutil, glob; [shutil.rmtree(i) for i in [k for k in glob.glob('*.egg-info/', recursive=True) if os.path.isdir(k)]]"
	@+python -c "import shutil; shutil.rmtree('htmlcov', True)"
	@+python -c "import shutil; shutil.rmtree('.pytest_cache', True)"
	@+python -c "import shutil; shutil.rmtree('dist', True)"


lint: ## check style with flake8
	flake8 --ignore=E501 idmtools_cli tests

test: ## Run our tests
	@+python -c "import os, sys; sys.path.append(os.getcwd()); os.system('py.test')"

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
	python setup.py sdist

release-staging: ## perform a release to staging
	bump2version --config-file .bumpversion.nightly.cfg build --allow-dirty
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*


release-staging-minor: ## perform a release to staging
	bump2version minor --allow-dirty
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*

release-staging-minor-commit: ## perform a release to staging and commit the version. This should be used when a pushing a "production" build to staging before being approved by test
	bump2version minor --commit
	@make dist
	twine upload --verbose --repository-url https://packages.idmod.org/api/pypi/pypi-staging/simple dist/*