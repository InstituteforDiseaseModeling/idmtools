Here is an example of how to run the [Covasim] model developed at IDM.

This approach uses a Docker container to run the simulation on a SLURM cluster with Singularity installed.

The example folder contains the following:
- `run.py`: the script that needs to be run by the user to submit the job to the cluster
- `inputs/sim.py`: the model simulation script that will be run on the cluster
- `inputs/run.sh`: the actual script that is executed on the SLURM cluster and will run `sim.py`
- `output/`: folder where simulation outputs will be downloaded to.


<!-- Refs -->
[Covasim]: https://github.com/InstituteforDiseaseModeling/covasim