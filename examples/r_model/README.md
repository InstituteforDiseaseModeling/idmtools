# Running example

This is a sample R model that currently runs in the LocalPlatform. The script automatically build the docker image for 
the user. If you would like to test the image outside of the script, you need to first run
```bash
docker-compose build
```

# Notes
   
The local platform allows us to run models through docker images. This makes it perfectly suited to running R models. 
There are a few rules you must follow when building your docker image:

1. They need a regular user with IDs 1000:1000 and no overlap from your running user. Windows users should not need to 
worry about this but to be compatible with execution on linux system you need to ensure this is true
1. Your docker image and script should be executable through docker run as a non-root user. For example, in this model 
we can test this by creating a test config.json and model.R in a directory and then running
    ```
    docker run -v /path/to/config/dir:/data -w /data -u "$(id -u):$(id -g)" idm-docker-staging.idmod.org/idmtools_r_model_example Rscript model.R --config-file config.json
    ```
    On Windows you would run
    ```
    docker run -v C:\path\to\config:/data -w /data -u "1000:1000" idm-docker-staging.idmod.org/idmtools_r_model_example Rscript model.R --config-file config.json
    ```
1. This image also uses s6 for testing scenarios. A note when using s6 that you need to create your own entrypoint that
skips s6 if the user is not root.