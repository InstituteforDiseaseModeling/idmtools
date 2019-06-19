import diskcache
from pprint import pprint

from system_task import SystemTask
from workflow import Workflow


cache = diskcache.Cache('workflow.diskcache')


tasks = [

    SystemTask(command='python --version', name='alpha'),
    SystemTask(command='python --version', name='beta'),

    SystemTask(command='python --version', name='gamma', depends_on=['beta']),
    SystemTask(command='python --version', name='delta', depends_on=['beta']),
    SystemTask(command='python --version', name='epsilon', depends_on=['beta']),

    SystemTask(command='python --version', name='zeta', depends_on=['gamma', 'delta']),

    SystemTask(command='python --version', name='eta', depends_on=['zeta'])

]

wf = Workflow(tasks=tasks)

initial_status = wf.status
print('Initial status of tasks in Workflow:')
pprint(initial_status)

wf.start()

final_status = wf.status
print('Final status of tasks in Workflow:')
pprint(final_status)
