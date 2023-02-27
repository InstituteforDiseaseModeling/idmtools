#!/usr/bin/env bash

## echo 'First arg:' $1
## cd $1
JOB_DIRECTORY=$1
echo "enter directory: '$JOB_DIRECTORY'"
cd $JOB_DIRECTORY
bash _run.sh 1> stdout.txt 2> stderr.txt