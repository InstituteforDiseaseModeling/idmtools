#!/usr/bin/env bash
if (( EUID == 0 )); then
    echo "Runing s6 init scripts"
    /init &
    sleep 1
    su idmtools -c "$@"
else
    echo "Skipping s6"
     $@
fi