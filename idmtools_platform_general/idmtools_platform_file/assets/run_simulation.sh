#!/usr/bin/env bash

JOB_DIRECTORY=$1

# Create the symbolic link
ln -s "$(dirname "${BASH_SOURCE[0]}")/Assets" "${JOB_DIRECTORY}/Assets"

echo "enter directory: '$JOB_DIRECTORY'"
cd $JOB_DIRECTORY
sed -i 's/\r//g' _run.sh
bash _run.sh 1> stdout.txt 2> stderr.txt