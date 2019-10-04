To use the slurm docker test platform, you need to follow these steps

1. Within this directory, run docker-compose up -d
2. Wait one minute are check the docker logs. Once the slurmctld is ready, then go to the next step
3. Run register_cluster.sh . On windows, you can run the docker-compose exec commands
4. Grab the IP Address of slurmctld
   `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' slurmctld`
5. Update the remote_host to the ip address from previous output in idmtools_platform_slurm/tests/idmtools.ini
6. Update the key_file path in idmtools_platform_slurm/tests/idmtools.ini to point to the absolute path of the 
   idmtools_platform_slurm/dockerized_slurm/id_rsa on your machine