"""
        This file demonstrates how to use StandAloneSimulationsBuilder in PythonExperiment's builder.

        we create 5 simulations and for each simulation, we set parameter 'a' = [0,4] and 'b' = a + 10:
        then add each updated simulation to builder
        then we are adding the builder to PythonExperiment
"""
import copy
import os
import sys

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH

if __name__ == "__main__":

    # define our platform
    platform = Platform('Calculon')

    # create experiment  object and define some extra assets
    assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
    e = Experiment(name=os.path.split(sys.argv[0])[1],
                   _tags={"string_tag": "test", "number_tag": 123},
                   assets=AssetCollection.from_directory(assets_path))

    # define paths to model and extra assets folder container more common assets
    model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")

    # define our base task including the common assets. We could also add these assets to the experiment above
    base_task = JSONConfiguredPythonTask(script_path=model_path, envelope='parameters')

    base_simulation = Simulation.from_task(base_task)

    # now build our simulations
    for i in range(5):
        # first copy the simulation
        sim = copy.deepcopy(base_simulation)
        # For now, you have to reset the uid manually when copying here. In future, you should only need to do a
        # copy method here
        sim._uid = None
        # configure it
        sim.task.set_parameter("a", i)
        sim.task.set_parameter("b", i + 10)
        # and add it to the simulations
        e.simulations.append(sim)

    # run the experiment
    e.run()
    # wait on it
    # in most real scenarios, you probably do not want to wait as this will wait until all simulations
    # associated with an experiment are done. We do it in our examples to show feature and to enable
    # testing of the scripts
    e.wait()
    # use system status as the exit code
    sys.exit(0 if e.succeeded else -1)
