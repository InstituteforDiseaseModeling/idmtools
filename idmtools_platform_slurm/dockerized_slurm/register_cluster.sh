#!/bin/bash
set -e

# https://github.com/giovtorres/docker-centos7-slurm/issues/3
# sacctmgr add cluster linux
#
#sacctmgr add account none,test Cluster=linux Description="none" Organization="none"
#
#sacctmgr add user da DefaultAccount=test

docker exec slurmctld bash -c "/usr/bin/sacctmgr --immediate add cluster name=linux" && \
docker exec slurmctld bash -c "/usr/bin/sacctmgr --immediate add account none,test Cluster=linux Description='none' Organization='none'" && \
docker exec slurmctld bash -c "/usr/bin/sacctmgr --immediate add user test DefaultAccount=test" && \
docker-compose restart slurmdbd slurmctld
ssh-copy-id -i id