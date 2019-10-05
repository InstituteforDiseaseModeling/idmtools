#!/bin/bash
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python2.7
mkvirtualenv -p /usr/local/bin/python3.7 idmtools
cd /idmtools
make clean-all
python3 dev_scripts/bootstrap.py