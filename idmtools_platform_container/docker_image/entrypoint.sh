#!/bin/bash

# Create user if it doesn't exist
if ! id appuser &>/dev/null; then
    echo "Creating user for UID: $(id -u)"
    groupadd -g $(id -g) appuser
    useradd -u $(id -u) -g $(id -g) -m appuser
fi

exec "$@"
