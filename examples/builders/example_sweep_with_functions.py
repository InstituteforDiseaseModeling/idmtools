import itertools
import os
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.sweeping import SwpFn, set_param, sweep_functions
from idmtools_test import COMMON_INPUT_PATH


def sweep_task_parameter_func(task, values):
    task.set_parameter('A', values['A'])
    task.set_parameter('B', values['B'])
    task.set_parameter('C', values['C'])
    task.set_parameter('E', values['E'])
    task.set_parameter('E', values['E'])
    return {'A': values['A'],
            'B': values['B'],
            'C': values['C'],
            'D': values['D'],
            'E': values['E']}

def get_sweep_builders(sweep_task_parameters):
    """
    Build simulation builders.
    Args:
        sweep_task_parameters: User inputs may overwrite the entries in the block.

    Returns:
        lis of Simulation builders
    """
    builder = SimulationBuilder()
    funcs_list = [[
        partial(set_param, param='Run_Number', value=x),
        SwpFn(sweep_task_parameter_func, y)
        ]
        for x in range(2)  # for sweep Run_Number
        for y in sweep_task_parameters
    ]
    builder.add_sweep_definition(sweep_functions, funcs_list)
    return [builder]

if __name__ == "__main__":
    platform = Platform('Calculon')
    # define our base task
    task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"),
                                         parameters=dict())


    A = [13000, 10000]
    B = [5, 4]
    C = [0.4]
    D = [0.009, 0.005]
    E = [0.05]
    sweep_task_parameters = []
    combinations_config_params = list(itertools.product(A, B, C, D, E))
    for c in combinations_config_params:
        sweep_task_parameters.append({'A': c[0], 'B': c[1],  'C': c[2], 'D': c[3], 'E': c[4]})

    builders = get_sweep_builders(sweep_task_parameters)
    # create TemplatedSimulations from task and builders
    ts = TemplatedSimulations(base_task=task, builders=builders)
    # create experiment from TemplatedSimulations
    experiment = Experiment.from_template(ts, name="test_sweep_task_parameters")
    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)