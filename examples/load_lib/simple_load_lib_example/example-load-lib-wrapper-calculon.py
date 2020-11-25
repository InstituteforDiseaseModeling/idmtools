import os
import sys

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.templated_script_task import TemplatedScriptTask, get_script_wrapper_unix_task, \
    LINUX_PYTHON_PATH_WRAPPER
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection


def run_example(ac_id):
    print(f'run example with ac: {ac_id}')

    # create AssetCollection based on ac_id
    common_assets = AssetCollection.from_id(ac_id,  as_copy=True)

    # create python task with script 'model_file0.py', task is doing this in comps: "python ./Assets/model_file0.py"
    # this example, model_file0.py does not need to set python path anymore
    task = JSONConfiguredPythonTask(script_path=os.path.abspath("model_file0.py"), common_assets=common_assets)
    wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)

    # we have to set the bash path remotely
    wrapper_task.script_binary = "/bin/bash"
    # create experiment with 1 base simulation with python task
    experiment = Experiment.from_task(name=os.path.basename(__file__), task=wrapper_task)
    experiment.tags = {'ac_id': str(ac_id)}

    experiment.run(wait_until_done=True)

    if experiment.succeeded:
        print('Experiment is complete!')
    else:
        print('Failed to run example!')


def main():
    # RequirementsToAssetCollection will do:
    # 1. check if asset collection exists for given requirements, return ac id (#4) if exists
    # 2. create an Experiment to install the requirements on COMPS
    # 3. create a WorkItem to create a Asset Collection
    # 4. return ac id based on the requirements.txt
    # note: pkg_list is not required. package in this list will override package in requirements.txt
    pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt', pkg_list=['astor==0.8.1'])
    ac_id = pl.run()
    print('ac_id: ', ac_id)

    if ac_id:
        # create experiment with asset collection
        run_example(ac_id)
    else:
        print('Failed to generate asset collection!')


if __name__ == '__main__':
    with Platform('CALCULON') as platform:
        main()
