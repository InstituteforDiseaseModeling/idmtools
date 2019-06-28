#IDM Tools Local Runner

The IDM Tool Local Runner allows execution of tasks in a local docker container and provides a platform that is
somewhat similar to COMPS, though much more limited

## Module Organization

    ├── ./docker_scripts          <- Script for use inside of docker container only. Mainly S6 service/user scripts
    ├── idmtools_local            <- Base of the module contents
    │   ├── cli                   <- Contains the CLI interface for the idmtools_local.
    │   ├── data                  <- Data definition for idmtool_local
    │   ├── tasks                 <- The various tasks processing methods
    │   ├── ui                    <- Web UI for idmtool_local
    ├── docker-compose.yml        <- Docker-compose file for the local service
    ├── Dockerfile                <- Dockfile for both Development and Production
    ├── requirements.txt          <- Python requirements for fopr the idmtools_local_runner
    ├── setup.py                  <- Python setup file with dependencies
    └── README.md                 <- The top-level README for developers using this project.

# Running the Local Runner

Generally you can do a 
`docker-compose up -d`

This will bring up 3 services
- postgres
- redis
- workers

The workers service contains the IDMTools workers that actually execut the tasks as well as containing a simplistic UI
running at http://localhost:5000


# Using the CLI

The CLI requires the workers service to already be running. From the idmtools_local_runner directory run
`docker-compose exec workers python -m idmtools_local.cli.run`

## Experiment commands

### Status

You can check the status of experiments use the follow command. It will also summarize the simulations under
the experiment as a progress bar with green section for completed tasks, yellow for in progress, red for failed, and
white for queued. 

`docker-compose exec workers python -m idmtools_local.cli.run experiment status`

Alternatively, you can run from anywhere using
`docker-compose exec -t workers python -m idmtools_local.cli.run experiment status` 

In addition, we used in conjunction with a console that supports auto-highlighting of hyperlinks, you will be able to
easily open up the asset directories by clicking on the data path URLs.

You can also perform filtering on the experiments
`docker-compose exec workers python -m idmtools_local.cli.run experiment status --tag type PythonExperiment`

`docker-compose exec workers python -m idmtools_local.cli.run experiment status --id 8EHU147Z`

### Delete

You can delete experiments and their child simulations using the following command. Optionally you can also delete
the associated data directories as well by using the *--data* option.

`docker-compose exec workers python -m idmtools_local.cli.run experiment delete <experiment_id>`

## Simulation Commands

## Status 

You can check the status of simulations use the follow command.

`docker-compose exec workers python -m idmtools_local.cli.run simulation status`

You can also filter by a either id, experiment id, status, and tags or any combination of the aforementioned

`docker-compose exec workers python -m idmtools_local.cli.run simulation status --experiment-id EFX6JXBV`

`docker-compose exec workers python -m idmtools_local.cli.run simulation status --id XDT0VMVV`

`docker-compose exec workers python -m idmtools_local.cli.run simulation status --status failed`

`docker-compose exec workers python -m idmtools_local.cli.run simulation status --tag a 5 --tag b`

`docker-compose exec workers python -m idmtools_local.cli.run simulation status --experiment-id --status failed`


# Using the UI

The Web UI is available at http://localhost:5000. Currently it only supports displaying the data directories from
experiments. It is best used in conjunction with the CLI status commands