#!/usr/bin/env bash
VIRTUALENV_DIR="$(mktemp -d)"
echo "env" $VIRTUALENV_DIR
trap 'rm -r "${VIRTUALENV_DIR}"' EXIT
virtualenv -p python3.7 "${VIRTUALENV_DIR}"
source "${VIRTUALENV_DIR}/bin/activate"
cd dev_scripts
./setup_virtualenv.sh
cd ..
cd idmtools_local_runner && \
	docker-compose up -d
cd ..
LOCAL_PATH="$(realpath $(dirname '$0')/)"
echo "auto login..."
cd ${LOCAL_PATH}/idmtools_core/tests && \
   python create_auth_token_args.py --comps_url "$1" --username "$2" --password "$3"
echo "run all tests..."
cd ${LOCAL_PATH}/idmtools_core/tests
python run_tests.py
echo "deactivate..."
deactivate


