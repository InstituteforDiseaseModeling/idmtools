![Staging: idmtools-platform-comps](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-platform-comps/badge.svg?branch=dev)

# idmtools-platform-comps

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Installing](#installing)
- [Development Tips](#development-tips)
- [Building SSMT Docker Image](#building-ssmt-docker-image)
- [Choose SSMT Docker Image to use in test/script](#choose-ssmt-docker-image-to-use-in-testscript)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-platform-comps --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
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

# Building SSMT Docker Image

To build the SSMT Docker image, follow these steps

1. ```bash
   docker login docker-production.packages.idmod.org
   ```
2. ```bash
   make ssmt-image
   ```
3. When prompted, enter your idm username and password

# Choose SSMT Docker Image to use in test/script

There are three ways to choose which ssmt docker image to use in your script:

1. specify docker_image in SSMTWorkItem creation, for example,
```bash
   wi = SSMTWorkItem(name=wi_name, command=command, docker_image='my_test_ssmt_docker_image')
```   
2. define docker_image in your idmtools.ini, for example:
```bash
    [COMPS2]
    type = COMPS
    endpoint = https://comps.idmod.org
    environment = Calculon
    ......
    docker_image = my_test_ssmt_docker_image
```

3. if not above two cases, idomtools system will determine the default ssmt docker image from platform for you:

   if endpoint = https://comps.idmod.org, it will use production docker image
   
   for all other cases, it will use the staging docker image
   
Note: if user overrode docker image in wi (case #1) and also defined docker image in idmtools.ini (case #2), 
      it will take #1 as higher priority