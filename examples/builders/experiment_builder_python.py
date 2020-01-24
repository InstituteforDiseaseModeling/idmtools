"""
        This file demonstrates how to use ExperimentBuilder in PythonExperiment's builder.
        We are then adding the builder to PythonExperiment.

        Parameters for sweeping:
            |__ a = [0,1,2,3,4]

        Expect 5 sims with config parameters, note: "b" is not a sweep parameter, but it is depending on a's value:
            sim1: {a:0, b:2}
            sim2: {a:1, b:3}
            sim3: {a:2, b:4}
            sim4: {a:3, b:5}
            sim5: {a:4, b:6}
"""

import os
import sys
from functools import partial

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH

if __name__ == "__main__":
    platform = Platform('COMPS2')
    pe = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                          model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
    pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

    pe.base_simulation.set_parameter("c", "c-value")


    def param_update_ab(simulation, param, value):
        # Set B within
        if param == "a":
            simulation.set_parameter("b", value + 2)

        return simulation.set_parameter(param, value)


    setAB = partial(param_update_ab, param="a")

    builder = SimulationBuilder()
    # Sweep parameter "a" and make "b" depends on "a"
    builder.add_sweep_definition(setAB, range(0, 5))
    pe.builder = builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
