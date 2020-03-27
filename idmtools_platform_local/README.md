<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [IDM Tools Local Runner](#idm-tools-local-runner)
  - [Module Organization](#module-organization)
- [Running the Local Runner](#running-the-local-runner)
- [Using the UI](#using-the-ui)
- [Using the local website](#using-the-local-website)
- [Development Tips](#development-tips)
  - [Understanding the components](#understanding-the-components)
  - [Debugging the workers](#debugging-the-workers)
    - [Debug configuration](#debug-configuration)
      - [Script Path](#script-path)
      - [Script Arguments](#script-arguments)
        - [Script Environment](#script-environment)
  - [Troubleshooting Tests](#troubleshooting-tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# IDM Tools Local Runner

The IDM Tool Local Runner allows execution of tasks in a local docker container and provides a platform that is
somewhat similar to COMPS, though much more limited

## Module Organization

    ├── ./docker_scripts          <- Script for use inside of docker container only. Mainly S6 service/user scripts
    ├── idmtools_platform_local   <- Base of the module contents
    │   ├── cli                   <- Contains the CLI interface for the idmtools_local.
    │   ├── client                <- API Client
    │   ├── infrastructure        <- Docker service related items
    │   ├── internals             <- Server related components
    │   │   ├── data              <- Data definition for idmtool_local
    │   │   ├── tasks             <- Our Queue Worker Tasks
    │   │   ├── ui                <- Web UI for idmtool_local
    │   │   └── workers           <- Dramatiq worker config and utils
    ├── docker-compose.yml        <- Docker-compose file for the local service
    ├── Dockerfile                <- Dockfile for both Development and Production
    ├── requirements.txt          <- Python requirements for fopr the idmtools_local_runner. This ONLY specifies client requirements
    ├── setup.py                  <- Python setup file with dependencies
    └── README.md                 <- The top-level README for developers using this project.

# Running the Local Runner

The local runner will start on it's own using when you select it as the platform. For example, from your code you can
 do the following with this example idmtools.ini file
 ```ini
[Local_Staging]
type = Local
 ```
 In your code, you could then get then use as would any other platform
```python
from idmtools.core.platform_factory import Platform
from idmtools.managers.experiment_manager import ExperimentManager

platform = Platform('Local')
...
em = ExperimentManager(experiment=experiment, platform=platform)
em.run()
em.wait_till_done()

```

You can manage the Local platform using cli commands
* `idmtools local down`    - Shutdown the local platform. You can also add the `--delete-data` flag to delete the local data as well
* `idmtools local restart` - Restart the local platform
* `idmtools local start`   - Start the local platform
* `idmtools local status`  - Check local platform status

The workers service contains the IDMTools workers that actually execut the tasks as well as containing a simplistic UI
running at http://localhost:5000

# Using the UI

The Web UI is available at http://localhost:5000/data. Currently it only supports displaying the data directories from
experiments. It is best used in conjunction with the CLI status commands

# Using the local website


To use the website, please use the following steps:

1. Run `idmtools local start` to start the local platfrom  
2. Run `pymake start-webui` to start the webserver
3. If a browser has not started, please open a browser and visit "http://localhost:3000" to see the website

Note: the above steps may change after the website is included as part of docker container

# Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run Unit tests
test-all    -   Run all tests including integration and docker test
docker-cleanup - Manually cleanup
docker-local - Build docker image using local pypi server for packaging

coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`

## Understanding the components

Local platform is built from two fundamental high-level areas, client-server. You can see from the project layout above 
that all server code is located under internals and client code is at the top-level of the package.

The client side code has two main areas of concern. The first is allocation and orchestration of the Local Platform 
services. This is done mostly through the infrastructure module. The second concern is communication with the API 
service which is done through the client module. 

Within the server, there are two distinct areas. The first area is dramatiq related workers. Dramatiq workers are 
mostly defined by the tasks, workers, and also data folder from the internals module. The second area is UI which is 
under the UI module of internals. UI also uses the internals data module.

Within a running instance of a local platform container the works between the two areas is divided into 3 or 4 processes 
depending on GPU availability. On the worker side we have
- Provisioning workers
- CPU Workers
- GPU workers if docker support nvidia containers

These workers all use the same code but have different runtime parameters defined in the run scripts within
 `idmtools_platform_local/docker_scripts/services`

The UI is the other portion. In a running container, it is ran using the usgi manager with nginx.

Including in this are two additional containers
* Redis
* Postgres

The local platform manages these containers for the end user.

## Debugging the workers

Currently, workers can only run on Linux. To debug from windows you will need to debug through a docker container. 
Sometimes logging can be just as effective as debugging in this situations.

To debug the workers you have to consider a few things first. First, the debug configuration will depend on which 
tasks you wish to debug. You will need to gather all the queues of the target task and any tasks sooner in the 
workflow. For example, RunTask is only triggered usually after CreateExperiment and CreateSimulation tasks.


### Debug configuration
Before debugging you will need to ensure the redis and postgres containers are running. You can do this by running 
`idmtools local start` and then `docker stop idmtools_workers`

You will then want to run with the following options

#### Script Path
path to dramatiq. This should be in the bin directory of your virtual env. On Windows, you have to debug 
through the docker and therefore will find dramatiq in /usr/local/bin

#### Script Arguments 
```
--verbose --processes 1 --threads 1 idmtools_platform_local.internals.workers.run_broker:redis_broker idmtools_platform_local.internals.workers.run --queues cpu --threads 1
```
    
If you need to debug more than one queue, use additional `--queues` options

##### Script Environment
You will most likely need the following environment variables. Change accordingly
* `DATA_PATH=/home/clinton/development/work/idmtools/idmtools_local_runner/test_data`
* `SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://idmtools:idmtools@localhost:5432/idmtools`
* `SQLALCHEMY_ECHO=1`
    
## Troubleshooting Tests

* By setting the environment variable `NO_TEST_WORKER_CLEANUP=1`, worker cleanup will be disabled on test. This is 
useful when a specific script/job is failing and you want to troubleshoot the output of the task(StdOut.txt)
* You can attempt to run simple jobs like python simulations by following these steps.
  1. Grab the command from the idmtools_workers logs
  ```
  [2019-11-12 07:22:19,253] [PID 341] [Thread-5] [idmtools_platform_local.internals.tasks.general_task] [INFO] Executing python ./Assets/model1.py config.json from working directory /data/8ZQTUTAC/T8PBPPHP
  ```
  1. With a running set of the local platform(if it is not running use `idmtools local start`) run the command
      ```bash
     docker exec -it idmtools_workers bash
     ```
  1. From within the bash shell run
     ```bash
     su - idmtools
     ```
  1. cd to the working directory. In this case, `/data/8ZQTUTAC/T8PBPPHP`
  1. Run the command
     ```
     python ./Assets/model1.py config.json
     ```
* The Local platform requires you to be able to run docker without needing sudo access. You can test this by running
`docker ps` and see if the command succeeds for you. Usually when you do not have access to docker as the current user
then you will receive errors like 

 ```bash
 Creating tar archive
removing 'idmtools-0.2.0+nightly' (and everything under it)
twine upload --verbose --repository-url http://localhost:7171 -u admin -p admin dist/*
Uploading distributions to http://localhost:7171
Uploading idmtools-0.2.0+nightly.tar.gz
 0%|                                                                                     | 0.00/48.4k [00:00<?, ?B/s]
Traceback (most recent call last):
 File "/software/anaconda3/lib/python3.7/site-packages/urllib3/connection.py", line 159, in _new_conn
   (self._dns_host, self.port), self.timeout, **extra_kw)
 File "/software/anaconda3/lib/python3.7/site-packages/urllib3/util/connection.py", line 80, in create_connection
   raise err
 File "/software/anaconda3/lib/python3.7/site-packages/urllib3/util/connection.py", line 70, in create_connection
   sock.connect(sa)
ConnectionRefusedError: [Errno 111] Connection refused
 ```
  