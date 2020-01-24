"""
        This file demonstrates how to use YamlExperimentBuilder in PythonExperiment's builder.
        then adding the builder to PythonExperiment.

        We first load a yaml file from local dir which contains parameters/values to sweep
        then sweep parameters based in yaml file with YamlExperimentBuilder
        Behind the scenes, we are using arm sweep, each group is treated with SweepArm and then add to builder

        Parameters in yaml file
            group1:
                - a: 1
                - b: 2
                - c: [3, 4]
                - d: [5, 6]
            group2:
                - c: [3, 4]
                - d: [5, 6, 7]

        Expect sims with parameters:
            sim1: {a:1, b:2, c:3, d:5}
            sim2: {a:1, b:2, c:3, d:6}
            sim3: {a:1, b:2, c:4, d:5}
            sim4: {a:1, b:2, c:4, d:6}
            sim5: {c:3, d:5}
            sim6: {c:3, d:6}
            sim7: {c:3, d:7}
            sim8: {c:4, d:5}
            sim9: {c:4, d:6}
            sim10: {c:4, d:7}

        This builder is very similar with ArmExperimentBuilder. but in more direct way. you just need list all cared
        parameter combinations in yaml file, and let builder do the job

"""
import os
import sys
from functools import partial

from idmtools.builders import YamlSimulationBuilder
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

    yaml_builder = YamlSimulationBuilder()
    base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))
    file_path = os.path.join(base_path, 'sweeps.yaml')
    func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
    yaml_builder.add_sweeps_from_file(file_path, func_map)
    pe.builder = yaml_builder
    em = ExperimentManager(experiment=pe, platform=platform)
    em.run()
    em.wait_till_done()
