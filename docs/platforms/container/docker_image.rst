ContainerPlatform Docker image
==============================

This document provides an overview of the Docker image build process.

**Note**: This document is primarily for developers. It is not necessary for users to build and push the Docker image. However, if you wish to use your own Docker image, please follow the instructions below at :ref:`extend-the-docker-image`.

Docker image overview
----------------------

The Docker image for `ContainerPlatform` is designed to provide a local running Docker container environment with all necessary tools and dependencies installed. The image is based on Rocky Linux 9.2 and includes the following tools:

- Python 3.9
- mipch 4.1.1
- emod-api 1.33.3
- Dependencies like numpy, pandas, scipy, matplotlib, etc.

Prerequisites
-------------
- Docker

Building the Docker image
-------------------------

Note: In general you do not need to run following commands. The image is automatically built in GitHub Actions and pushed to the `IDMOD Artifactory <https://packages.idmod.org/>`_.

To build the Docker image locally, run:

.. code-block:: bash

   python build_docker_image.py --username <username> --password <password>


where `<username>` and `<password>` refer to your IDMOD Artifactory account credentials, which are the same as IDMOD email and password.

Additionally, you can build the image with a different Dockerfile and image name by specifying the `--dockerfile` and `--image_name` arguments:

.. code-block:: bash

   python build_docker_image.py --username <username> --password <password> --dockerfile Dockerfile_buildenv --image_name container-rocky-buildenv


This will build the image with the name idm-docker-staging.packages.idmod.org/idmtools/container-rocky-buildenv:x.x.x.

Docker image versioning
-----------------------

The Docker image version is determined by the version in the IDM Docker-staging Artifactory. The version number advances by 0.0.1 for each new build.

By default, you do not build and push Docker image to IDM Artifactory. The image is automatically built in GitHub Actions and pushed to the IDM Artifactory. The image is used in the ContainerPlatform object. For example:

.. code-block:: bash

   from idmtools_platform_container import Platform
   platform = Platform('CONTAINER', job_directory='any_dir', docker_image='idm-docker-public.packages.idmod.org/idmtools/container-rocky-runtime:x.x.x')


where docker_image can be your locally built image or the image in the IDM Artifactory. If you do not provide a docker_image, the default image will be used.

Publishing the Docker image
---------------------------

Note: You do not need to push the Docker image to the Artifactory. The image is automatically built in GitHub Actions and pushed to the IDM Artifactory.  If you want to push the image to the Artifactory, run:

.. code-block:: bash

   python push_docker_image.py --username <username> --password <password>

where <username> and <password> are the username and password for the IDM Artifactory account.

.. _extend-the-docker-image:

Extend the Docker image
-----------------------
If you want to build your own Docker image, please use our ``container-rocky-runtime`` as your baseline image and add the following line to the top of your Dockerfile:

.. code-block:: bash

   FROM docker-production-public/idmtools/container-rocky-runtime:0.0.3

You can use general Docker build `command <https://docs.docker.com/reference/cli/docker/buildx/build/>`_ to build your own Docker image.
Then use that image in the Platform object. For example:

.. code-block:: bash

   from idmtools_platform_container import Platform
   platform = Platform('CONTAINER', job_directory='any_dir', docker_image='your_own_image_name:x.x.x')

