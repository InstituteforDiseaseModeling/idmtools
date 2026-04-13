![Staging: idmtools-platform-comps](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-comps/badge.svg?branch=dev)

# idmtools-platform-comps

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

  - [Installing](#installing)
- [Development Tips](#development-tips)
- [Building SSMT Docker Image Locally](#building-ssmt-docker-image-locally)
- [Choose SSMT Docker Image to use in test/script](#choose-ssmt-docker-image-to-use-in-testscript)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-platform-comps
```

# Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`

# Building SSMT Docker Image Locally

To build the SSMT Docker image, follow these steps

1. ```bash
   docker login ghcr.io -u username -p password
   ```
2. ```bash
   make ssmt-image-docker-build
   ```

# Choose SSMT Docker Image to use in test/script

There are three ways to choose which ssmt docker image to use in your script:

1. specify docker_image in SSMTWorkItem creation, for example,
```bash
   wi = SSMTWorkItem(name=wi_name, command=command, docker_image='my_test_ssmt_docker_image')
```   
2. define docker_image in your idmtools.ini, for example:
```bash
    [COMPS]
    type = COMPS
    endpoint = https://comps.idmod.org
    environment = Calculon
    ......
    docker_image = my_test_ssmt_docker_image
```
