"""
        This file demonstrates how to use CsvExperimentBuilder in PythonExperiment's builder.
        then adding the builder to PythonExperiment.

        We first load a csv file from local dir which contains parameters/values to sweep
        then sweep parameters based in csv file with CsvExperimentBuilder
        the csv file basically already lists all possible combinations of parameters you wan to sweep

        Paramaters names(header) and values in csv file
            a,b,c,d
            1,2,3,
            1,3,1,
            2,2,3,4
            2,2,2,5
            2,,3,6
        Expect sims with parameters:
            sim1: {a:1, b:2, c:3}
            sim2: {a:1, b:3, c:1}
            sim3: {a:2, b:2, c:3, d:4}
            sim4: {a:2, b:2, c:2, d:5}
            sim5: {a:2, c:3, d:6}  <-- no 'b'

        This builder can be used to test or simple scenarios.
        for example, you may only want to test list of parameter combinations, and do not care about anything else,
        you can list them in csv file so you do not have to go through traditional sweep method(i.e ExperimentBuilder's)

"""

import os
import sys
from functools import partial
import numpy as np

from idmtools.builders import CsvExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


setA = partial(param_update, param="a")
setB = partial(param_update, param="b")
setC = partial(param_update, param="c")
setD = partial(param_update, param="d")

if __name__ == "__main__":
    platform = Platform('COMPS2')
    pe = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                          model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
    pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

    pe.base_simulation.set_parameter("c", "c-value")

    builder = CsvExperimentBuilder()
    base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))
    file_path = os.path.join(base_path, 'sweeps.csv')
    func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
    type_map = {'a': np.int, 'b': np.int, 'c': np.int, 'd': np.int}
    builder.add_sweeps_from_file(file_path, func_map, type_map)
    pe.builder = builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
