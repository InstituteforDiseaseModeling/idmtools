# Example shows how to override Platform config values without idmtools.ini file in the path
# Note, this example does not use idmtools.ini file. you are free to remove idmtools.ini file and try run this example

import sys

from idmtools.core.platform_factory import Platform
from examples.idmtools_ini_alias import shared_function

experiment = shared_function.create_experiment()


# We can use code to define Platform configuration. "Calculon" is Production linux environment
# To see list of environment aliases, you can run cli command: idmtools info plugins platform-aliases
with Platform('Calculon', priority='Highest', node_group="idm_abcd", num_cores=1):
    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
