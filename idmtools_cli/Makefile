.PHONY: clean clean-test clean-pyc clean-build docs help release-local test lint
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

dev-install: ## install the cli in dev mode with test packages
	pip install -e .[test,packaging]

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 --ignore=E501 idmtools_cli tests

test: ## run tests quickly with the default Python
	PYTHONPATH=${PWD}:${PYTHONPATH} \
	UNIT_TESTS=1 py.test

coverage: ## check code coverage quickly with the default Python
	PYTHONPATH=${PWD}:${PYTHONPATH} \
	coverage run --source idmtools_cli -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

release-local: dist ## package and upload a release to http://localhost:7171
	twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*


dist: clean ## builds source and wheel package
	python setup.py sdist