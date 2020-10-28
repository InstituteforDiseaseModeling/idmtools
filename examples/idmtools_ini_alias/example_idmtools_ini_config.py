# Example shows how to use idmtools.ini file with Platform

import sys

from idmtools.core.platform_factory import Platform
from examples.idmtools_ini_alias import shared_function

experiment = shared_function.create_experiment()

# create a platform with "COMPS_SLURM" block which defined in simtools.ini file
with Platform('COMPS_SLURM'):
    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
