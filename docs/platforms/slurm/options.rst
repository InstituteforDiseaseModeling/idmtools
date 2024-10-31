=========================
Configuration and options
=========================
|IT_s| supports the |SLURM_s| options for configuring, submitting and running jobs.
The following lists some of the sbatch options (https://slurm.schedmd.com/sbatch.html)
that are used when making calls to :py:class:`idmtools_platform_slurm.platform_operations.SlurmPlatform`:

* account (https://slurm.schedmd.com/sbatch.html#OPT_account)
* cpus_per_task (https://slurm.schedmd.com/sbatch.html#OPT_cpus-per-task)
* exclusive (https://slurm.schedmd.com/sbatch.html#OPT_exclusive)
* mem_per_cpu (https://slurm.schedmd.com/sbatch.html#OPT_mem-per-cpu)
* modules (https://slurm.schedmd.com/sbatch.html#OPT_modules)
* nodes (https://slurm.schedmd.com/sbatch.html#OPT_nodes)
* ntasks (https://slurm.schedmd.com/sbatch.html#OPT_ntasks)
* partition (https://slurm.schedmd.com/sbatch.html#OPT_partition)
* requeue (https://slurm.schedmd.com/sbatch.html#OPT_requeue)
* time (https://slurm.schedmd.com/sbatch.html#OPT_time)
* mpi_type: MPI type to use in slurm. Default is pmi2. Options are pmi2, pmix