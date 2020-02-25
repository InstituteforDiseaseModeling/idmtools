import os

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python import PythonExperiment
from idmtools.custom_lib.requirements_to_asset_cellection import RequirementsToAssetCollection


def test():
    platform = Platform('COMPS2')

    pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt',
                                       pkg_list=['numpy == 1.16.1', 'pandas<=0.23.1', 'six<'])

    exp_id = '874e86c6-704f-ea11-a2be-f0921c167861'
    wi_id = '8ec6fb40-4653-ea11-a2bf-f0921c167862'
    from idmtools.entities.experiment import Experiment
    from idmtools.core import ItemType
    # item = Experiment(_uid=exp_id)
    # item = pl.platform.get_item(exp_id, ItemType.EXPERIMENT)

    item = pl.platform.get_item(wi_id, ItemType.WORKFLOW_ITEM)

    pl.wait_till_done(item)
    exit()

    pkg_list = pl.validate_requirements()
    exit()

    pl.save_updated_requirements()
    exit()

    pl.validate_requirements(save_to_file=True)
    exit()

    ret = pl.is_requirements_changed()
    print(ret)


def run_example_hello(ac_id):
    print(f'run example with ac: {ac_id}')

    platform = Platform('COMPS2')
    ac = platform.get_item(ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)

    experiment = PythonExperiment(name="Simple Experiment Hello", model_path=os.path.join("model_hello.py"), assets=ac)
    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()


def run_example_jieba(ac_id):
    print(f'run example with ac: {ac_id}')

    platform = Platform('COMPS2')
    ac = platform.get_item(ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)

    experiment = PythonExperiment(name="Simple Experiment Demo", model_path=os.path.join("model_jieba.py"), assets=ac)
    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()


def run_example_astor(ac_id):
    print(f'run example with ac: {ac_id}')

    platform = Platform('COMPS2')
    ac = platform.get_item(ac_id, item_type=ItemType.ASSETCOLLECTION, raw=False)

    experiment = PythonExperiment(name="Simple Experiment Demo", model_path=os.path.join("model_astor.py"), assets=ac)
    em = ExperimentManager(experiment=experiment, platform=platform)
    em.run()
    em.wait_till_done()


def main():
    # ac_id = 'b8dd6337-ce54-ea11-a2bf-f0921c167862'
    # run_example(ac_id)
    # exit()
    # test(pl)

    model_folder = r'C:\Projects\idmtools_zdu\examples\load_lib'  # ['idmtools_models.egg==info', 'idmtools.egg==info', 'jieba==0.42.1', 'COMPS==0.1.1.1', 'astor==0.8.1']
    # model_folder = r'C:\Projects\idmtools_zdu\examples\analyzers'   # ['idmtools.egg==info', 'numpy==1.16.4', 'pandas==0.24.2']
    model_folder = r'C:\Projects\idmtools_zdu\examples\ssmt'      # ['idmtools.egg==info', 'matplotlib==3.1.2', 'tweepy==3.8.0', 'simtools==0.2']

    model_folder = r'C:\Projects\idmtools_zdu\examples\ssmt\check installed packages'   # ['idmtools.egg==info']
    model_folder = r'C:\Projects\idmtools_zdu\examples\ssmt\generic_ssmt'   # ['matplotlib==3.1.2', 'idmtools.egg==info', 'simtools==0.2']
    model_folder = r'C:\Projects\idmtools_zdu\examples\ssmt\hello_world'    # ['idmtools.egg==info']
    model_folder = r'C:\Projects\idmtools_zdu\examples\ssmt\simple_analysis'    # ['matplotlib==3.1.2', 'idmtools.egg==info', 'tweepy==3.8.0', 'simtools==0.2']
    model_folder = r'C:\Projects\idmtools_zdu\examples\ssmt\simple_assets'  # ['idmtools.egg==info']

    # model_folder = r'C:\Projects\idmtools_zdu\examples'

    # extra_libraries = retrieve_python_dependencies(model_folder)
    # print(extra_libraries)
    # exit()
    #
    #
    # test_auto_pkg_detection(model_folder)
    # exit()

    # test_auto_detect_lib()
    # exit()

    platform = Platform('COMPS2')
    pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt',
                                       pkg_list=['astor'])  # 'jieba', 'astor', 'tweepy'

    # print(pl.requirements)
    # print(pl.checksum)
    # print(pl.is_requirements_changed())
    # exit()

    # pkg_list = pl.validate_requirements()
    # print(pkg_list)
    # exit()

    # ac_id = pl.retrieve_ac_by_tag()
    # wi_id = '70b7b935-1d54-ea11-a2bf-f0921c167862'
    # ac_id = pl.retrieve_ac_by_wi(wi_id)
    # print('ac_id:: ', ac_id)
    # exit()

    # ac = pl.retrieve_ac_by_tag()
    # print('ac_id: ', ac.id)
    # exit()

    ac_id = pl.run()
    print('ac_id: ', ac_id)

    if ac_id:
        # run_example_hello(ac_id)
        # run_example_jieba(ac_id)
        run_example_astor(ac_id)
    else:
        print('Failed to generate asset collection!')


if __name__ == '__main__':
    main()
