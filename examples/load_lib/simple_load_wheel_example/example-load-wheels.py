import os
import sys

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection


def run_example(ac_id):
    print(f'run example with ac: {ac_id}')
    # create AssetCollection based on ac_id
    common_assets = AssetCollection.from_id(ac_id, as_copy=True)

    # create python task with script 'model_file.py', task is doing this in comps: "python ./Assets/model_file.py"
    task = JSONConfiguredPythonTask(script_path=os.path.abspath("model_file.py"), common_assets=common_assets)

    # create experiment with 1 base simulation with python task
    experiment = Experiment(name=os.path.split(sys.argv[0])[1], simulations=[task.to_simulation()])
    experiment.tags = {'ac_id': str(ac_id)}

    experiment.run(wait_until_done=True)

    if experiment.succeeded:
        print('Experiment is complete!')
    else:
        print('Failed to run example!')


def main():
    # RequirementsToAssetCollection will do:
    # 1. check if asset collection exists for given requirements, return ac id (#4) if exists
    # 2. create an Experiment to install the requirements on CALCULON
    # 3. create a WorkItem to create a Asset Collection
    # 4. return ac id based on the requirements.txt
    # note: pkg_list is not required. package in this list will override package in requirements.txt
    pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt', pkg_list=['astor==0.8.0'],
                                       local_wheels=['seaborn-0.7.1-py2.py3-none-any.whl', 'lz4-0.18.1-cp36-cp36m-win_amd64.whl'])

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
