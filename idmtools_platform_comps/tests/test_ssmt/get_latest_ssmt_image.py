from idmtools_platform_comps.utils.package_version_new import get_latest_docker_image_version_from_ghcr
from idmtools_platform_comps import __version__

def get_latest_image_stage():
    current_version = get_latest_docker_image_version_from_ghcr("idmtools-comps-ssmt-worker", base_version=__version__)
    return current_version