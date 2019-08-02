IPY=python -c

.PHONY:
	package_all_to_local
	ensure-twine
	start_local_pypi
	build-local_pypy
	package_all_to_local
	publish_to_local
	publish_to_local_cli
	publish_to_local_core
	publish_to_local_models_collections
	publish_to_local_platform_comps
	publish_to_platform_local
	publish_to_platform_test


start_local_pypi: package_all_to_local ## Start our local pypi server

package_all_to_local: build-local_pypy publish_to_local
	echo " Ready to package"

ensure-twine:
	pip install twine

build-local_pypy:
	cd dev_scripts/local_pypi && docker-compose up -d

publish_to_local: ensure-twine publish_to_local_cli publish_to_local_core publish_to_local_models_collections publish_to_local_platform_comps publish_to_platform_local publish_to_platform_test


publish_to_local_cli:
	cd idmtools_cli && twine upload --repository-url http://localhost:7171

publish_to_local_core:
	cd idmtools_core && twine upload --repository-url http://localhost:7171

publish_to_local_models_collection:
	cd idmtool_models_collection&& twine upload --repository-url http://localhost:7171


publish_to_local_platform_comps:
	cd idmtools_platform_comps && twine upload --repository-url http://localhost:7171

publish_to_platform_local:
	cd idmtools_platform_local && twine upload --repository-url http://localhost:7171

publish_to_platform_test:
	cd idmtools_test && twine upload --repository-url http://localhost:7171




