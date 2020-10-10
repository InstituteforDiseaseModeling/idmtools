#!/usr/bin/env bash

VIRTUALENV_DIR="$(mktemp -d)"
echo "env" $VIRTUALENV_DIR
trap 'rm -r "${VIRTUALENV_DIR}"' EXIT
virtualenv -p python3.6 "${VIRTUALENV_DIR}"
source "${VIRTUALENV_DIR}/bin/activate"

echo "install idmtools ..."
LOCAL_PATH="$(realpath $(dirname '$0')/)"
echo ${LOCAL_PATH}
pip install py-make
make setup-dev

echo "pip list..."
pip list

echo "auto login..."
python dev_scripts/create_auth_token_args.py --comps_url "$1" --username "$2" --password "$3"
#python dev_scripts/create_auth_token_args.py --comps_url "https://comps2.idmod.org" --username "shchen" --password "Password123"

echo "run all tests..."

make test-all

echo "deactivate..."
deactivate

