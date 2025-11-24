
==================
CLI Slurm examples
==================

You can use |IDM_s| CLI to get all kind of statuses for |Slurm_s|.

To see job directory type the following at command prompt:

.. command-output:: idmtools slurm <JOB_DIRECTORY> get-path --suite-id <suite_id> --help
   :returncode: 0

To get the latest status of a |SLURM_s|, type the following at a command prompt:

.. command-output:: idmtools slurm <JOB_DIRECTORY> get-latest --help
   :returncode: 0

To get the status for a specific Experiment, type the following at a command prompt:

.. command-output:: idmtools slurm <JOB_DIRECTORY> get-status --exp-id <exp_id> --help
   :returncode: 0

To get the status report for a specific Suite, Experiment or Simulation, type the following at a command prompt:

.. command-output:: idmtools slurm <JOB_DIRECTORY> status-report --exp-id <exp_id> --help
   :returncode: 0
