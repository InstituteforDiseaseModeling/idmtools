#!/usr/bin/env bash
# Get the parameters passed from sbatch.sh
mpi_type="$2"
mpi_flag="$3"

SIMULATION_INDEX=$((${SLURM_ARRAY_TASK_ID} + $1))
JOB_DIRECTORY=$(find . -type d -maxdepth 1 -mindepth 1  | grep -v Assets | head -$SIMULATION_INDEX | tail -1)
cd $JOB_DIRECTORY
# Run the simulation based on whether MPI is required
if [ "$mpi_flag" == "mpi" ]; then
    echo "run mpi with $mpi_type"
    srun --mpi=$mpi_type _run.sh 1> stdout.txt 2> stderr.txt
else
    srun _run.sh 1> stdout.txt 2> stderr.txt
fi
