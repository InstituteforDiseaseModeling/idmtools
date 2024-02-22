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
    # use objects such as Platform('COMPS') instead
    with platform('Calculon'):
        # define our base task
        base_task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"),
                                             parameters=dict(c='c-value'))
        # define our input csv sweep
        base_path = os.path.abspath(os.path.join(COMMON_INPUT_PATH, "builder"))
        file_path = os.path.join(base_path, 'sweeps.csv')
        builder = CsvExperimentBuilder()
        func_map = {'a': setA, 'b': setB, 'c': setC, 'd': setD}
        type_map = {'a': np.int64, 'b': np.int64, 'c': np.int64, 'd': np.int64}
        builder.add_sweeps_from_file(file_path, func_map, type_map)

        # now define we want to create a series of simulations using the base task and the sweep
        ts = TemplatedSimulations.from_task(base_task)
        # optionally we could update the base simulation metdata here
        # ts.base_simulations.tags['example'] 'yes'
        ts.add_builder(builder)

        # define our experiment with its metadata
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
