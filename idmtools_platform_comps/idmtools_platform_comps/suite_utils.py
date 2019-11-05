
def create_platform_suite(platform, suite):
    """
    Create a suite from platform
    Returns: Platform Suite
    """
    if suite is None:
        return

    from idmtools_platform_comps.comps_platform import COMPSPlatform
    from idmtools.core import ItemType
    if not isinstance(platform, COMPSPlatform):
        print("/!\\ WARNING: Currently Suite is only supported by COMPSPlatform!")
        exit()

    # Create suite
    ids = platform.create_items(items=[suite])

    suite_uid = ids[0]
    comps_suite = platform.get_platform_item(item_id=suite_uid, item_type=ItemType.SUITE)

    return comps_suite