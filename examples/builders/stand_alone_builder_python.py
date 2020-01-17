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
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH

if __name__ == "__main__":
    platform = Platform('COMPS2')
    model_path = os.path.join(COMMON_INPUT_PATH, "python", "model.py")
    ac = AssetCollection()
    assets_path = os.path.join(COMMON_INPUT_PATH, "python", "Assets")
    ac.add_directory(assets_directory=assets_path)
    pe = PythonExperiment(name=os.path.split(sys.argv[0])[1], model_path=model_path, assets=ac)
    pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
    pe.base_simulation.envelope = "parameters"
    builder = StandAloneSimulationsBuilder()
    for i in range(5):
        sim = pe.simulation()
        sim.set_parameter("a", i)
        sim.set_parameter("b", i + 10)
        builder.add_simulation(sim)
    pe.builder = builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
