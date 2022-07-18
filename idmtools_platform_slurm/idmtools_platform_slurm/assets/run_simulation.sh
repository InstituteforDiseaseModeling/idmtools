#!/usr/bin/env bash

JOB_DIRECTORY=$(find . -type d -maxdepth 1 -mindepth 1  | grep -v Assets | head -${SLURM_ARRAY_TASK_ID} | tail -1)
cd $JOB_DIRECTORY
bash _run.sh 1> stdout.txt 2> stderr.txt