#!/bin/bash
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python2.7
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