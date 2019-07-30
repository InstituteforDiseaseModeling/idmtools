#!/usr/bin/env bash

read -p "Are you sure want to reset your environment?" -n 1 choice
echo  # Move to new line
if [[ "$choice" == [Yy]* ]]
then
    # Enable trace so users can see operations that we are executing
    set +o xtrace

    rm -rf ../data
    docker-compose down -v
    docker network rm idmtools_network || true
    docker-compose build --no-cache
    # reset trace
    set -o xtrace
fi