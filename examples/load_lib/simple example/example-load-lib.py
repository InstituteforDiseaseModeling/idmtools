import os
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools.custom_lib.requirements_to_asset_cellection import RequirementsToAssetCollection


def run_example_astor(ac_id):
    print(f'run example with ac: {ac_id}')

    platform = Platform('COMPS2')
    ac = platform.get_item(ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)

    experiment = PythonExperiment(name="Simple Experiment Demo", model_path=os.path.join("model_astor.py"), assets=ac)
    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()


def main():
    platform = Platform('COMPS2')
    pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt',
                                       pkg_list=['astor'])

    ac_id = pl.run()
    print('ac_id: ', ac_id)

    if ac_id:
        run_example_astor(ac_id)
    else:
        print('Failed to generate asset collection!')


if __name__ == '__main__':
    main()
