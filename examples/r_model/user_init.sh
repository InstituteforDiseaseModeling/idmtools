#!/usr/bin/env bash
if (( EUID == 0 )); then
    echo "Runing s6 init scripts"
    /init &
    su idmtools
else
    echo "Skipping s6"
     $@
fi