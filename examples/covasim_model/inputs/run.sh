#!/bin/bash

# ------------------------------------------------------------------ #
# Cluster run script
# This script pull the public Docker container for Covasim
# ------------------------------------------------------------------ #

# Store the .sif container file name
image=covasim.sif

# Pull the container from Docker Hub
singularity pull $image docker://idmod/covasim

# Use the container to run sim.py
singularity exec -B /mnt/idm $image python3 ./Assets/sim.py
