#!/bin/bash
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python2.7
# stop any existing setup as it nneds to be redone from within container
docker stop idmtools_workers idmtools_redis idmtools_postgres || true
docker rm idmtools_workers idmtools_redis idmtools_postgres || true
# setup our idmtools virtualenv
mkvirtualenv -p /usr/local/bin/python3.7 idmtools
pip install py-make
cd /idmtools
# clean in case our host is windows and there are already built files
make clean-all
# install in the local environment
python3 dev_scripts/bootstrap.py
# docker within docker causes issues with localhost so we should
# default clients to gateway
export REDIS_HOST=$(sudo route -n | awk '$4 == "UG" {print $2}')
export API_HOST=$REDIS_HOST
# docker in docker requires us to mount via volume name so the directory can be mounted by items
export IDMTOOLS_WORKERS_DATA_MOUNT_BY_VOLUMENAME=linux-test-env_idmtools_local_workers
export IDMTOOLS_REDIS_DATA_MOUNT_BY_VOLUMENAME=linux-test-env_idmtools_local_redis
# Because the directories for local data are mapped as directories we want to shallow delete our data(only data within
# container and not the whole directory)
export SHALLOW_DELETE=1