from pprint import pprint

from finalize_task import FinalizeTask
from system_task import SystemTask
from python_task import PythonTask
from workflow import Workflow
from iterative_python_task import IterativePythonTask
from iteration_manager_python_task import IterationManagerPythonTask


# All python-called task methods must return result, next_status
# None for either/both is ok
def add(a, b):
    result = a + b
    print(f'Add result: {a} + {b} = {result}')
    return result, None


def add_file(input_filename, output_filename):
    import pandas as pd
    df = pd.read_csv(input_filename, index_col=0)
    df.loc[:, 'a'] = df['a'] + df['b']
    df.to_csv(output_filename)
    return None, None


def rename_file(file, to):
    import os
    os.rename(file, to)
    return None, None


iteration_args = {
    'class': IterativePythonTask,
    'method': add_file,
    'name_root': 'iter',
    'method_kwargs': {
        'input_filename': {
            'pattern': 'add_result_%d.csv',
            'offset': -1  # apply this numerical shift to the task's number to get the right pattern input
        },
        'output_filename': {
            'pattern': 'add_result_%d.csv',
            'offset': 0  # apply this numerical shift to the task's number to get the right pattern input
        }
    }
}

iteration_mgr = IterationManagerPythonTask(name='iteration-manager',
                                           depends_on=['alpha', 'beta'],
                                           iteration_args=iteration_args,  # these define it
                                           workflow=None)  # must be set after Workflow creation to be functional

tasks = [
    SystemTask(name='alpha', command='python --version', depends_on=[]),
    SystemTask(name='beta', command='python --version', depends_on=[]),
    SystemTask(name='zeta', command='python --version', depends_on=[]),
    iteration_mgr,
    SystemTask(name='gamma', command='python --version', depends_on=['iteration-manager']),
    PythonTask(name='delta', method=add, method_kwargs={'a': 3, 'b': 10}, depends_on=['gamma', 'zeta']),
    FinalizeTask(name='finalize', depends_on=[])

]

wf = Workflow(name='demo', tasks=tasks)
iteration_mgr.workflow = wf

initial_status = wf.status
print('Initial status of tasks in Workflow:')
pprint(initial_status)

wf.start()

final_status = wf.status
print('Final status of tasks in Workflow:')
pprint(final_status)

# import json
# print('Final json representation:')
# print(json.dumps(wf.to_json(), indent=2))

# PythonTask(name='rename_file', method=rename_file, method_kwargs={'file': 'rename_me.csv', 'to': 'add_result_-1.csv'},
#            depends_on=['alpha', 'beta'])

# Questions/Discussion:
# - passing results from one task to another (can we do it programmatically for PythonTasks?)
# - discovery of iterative tasks seems bad. But where else to store/find their definitions if
#   they are generated programmatically? Their data can include function names (can we pickle this?)
# - appropriate data store type/usage?
# - iteration: the alternatives to adding new tasks to a workflow are:
#   - Having a loop task with additional written-out state (e.g. ids of workflows attached to loop passes)
#   - Having no iteration in tasks directly. Iteration is handled by individual tasks themselves internally
#     (e.g. run_calib_iterations.py <calib_dir> -n_iter 10
