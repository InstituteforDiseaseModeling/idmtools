ContainerPlatform Docker Image
==============================

This document provides an overview of the Docker image build process.

Docker Image Overview
----------------------

The Docker image for `ContainerPlatform` is designed to facilitate the platform by providing a local running environment with all necessary tools and dependencies installed. The image is based on Rocky Linux 9.2 and includes the following tools:

- Python 3.9
- mipch 4.1.1
- emod-api 1.33.3
- Dependencies like numpy, pandas, scipy, matplotlib, etc.

Prerequisites
-------------
- Docker

Building the Docker Image
-------------------------

Note: You do not need to build the image locally. The image is automatically built in GitHub Actions and pushed to the IDMOD Artifactory.

To build the Docker image locally, run:

.. code-block:: bash

   python build_docker_image.py --username <username> --password <password>


where <username> and <password> are the username and password for the IDMOD Artifactory account.  You can also build the image with a different Dockerfile and image name by specifying the --dockerfile and --imagename arguments:

.. code-block:: bash

   python build_docker_image.py --username <username> --password <password> --dockerfile Dockerfile_buildenv --imagename container-rocky-buildenv


This will build the image with the name idm-docker-staging.packages.idmod.org/idmtools/container-rocky-buildenv:x.x.x.

Docker Image Versioning
-----------------------

The Docker image version is determined by the version in the IDM Docker-staging Artifactory. The version number advances by 0.0.1 for each new build.
Docker Image Usage
By default, you do not need to worry about building and using the Docker image. The image is automatically built in GitHub Actions and pushed to the IDM Artifactory. The image is used in the ContainerPlatform object. For example:

.. code-block:: bash

   from idmtools_platform_container import Platform
   platform = Platform('CONTAINER', docker_image='idm-docker-public.packages.idmod.org/idmtools/container-rocky-runtime:x.x.x')


where docker_image can be your locally built image or the image in the IDM Artifactory. If you do not provide a docker_image, the default image will be used.

Publishing the Docker Image
---------------------------

Note: You do not need to push the Docker image to the Artifactory. The image is automatically built in GitHub Actions and pushed to the IDM Artifactory.  If you want to push the image to the Artifactory, run:

.. code-block:: bash

   python push_docker_image.py --username <username> --password <password>

where <username> and <password> are the username and password for the IDM Artifactory account.
