# Overview

This environment provides windows users(and linux users) with a test environment for Debian linux. This is useful to
test cross-platform compatibility issues in an easy to stand up manner. Because of some complication with a nested
dockerization configuration, this environment configures the Local platform differently from normal machines. The key
differences are the worker and redis data is stored in a docker volume. 

Here is a rough diagram of the difference
```
    ----------------------------------
    |                                 |
    |  Host                           |
    |                                 |
    |   worker_data  ----> [Worker]   |
    |   redis-data   ----> [Redis]    |
    -----------------------------------
```
[] Indicates the item is a container.

The linux test environment looks more like the follow
vs
```bash
    ----------------------------------
    |                                 |
    |  Host                           |
    |   [Liunxtstenv]                 |
    |   |                             |
    |   [worker_data]  ----> [Worker] |
    |   [redis-data]   ----> [Redis]  |
    -----------------------------------
```
You can see that the Linux tst env is linked to the worker_data and redis_data like the worker and redis containers. 
Also you can see instead of being a "real" directory that it is a containerized filesystem. This is what allows us to use a nested environment like this no matter the host system.

# Setup

1. Before use, be sure you have ran 
   `make setup-dev`
    This is required to create the worker containers used by tasks internally

2. Then build using
   `docker-compose build`
3. Then run, `docker-compose run linuxtst` from this directory.
4. When in the environment, buefore running test-all you most likely will need to do the following
   - docker login idm-docker-staging.packages.idmod.org
   - python dev_scripts/create_auth_token_args.py

## Tips

You most likely will want to clear your data in your test environment. You can do that by running 
`docker-compose down -v`. This is useful when permissions have been corrupted which should only happen in the case of 
a code bug.

You should always run build to ensure you have gotten any updates. 

In addition, the idmtools has password-less sudo access so you can install any needed packages.
Remember to run `sudo apt update` first. For example, you may want to edit files directly in the container and need nano
so you could run `sudo apt install nano`


# TODO
Support docker builds within container. We need to detect the gateway address
