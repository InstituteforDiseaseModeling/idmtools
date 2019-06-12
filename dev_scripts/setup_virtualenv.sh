#!/usr/bin/env bash


LOCAL_PATH="$(realpath $(dirname '$0')/../)"
echo ${LOCAL_PATH}
cd ${LOCAL_PATH}/idmtools_core && \
    pip install -e . --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
cd ${LOCAL_PATH}/idmtools_local_runner && \
    pip install -e .
cd ${LOCAL_PATH}/idmtools_models_collection && \
    pip install -e .