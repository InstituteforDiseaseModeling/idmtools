from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection

exp_id = '30a54b1f-3780-ea11-a2bf-f0921c167862'
platform = Platform('COMPS2')
pl = RequirementsToAssetCollection(platform, requirements_path='./requirements.txt')
pl.run_wi_to_create_ac(exp_id)