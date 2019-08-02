IPY=python -c

.PHONY:
	all
	package-production

build-docker: package_all_to_local ## Build our docker-image
	docker-compose build

package_all_to_local:
	cd ../ && pymake package_all_to_local