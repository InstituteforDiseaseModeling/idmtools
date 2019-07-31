#!/usr/bin/env bash


LOCAL_PATH="$(realpath $(dirname '$0')/../)"
echo ${LOCAL_PATH}


packages=( "idmtools_core" "idmtools_platform_local" "idmtools_platform_comps" "idmtools_models_collection" "idmtools_test" )
for i in "${packages[@]}"
do
echo "Installing local ${i}"
cd ${LOCAL_PATH}/${i} && \
    pip install -e .[test] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
done