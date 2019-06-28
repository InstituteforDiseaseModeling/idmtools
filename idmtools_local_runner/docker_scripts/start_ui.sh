#!/usr/bin/with-contenv sh

# This script launches our Local Runner UI

export FLASK_APP=idmtools_local.ui.app:application
exec /usr/local/bin/flask run --host=0.0.0.0

echo "IDM Tools Local UI available at http://localhost:5000"