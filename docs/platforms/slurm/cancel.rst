===========
Cancel jobs
===========

To cancel a submitted job (simulation/experiment/suite) on the |SLURM_s| cluster you must 
use the ``scancel`` |SLURM_s| command from a terminal session connected to the |SLURM_s| 
cluster. |IT_s| submits jobs as job arrays. The job id of the job array is used with 
``scancel`` for cancelling jobs.

View jobs in queue
````````````````````
To view the job id associated with the job array use the ``squeue`` command::

    squeue

Cancel a specific job
````````````````````````
To cancel a specific job from the job arrary specify the job id and index number::

    scancel job-id-number-and-index-number-here

Cancel all jobs
````````````````
To cancel all jobs within the job arrary only specify the job id number::

    scancel job-id-number-only