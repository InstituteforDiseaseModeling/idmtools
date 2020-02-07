#!/usr/bin/env bash
# This script is meant to be ran when initializing the container

# Check if we are running as root
# If so, run the init script
if (( EUID == 0 )); then
    echo "Running s6 init scripts"
    /init &
    sleep 1
    echo Running $@
    su idmtools -c '$@'
# Run the command directly
else
    echo "Skipping s6"
     $@
fi
