#!/bin/bash

# ------------------------------------------------------------------ #
# Cluster run script
# This script pulls the public Docker container for Covasim and
# then runs the simulation script.
# ------------------------------------------------------------------ #

# ---------- #
# Variables
# ---------- #

# URI for the image (URI formats: https://sylabs.io/guides/3.5/user-guide/cli/singularity_pull.html)
uri='docker://idmod/covasim'

# image file name after downloading
image='covasim.sif'

# Get the appropriate mount path(s) for current environment (e.g., /mnt/idm)
mounts="$(/bin/ls -dm /mnt/* | sed "s/, /,/g")"

# ---------- #
# Script
# ---------- #

# List the variables for the job
echo -e '# Environment Variables\n'
( set -o posix ; set )
echo

# create outputs directory
mkdir outputs

# Pull the container from Docker Hub
singularity pull $image $uri

# Use the image to run sim.py
singularity exec -B "$mounts" $image python3 ./Assets/sim.py
