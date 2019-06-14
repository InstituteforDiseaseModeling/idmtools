import sys
import os
from workflow import Workflow

workflow_yaml_file = sys.argv[1]
print(os.getcwd())
wf = Workflow.from_yaml(yaml_filename=workflow_yaml_file)
print('made Workflow, starting...')
wf.start()

final_status = wf.status
from pprint import pprint
print('Final status of tasks in Workflow:')
pprint(final_status)
