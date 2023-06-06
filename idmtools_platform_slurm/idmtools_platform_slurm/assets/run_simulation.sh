#!/usr/bin/env bash

SIMULATION_INDEX=$((${SLURM_ARRAY_TASK_ID} + $1))
JOB_DIRECTORY=$(find . -type d -maxdepth 1 -mindepth 1  | grep -v Assets | head -$SIMULATION_INDEX | tail -1)
cd $JOB_DIRECTORY
bash _run.sh 1> stdout.txt 2> stderr.txt