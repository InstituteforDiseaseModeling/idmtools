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
2. Install [Covasim from PyPi] (optional, only used for local
   development support)

   ```
   pip install covasim
   ```
3. Run from command line

   ```
   python run.py
   ```

### Folder Contents

The example folder contains the following:
- `run.py`: the script that needs to be run by the user to submit the
  job to the cluster
- `inputs/sim.py`: the model simulation script that will be run on the
  cluster
- `inputs/run.sh`: the actual script that is executed on the SLURM
  cluster and will run `sim.py`
- `output/`: folder where simulation outputs will be downloaded to.


<!-- Refs -->
[Covasim]: https://github.com/InstituteforDiseaseModeling/covasim
[Covasim from PyPi]: https://pypi.org/project/covasim
