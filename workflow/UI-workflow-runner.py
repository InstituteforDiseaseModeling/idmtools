import diskcache
from pprint import pprint
from PyInquirer import prompt, print_json
from file_exists_task import FileExistsTask
from finalize_task import FinalizeTask
from system_task import SystemTask
from python_task import PythonTask
from workflow import Workflow
import webbrowser
import json
import os

def add(a, b):
    result = a + b
    print(f'Add result: {a} + {b} = {result}')
    return result


def saveJson(content):
    with open("UI/data1.js", "w") as dataFile:
        dataFile.write(content)
        dataFile.close()


def showJson():
    seeWF = [
        {
            'type': 'list',
                'name': 'wf',
                'choices': ['Yes', 'No'],
                'message': 'See current workflow?',
                'filter': lambda val: val.lower()
        }
    ]

    answers = prompt(seeWF)

    if "yes" in answers["wf"]:
        webbrowser.open("file://" + os.path.join(os.getcwd(), "UI/cytoscapeTest.html"))

cache = diskcache.Cache('workflow.diskcache')


tasks = [

    SystemTask(command=['python', '--version'], name='alpha'),
    SystemTask(command=['python', '--version'], name='beta'),

    SystemTask(command=['python', '--version'], name='gamma', depends_on=['beta']),
    SystemTask(command=['python', '--version'], name='delta', depends_on=['beta']),
    SystemTask(command=['python', '--version'], name='epsilon', depends_on=['beta']),

    SystemTask(command=['python', '--version'], name='zeta', depends_on=['gamma', 'delta']),

    FileExistsTask(name='eta', path='continue.txt', depends_on=['zeta']),

    PythonTask(name='theta', method=add, method_kwargs={'a': 3, 'b': 10}, depends_on=['eta']),

    FinalizeTask(name='finalize')

]

startSample = [
        {
            'type': 'list',
            'name': 'run',
            'choices': ['Yes', 'No'],
            'message': 'Run Sample?',
            'filter': lambda val: val.lower()
        }
    ]

seeInput = [
    {
         'type': 'list',
            'name': 'input',
            'choices': ['Yes', 'No'],
            'message': 'See Input workflow first?',
            'filter': lambda val: val.lower()
    }  
]

seeOutput = [
    {
         'type': 'list',
            'name': 'output',
            'choices': ['Yes', 'No'],
            'message': 'See workflow output?',
            'filter': lambda val: val.lower()
    }  
]

continueExec = [
    {
         'type': 'list',
            'name': 'continue',
            'choices': ['Yes', 'No'],
            'message': 'continue with execution?',
            'filter': lambda val: val.lower()
    }  
]

answers = prompt(startSample)

if "yes" in answers["run"]:
    

    wf = Workflow(name="test", tasks=tasks)

    #write json to file
    saveJson("var data = " + json.dumps(wf.to_json()))
    #show workflow
    showJson()

    
    continueAnswer = prompt(continueExec)

    if "yes" in continueAnswer['continue']:

        initial_status = wf.status
        print('Initial status of tasks in Workflow:')
        pprint(initial_status)

        wf.start()

        final_status = wf.status
        print('Final status of tasks in Workflow:')
        pprint(final_status)

        # write json to file
        saveJson("var data = " + json.dumps(wf.to_json()))
        # show workflow
        showJson()
