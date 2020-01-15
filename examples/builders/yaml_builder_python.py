import os
import sys
from functools import partial
import numpy as np

from idmtools.builders import CsvExperimentBuilder, YamlExperimentBuilder
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
    platform = Platform('COMPS')
    pe = PythonExperiment(name=os.path.split(sys.argv[0])[1],
                          model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))
    pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

    pe.base_simulation.set_parameter("c", "c-value")

    yaml_builder = YamlExperimentBuilder()
    base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))
    file_path = os.path.join(base_path, 'sweeps.yaml')
    func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
    yaml_builder.add_sweeps_from_file(file_path, func_map)
    pe.builder = yaml_builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
