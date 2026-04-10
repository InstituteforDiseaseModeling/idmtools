<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [idmtools_platform_container Docker image](#idmtools_platform_container-docker-image)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Build Docker image](#build-docker-image)
  - [Docker image versioning](#docker-image-versioning)
  - [Docker image usage](#docker-image-usage)
  - [Publish Docker image](#publish-docker-image)
  - [Extend the Docker image](#extend-the-docker-image)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# idmtools_platform_container Docker image

**Note**: This document is primarily for developers. It is not necessary for users to build and push the Docker image. However, if you wish to use your own Docker image, please follow the instructions in the [Extend the Docker Image](#extend-the-docker-image).

## Introduction
This Docker image is designed to facilitate idmtools_platform_container. It serves as a local running platform with all necessary tools and dependencies installed. The image is based on Rocky Linux 9.2 and includes the following:- python 3.9
- mipch 4.1.1
- emod-api 1.33.3
- emod-api's dependencies like numpy, pandas, scipy, matplotlib etc.

## Prerequisites
- Docker
  On Windows or Mac, please use Docker Desktop 2.1.0.5 or 2.2.0.1

## Build Docker image
Note, You do not need to build the image locally. The image is automatically built via GitHub Actions and pushed to the IDM GitHub Container Registry. 

To build Docker image locally, run:
```bash
python build_container_image.py --username <username> --token <github_token> --production
```
where `<username>` and `<token>` are your credentials for the GitHub Container Registry (ghcr.io) with read permission.

You can also build the image with a different Dockerfile and image name by specifying the `--dockerfile` and `--image_name` arguments.
```bash
python build_container_image.py --username <username> --token <token> --dockerfile Dockerfile_buildenv --image_name container-rocky-buildenv
```
This will build an image named 'ghcr.io/institutefordiseasemodeling/idmtools-comps-ssmt-worker:x.x.x.x'

## Docker image versioning
The Docker image version is determined by the version in the IDM GitHub Container Registry. The version number advances by 0.0.1 for each new build. https://github.com/InstituteforDiseaseModeling/idmtools/pkgs/container/idmtools-comps-ssmt-worker. 

## Docker image usage
By default, you do not need to worry about building the image or how to use it. The image is automatically built via GitHub Actions and pushed to the IDM GitHub Container Registry. The image is used by the idmtools_platform_container Platform object
```python
from idmtools.core.platform_factory import Platform
platform = Platform('CONTAINER', job_directory='any_dir', docker_image='ghcr.io/institutefordiseasemodeling/idmtools-comps-ssmt-worker::x.x.x.x')
```
The docker_image parameter can be your locally built image or an image from the IDM GHCR. If you do not provide docker_image, the default image will be used.

## Publish Docker image
Note, you do not need to push docker image to GHCR. The image is auto built in github action and pushed to IDM GHCR.
If you want to push the image to artifactory, run:
```bash
python build_container_image.py --username <username> --token <github_token> --production --push
```

## Extend the Docker image
If you want to build you own Docker image, please use our ``container-rocky-runtime`` as your baseline image and add the following line to the top of your Dockerfile:

```bash
   FROM ghcr.io/institutefordiseasemodeling/idmtools-comps-ssmt-worker/0.0.3
```
You can use general Docker build [command](https://docs.docker.com/reference/cli/docker/buildx/build/) to build your own Docker image.
Then use that image in the Platform object. For example:

```bash
   from idmtools_platform_container import Platform
   platform = Platform('CONTAINER', job_directory='any_dir', docker_image='your_own_image_name:x.x.x')
```