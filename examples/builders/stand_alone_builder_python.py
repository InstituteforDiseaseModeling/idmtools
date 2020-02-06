"""
        This file demonstrates how to use StandAloneSimulationsBuilder in PythonExperiment's builder.

        we create 5 simulations and for each simulation, we set parameter 'a' = [0,4] and 'b' = a + 10:
        then add each updated simulation to builder
        then we are adding the builder to PythonExperiment
"""

import os
import sys

from idmtools.assets import AssetCollection
from idmtools.builders import StandAloneSimulationsBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH

if __name__ == "__main__":

    # define our platform
    platform = Platform('COMPS2')

    # define paths to model and extra assets folder container more common assets
    model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
    assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")

    # define our base task
    base_task = JSONConfiguredPythonTask(script_path=model_path,
                                         envelope='parameters',
                                         common_assets=AssetCollection.from_directory(assets_path))

    # define that we want to build multiple simulations
    ts = TemplatedSimulations(base_task=base_task)

    # builder the simulations from the stand alone builder
    builder = StandAloneSimulationsBuilder()
    for i in range(5):
        sim = ts.new_simulation()
        sim.task.set_parameter("a", i)
        sim.task.set_parameter("b", i + 10)
        builder.add_simulation(sim)
    ts.add_builder(builder)

    # create experiment and wait
    tags = {"string_tag": "test", "number_tag": 123}
    e = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1], tags=tags)
    e.run(platform=platform)
    # in most real scenarios, you probably do not want to wait as this will wait until all simulations
    # associated with an experiment are done. We do it in our examples to show feature and to enable
    # testing of the scripts
    e.wait()
