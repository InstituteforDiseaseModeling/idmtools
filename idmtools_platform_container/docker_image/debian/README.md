<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [idmtools_platform_container Docker Image](#idmtools_platform_container-docker-image)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Build Docker Image locally](#build-docker-image-locally)
  - [Use docker image in idmtools](#use-docker-image-in-idmtools)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Debian12 Docker Image

## Introduction
This Docker image is designed to facilitate idmtools_platform_container. It serves as local running platform with all necessary tools and dependencies installed. 

The image built from this Dockerfile is based on debian:12 docker image and includes the following packages and utilities:
- python 3.11
- mipch 4.0.2
- emod-api 2.0.1

## Prerequisites
- Docker

## Build Docker Image locally
```bash
docker build -t debian12-env:0.0.1 .
```

## Use docker image in idmtools
```python
from idmtools.core.platform_factory import Platform
platform = Platform('CONTAINER', docker_image='debian12-env:0.0.1')
```
Note, here `debian12-env:0.0.1` is the image name you built in the previous step. 

If your script needs extra python packages, you can install with extra_packages argument in Platform at runtime:
```python
from idmtools.core.platform_factory import Platform
platform = Platform('CONTAINER', docker_image='debian12-env', extra_packages=['emodpy~=2.0.0', 'pytest'])

# or use idmtools cli command to install before run script: idmtools container install <package>
```
