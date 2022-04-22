"""idmtools ssmt script.

This script is used on server side only and not meant to be ran on a local machine.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: noqa F405 F403
import sys
from argparse import Namespace
from logging import getLogger
from COMPS.Data.WorkItem import RelationType
from typing import List, Dict
import os
from COMPS.Data import AssetCollectionFile, WorkItem

# we have to support two ways to load the utils. The first is load from Assets
# the fallback is the installed package
# this allows us to move forward with changes to utils without need for new images
try:
    from file_filter import *
    from common import *
except (FileNotFoundError, ImportError):
    from idmtools_platform_comps.utils.ssmt_utils.file_filter import *
    from idmtools_platform_comps.utils.ssmt_utils.common import *

logger = getLogger(__name__)
user_logger = getLogger('user')


class NoFileFound(Exception):
    doc_link: str = "platforms/comps/errors.html#errors"


def create_asset_collection(file_list: SetOfAssets, ac_files: List[AssetCollectionFile], tags: Dict[str, str]):  # pragma: no cover
    """

    Args:
        file_list:
        ac_files: AC Files
        tags: Tags to add

    Returns:

    """
    asset_collection = AssetCollection()
    asset_collection.set_tags(tags)
    # Maps checksum to AssetCollectionFile and the path on disk to file
    asset_collection_map: Dict[uuid.UUID, Tuple[AssetCollectionFile, str, int]] = dict()
    for file in file_list:
        fn = os.path.basename(file[1])
        acf = AssetCollectionFile(file_name=fn, relative_path=file[1].replace(fn, "").strip("/"), md5_checksum=file[2])
        asset_collection_map[file[2]] = (acf, file[0], file[3])
        asset_collection.add_asset(acf)

    # add files from acs
    for f in ac_files:
        asset_collection.add_asset(f)

    # do initial save to see what assets are in comps
    missing_files = asset_collection.save(return_missing_files=True)
    if missing_files:
        user_logger.info(f"{len(missing_files)} not currently in COMPS as Assets")

        ac2 = AssetCollection()
        new_files = 0
        total_to_upload = 0
        for checksum, asset_details in asset_collection_map.items():
            if checksum in missing_files:
                new_files += 1
                total_to_upload += asset_details[2]
                acf = AssetCollectionFile(file_name=asset_details[0].file_name, relative_path=asset_details[0].relative_path)
                ac2.add_asset(acf, asset_details[1])
            else:
                ac2.add_asset(asset_details[0])
        user_logger.info(f"Saving {new_files} totaling {humanfriendly.format_size(total_to_upload)} assets to comps")
        ac2.set_tags(tags)
        ac2.save()
        asset_collection = ac2
    return asset_collection


def get_argument_parser():
    p = get_common_parser("AssetizeOutputs")
    p.add_argument("--asset-tag", action='append', help="List of tags as value pairs. Eg: ABC=123")
    return p


def build_asset_tags(parsed_args: Namespace) -> Dict[str, str]:
    """
    Builds our Asset tag dic from tags

    Args:
        parsed_args: Parse Arg

    Returns:
        Dict of tags
    """
    asset_tags = dict()
    if parsed_args.asset_tag:
        for tag in parsed_args.asset_tag:
            name, value = tag.split("=")
            asset_tags[name] = value
    return asset_tags


if __name__ == "__main__":  # pragma: no cover
    # build our argument parser and then parse the command line
    parser = get_argument_parser()
    args = parser.parse_args()

    # Set our JOB config global with config provided
    JOB_CONFIG = vars(args)
    # register our error handler
    sys.excepthook = get_error_handler_dump_config_and_error(JOB_CONFIG)
    print(args)

    # Parse the common arguments common to filter scripts
    entity_filter_func, fn_format_func = parse_filter_args_common(args)
    # Parse our Tags
    asset_tags = build_asset_tags(args)

    # login
    client = login_to_env()

    # Load our workitem
    wi = WorkItem.get(os.environ['COMPS_WORKITEM_GUID'])

    # Gather all our files in Experiments, Simulations, and Asset Collections
    files, files_from_ac = filter_files_and_assets(args, entity_filter_func, wi, fn_format_func)
    if len(files) == 0 and len(files_from_ac) == 0:
        raise NoFileFound("No files found with patterns specified. Please verify your filters.")

    ensure_no_duplicates(files_from_ac, files)

    if args.dry_run:
        print_results(files_from_ac, files)
    else:
        ac = create_asset_collection(files, files_from_ac, tags=asset_tags)

        with open('asset_collection.id', 'w') as o:
            user_logger.info(ac.id)
            o.write(str(ac.id))

        wi.add_related_asset_collection(ac.id, RelationType.Created)
