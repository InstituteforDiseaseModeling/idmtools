<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->



<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#Build docker image
1. Login to staging artifactory with idmod email and password

   `docker login idm-docker-staging.packages.idmod.org`
2. Build image in local

   Run build_docker_image.py in command line:

   `python build_docker_image.py --username username@idmod.org --password password`

3. Publish docker image to idm staging docker artifactory
  
   Run this docker command in command line: (need to replace version number)

   `docker push idm-docker-staging.packages.idmod.org/hongminc/rocky_mpi_docker/dtk_run_rocky_py39:1.0.0`

    Note, step 3 will automatically increase version by 1 based on VERSION file.
4. Update VERSION file to the latest
5. download docker to sif file:
   singularity pull --docker-login docker://idm-docker-staging.packages.idmod.org/idmtools/rocky_mpi_docker/dtk_run_rocky_py39:1.0.0 

