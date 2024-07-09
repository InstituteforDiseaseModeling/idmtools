============
Docker Image
============

This Docker image is designed to facilitate idmtools_platform_container. It serves as local running platform with all
necessary tools and dependencies installed. The image is based on rockylinux 9.2 and includes the following tools:

python 3.9
mipch 4.1.1
emod-api 1.33.3
emod-api's dependencies like numpy, pandas, scipy, matplotlib etc.

Prerequisites
=============
* Docker
* Build Docker Image

Note, you do not need to build the image locally. The image is auto built in github action and pushed to idmod artifactory.

Build Docker Image
==================
To build Docker image locally, run following script:

::

    python Run build_docker_image.py --username <username> --password <password>

where <username> and <password> are the username and password for the idmod artifactory account.

You can also build the image with different docker file and image name --dockerfile and --image_name arguments.

Docker Image Versioning
=======================
The Docker image version is determined by the version in idm docker-staging artifactory. It will advance the version number by 0.0.1 for each new build.

Docker Image Usage
==================
By default, you DO NOT need to worry about the image build and where to call image. The image is auto built in github action whenever there is new pull request with any changes to Dockerfile or idmtools_platform_container package. The image is called in idmtools_platform_container Platform object. For example,

.. code-block:: python

    from idmtools_platform_container import Platform
    platform = Platform('CONTAINER', docker_image='idm-docker-public.packages.idmod.org/idmtools/container-rocky-runtime:x.x.x')

where docker_image can be your local built image or the image in idmod artifactory. If you do not provide docker_image, the default image will be used.

Publish Docker Image
====================
Note, you do not need to push docker image to artifactory. The image is auto built in github action and pushed to idmod artifactory. If you want to push the local built image to artifactory, run:

::

    python push_docker_image.py --username <username> --password <password>

where <username> and <password> are the username and password for the idmod artifactory account.
