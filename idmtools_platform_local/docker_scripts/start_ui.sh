#!/usr/bin/with-contenv sh

# This script launches our Local Runner UI

export FLASK_APP=idmtools_platform_local.workers.ui.app:application
exec s6-setuidgid idmtools /usr/local/bin/flask run --host=0.0.0.0

echo "IDM Tools Local UI available at http://localhost:5000"