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
pymake setup-dev
pip install PyComps==2.3.5b3 --index-url=https://idm_bamboo_user@idmod.org:${bamboo.PasswordEArtifactory}@packages.idmod.org/api/pypi/pypi-staging/simple --no-cache-dir --force-reinstall

echo "pip list..."
pip list

echo "auto login..."
python dev_scripts/create_auth_token_args.py --comps_url "$1" --username "$2" --password "$3"
#python dev_scripts/create_auth_token_args.py --comps_url "https://comps2.idmod.org" --username "shchen" --password "Password123"

echo "run all tests..."

pymake test-all

echo "deactivate..."
deactivate

