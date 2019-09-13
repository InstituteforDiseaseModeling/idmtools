# IDM Tools Local Runner

The IDM Tool Local Runner allows execution of tasks in a local docker container and provides a platform that is
somewhat similar to COMPS, though much more limited

## Module Organization

    ├── ./docker_scripts          <- Script for use inside of docker container only. Mainly S6 service/user scripts
    ├── idmtools_platform_local   <- Base of the module contents
    │   ├── cli                   <- Contains the CLI interface for the idmtools_local.
    │   ├── data                  <- Data definition for idmtool_local
    │   ├── tasks                 <- The various tasks processing methods
    │   ├── ui                    <- Web UI for idmtool_local
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
