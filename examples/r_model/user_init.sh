#!/usr/bin/env bash
if (( EUID == 0 )); then
    echo "Running s6 init scripts"
    /init &
    sleep 1
    echo Running $@
    su idmtools -c '$@'
else
    echo "Skipping s6"
     $@
fi
