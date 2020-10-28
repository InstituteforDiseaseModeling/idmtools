<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Folder Contents](#folder-contents)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

### Overview

Here is an example of how to run the [Covasim] model developed at IDM.

This approach uses a container to run the simulation on a SLURM cluster
with Singularity installed.

### Quick Start

1. Install idmtools

   ```
   pip install idmtools[idm] 
   ```
2. Create assetcollection of covasim.sif from idm covasim image in docker hub

   ```
   python create_covasim_sif_ac.py
   ```
3. Create simulations with covasim image

   ```
   python run_covasim.py
   ```

### Folder Contents

The example folder contains the following:
- `create_covasim_sif_ac.py`: the script that is executed on the Calculon
  cluster and will create assetcollection of covasim.sif image which used for run_sim.py
  
- `run_vocasim.py`: the script that needs to be run by the user to submit the
  job to the Calculon cluster
- `inputs/sim.py`: the model simulation script that will be run on the
  cluster

- `output/`: folder where simulation outputs will be downloaded to.


<!-- Refs -->
[Covasim]: https://github.com/InstituteforDiseaseModeling/covasim
[idm Covasim from docker hub]: https://hub.docker.com/search?q=covasim&type=image
