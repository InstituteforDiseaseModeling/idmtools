.PHONY: clean lint test coverage release-local dist release-staging release-staging-minor-commit release-staging-minor

clean: ## Clean all our jobs
	python dev_scripts/run_pymake_on_all.py clean

setup-dev:  ## Setup packages in dev mode
	python dev_scripts/setup_dev_env.py

lint: ## check style with flake8
	python dev_scripts/run_pymake_on_all.py lint

test: ## Run our tests
    python dev_scripts/run_pymake_on_all.py test

coverage: ## Generate a code-coverage report
	python dev_scripts/run_pymake_on_all.py coverage

release-local: ## package and upload a release to http://localhost:7171
	@make dist
	twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*

dist: ## build our package
	python dev_scripts/run_pymake_on_all.py dist

release-staging: ## perform a release to staging
	python dev_scripts/run_pymake_on_all.py release-staging

# Use before release-staging-minor-commit to confirm next version.
release-staging-minor-dry-run: ## perform a release to staging and bump the minor version.
	python dev_scripts/run_pymake_on_all.py release-staging-dry-run

# This should be used when a pushing a "production" build to staging before being approved by test
release-staging-minor-commit: ## perform a release to staging and commit the version.
	python dev_scripts/run_pymake_on_all.py release-staging-minor-commit
