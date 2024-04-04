# Example shows how to override Platform config values
import os
import sys

from idmtools.core.platform_factory import Platform
from examples.idmtools_ini_alias import shared_function

experiment = shared_function.create_experiment()

# We can use code to define Platform configuration. "CALCULON" is Production Linux environment
# To see list of environment aliases, you can run cli command: idmtools info plugins platform-aliases
with Platform('CALCULON',
              priority='Normal',
              simulation_root=os.path.join('$COMPS_PATH(USER)', 'my_output'),
              node_group='idm_abcd',
              num_cores=1,
              num_retries=0,
              exclusive=False):

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
