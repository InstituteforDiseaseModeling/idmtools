import os
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools.custom_lib.requirements_to_asset_collection import RequirementsToAssetCollection


def run_example(ac_id):
    print(f'run example with ac: {ac_id}')

    exp_name = "run_example_use_ac"

    platform = Platform('COMPS2')
    common_assets = AssetCollection.from_id(ac_id, platform=platform)
    task = JSONConfiguredPythonTask(script_path=os.path.abspath("model_file.py"), common_assets=common_assets)
    experiment = Experiment(name=exp_name, simulations=[task.to_simulation()])
    experiment.tags = {'ac_id': str(ac_id)}

    platform.run_items(experiment)
    platform.wait_till_done(experiment)

    if experiment.succeeded:
        print('Experiment is complete!')
    else:
        print('Failed to run example!')


def main():
    platform = Platform('COMPS2')
    pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt', pkg_list=['astor==0.8.0'])

    ac_id = pl.run()
    print('ac_id: ', ac_id)

    if ac_id:
        run_example(ac_id)
    else:
        print('Failed to generate asset collection!')


if __name__ == '__main__':
    main()
