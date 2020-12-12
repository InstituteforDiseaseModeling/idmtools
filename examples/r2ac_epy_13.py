
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.assets import Asset, AssetCollection 

slurm_platform = Platform("SLURM", num_cores=16)
requirements_filename = "requirements.txt"

r2ac = RequirementsToAssetCollection(
    platform=slurm_platform,
    requirements_path=requirements_filename
)
other_assets = AssetCollection.from_id(r2ac.run())
