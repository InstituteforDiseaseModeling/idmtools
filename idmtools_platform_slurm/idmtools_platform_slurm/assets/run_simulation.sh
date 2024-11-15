#!/usr/bin/env bash
# Get the parameters passed from sbatch.sh
mpi_type="$2"

SIMULATION_INDEX=$((${SLURM_ARRAY_TASK_ID} + $1))
JOB_DIRECTORY=$(find . -type d -maxdepth 1 -mindepth 1  | grep -v Assets | head -$SIMULATION_INDEX | tail -1)
cd $JOB_DIRECTORY
current_dir=$(pwd)
echo "The script is running from: $current_dir"

# Run the simulation based on whether MPI is required
if [ "$mpi_type" = "no-mpi" ]; then
    echo "Run without MPI"
    srun _run.sh 1> stdout.txt 2> stderr.txt
elif [ "$mpi_type" = "mpirun" ]; then
    echo "Run mpirun"
    mpirun "$current_dir"/_run.sh 1> stdout.txt 2> stderr.txt
elif [ "$mpi_type" = "pmi2" ] || [ "$mpi_type" = "pmix" ]; then # pmi2 or pmix
    echo "Run MPI with $mpi_type"
    srun --mpi=$mpi_type _run.sh 1> stdout.txt 2> stderr.txt
else
    echo "Invalid MPI type: $mpi_type"
fi
