import sys
import os
from pprint import pprint
from workflow import Workflow

workflow_yaml_file = sys.argv[1]
print(os.getcwd())
wf = Workflow.from_yaml(yaml_filename=workflow_yaml_file)

initial_status = wf.status
print('Initial status of tasks in Workflow:')
pprint(initial_status)

print('Running workflow...')
wf.start()

final_status = wf.status
print('Final status of tasks in Workflow:')
pprint(final_status)


print('---')
print('json representation of DAG:')
pprint(wf.to_json())