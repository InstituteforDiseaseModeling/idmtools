import os
import contextlib
from idmtools.core import TRUTHY_VALUES, getLogger
from idmtools.registry.hook_specs import function_hook_impl

TEST_WITH_NEW_CODE = os.environ.get("TEST_WITH_PACKAGES", 'n').lower() in TRUTHY_VALUES
logger = getLogger(__name__)


# Make a plugin here to load our local packages if needed to test CLI functions
@function_hook_impl
def idmtools_platform_pre_create_item(item: 'IEntity', **kwargs):
    # do it dynamically
    load_packages_to_ssmt_image_dynamically(item)


def load_packages_to_ssmt_image_dynamically(item):
    with contextlib.suppress(ImportError):
        from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput
        from idmtools_platform_comps.utils.download.download import DownloadWorkItem
        from idmtools_test.utils.comps import load_library_dynamically
        if os.environ.get("TEST_WITH_PACKAGES", 'n').lower() in TRUTHY_VALUES:
            logger.debug("TEST WITH NEW CODE is enabled. Adding COMPS and IDMTOOLS package to asset")
            if isinstance(item, (AssetizeOutput, DownloadWorkItem)):
                item.add_pre_creation_hook(load_library_dynamically)
