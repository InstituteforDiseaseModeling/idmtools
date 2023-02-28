#!/usr/bin/env bash

JOB_DIRECTORY=$1
echo "enter directory: '$JOB_DIRECTORY'"
cd $JOB_DIRECTORY
bash _run.sh 1> stdout.txt 2> stderr.txt