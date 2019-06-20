import diskcache
from pprint import pprint

from file_exists_task import FileExistsTask
from system_task import SystemTask
from python_task import PythonTask
from workflow import Workflow

def add(a, b):
    result = a + b
    print(f'Add result: {a} + {b} = {result}')
    return result


cache = diskcache.Cache('workflow.diskcache')


tasks = [

    SystemTask(command='python --version', name='alpha'),
    SystemTask(command='python --version', name='beta'),

    SystemTask(command='python --version', name='gamma', depends_on=['beta']),
    SystemTask(command='python --version', name='delta', depends_on=['beta']),
    SystemTask(command='python --version', name='epsilon', depends_on=['beta']),

    SystemTask(command='python --version', name='zeta', depends_on=['gamma', 'delta']),

    FileExistsTask(name='eta', path='continue.txt', depends_on=['zeta']),

    PythonTask(name='theta', method=add, method_kwargs={'a': 3, 'b': 10}, depends_on=['eta'])

]

wf = Workflow(tasks=tasks)

initial_status = wf.status
print('Initial status of tasks in Workflow:')
pprint(initial_status)

wf.start()

final_status = wf.status
print('Final status of tasks in Workflow:')
pprint(final_status)
