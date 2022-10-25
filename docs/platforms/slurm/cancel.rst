===========
Cancel jobs
===========

To cancel a submitted job (simulation/experiment/suite) on the |SLURM_s| cluster you must 
use the ``scancel`` |SLURM_s| command from a terminal session connected to the |SLURM_s| 
cluster. |IT_s| submits jobs as job arrays. The job id of the job array is used with 
``scancel`` for cancelling jobs. For more information about scancel, see 
https://slurm.schedmd.com/scancel.html. 

View jobs in queue
````````````````````
To view the job id associated with the job array use the ``squeue`` command::

    squeue

For more information about squeue, see https://slurm.schedmd.com/squeue.html.

Cancel a specific job
````````````````````````
To cancel a specific job from the job array specify the job id of the job array and index number::

    scancel job-id-number-and-index-number-here

Cancel all jobs
````````````````
To cancel all jobs within the job array only specify the job id of the job array::

    scancel job-id-number-only-here