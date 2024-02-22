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
from idmtools.core.platform_factory import platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH

# define function partials to be used during sweeps
setA = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="a")
setB = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="b")
setC = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="c")
setD = partial(JSONConfiguredPythonTask.set_parameter_sweep_callback, param="d")

if __name__ == "__main__":
    # define what platform we want to use. Here we use a context manager but if you prefer you can
    # use objects such as Platform('BELEGOST') instead
    with platform('Calculon'):
        # define our base task
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"),
                                             parameters=dict(c='c-value'))
        # define our input csv sweep
        base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))
        file_path = os.path.join(base_path, 'sweeps.yaml')
        builder = YamlSimulationBuilder()
        # define a list of functions to map the specific yaml values
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        builder.add_sweeps_from_file(file_path, func_map)
        # optionally, if you can also pass a function that is used for all parameters
        # The default behaviour of the builder is to assume the default function will be a partial
        # and attempts to call it with one var(param) before building sweep
        # builder.add_sweeps_from_file(file_path, JSONConfiguredPythonTask.set_parameter_partial)

        # now define we want to create a series of simulations using the base task and the sweep
        ts = TemplatedSimulations.from_task(base_task)
        # optionally we could update the base simulation metdata here
        # ts.base_simulations.tags['example'] 'yes'
        ts.add_builder(builder)

        # define our experiment from our template and add some metadata to the experiment
        experiment = Experiment.from_template(ts,
                                              name=os.path.split(sys.argv[0])[1],
                                              tags={"string_tag": "test", "number_tag": 123}
                                              )

        # run the experiment and wait. By default run does not wait
        # in most real scenarios, you probably do not want to wait as this will wait until all simulations
        # associated with an experiment are done. We do it in our examples to show feature and to enable
        # testing of the scripts
        experiment.run(wait_until_done=True)
        # use system status as the exit code
        sys.exit(0 if experiment.succeeded else -1)
