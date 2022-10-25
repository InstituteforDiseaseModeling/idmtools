"""idmtools download workitem ssmt script.

This script is meant to be ran remotely on SSMT, not locally.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: noqa F405 F403
import sys
import zipfile
from logging import getLogger
import os
from COMPS.Data import WorkItem

# we have to support two ways to load the utils. The first is load from Assets
# the fallback is the installed package
# this allows us to move forward with changes to utils without need for new images
from idmtools_platform_comps.utils.ssmt_utils.file_filter import parse_filter_args_common, filter_files_and_assets

try:
    from file_filter import *
    from common import *
except (FileNotFoundError, ImportError):
    from idmtools_platform_comps.utils.ssmt_utils.file_filter import *
    from idmtools_platform_comps.utils.ssmt_utils.common import *

logger = getLogger(__name__)
user_logger = getLogger('user')


def get_argument_parser():
    p = get_common_parser("Download")
    p.add_argument("--zip-name", default="output.zip")
    return p


def create_archive_from_files(args: Namespace, files, files_from_ac, compress_type: str = "lzma"):
    if compress_type == "lzma":
        compress_type = zipfile.ZIP_LZMA
    elif compress_type == "deflate":
        compress_type = zipfile.ZIP_DEFLATED
    elif compress_type == "bz":
        compress_type = zipfile.ZIP_BZIP2
    with zipfile.ZipFile(args.zip_name, mode="w", compression=compress_type) as zo:
        for f in tqdm(sorted(files, key=lambda x: x[1]), total=len(files), mininterval=5, maxinterval=15):
            logger.info(f"Adding {f[0].encode('ascii', 'ignore').decode('utf-8')} to {f[1].encode('ascii', 'ignore').decode('utf-8')}")
            zo.write(f[0], f[1].encode('ascii', 'ignore').decode('utf-8'))
        for f in tqdm(files_from_ac, total=len(files_from_ac), mininterval=5, maxinterval=15):
            fn = PurePath(f.relative_path).joinpath(f.file_name) if f.relative_path else f.file_name
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Adding {f[0]} to {fn}")
            zo.write(f.uri, fn)


if __name__ == "__main__":  # pragma: no cover
    # build our argument parser and then parse the command line
    parser = get_argument_parser()
    parser.add_argument("--compress-type", choices=["lzma", "deflate", "bz2"], default="lzma")
    args = parser.parse_args()

    # Set our JOB config global with config provided
    JOB_CONFIG = vars(args)
    # register our error handler
    sys.excepthook = get_error_handler_dump_config_and_error(JOB_CONFIG)

    # Parse the common arguments common to filter scripts
    entity_filter_func, fn_format_func = parse_filter_args_common(args)

    # login
    client = login_to_env()

    # Load our work-item
    wi = WorkItem.get(os.environ['COMPS_WORKITEM_GUID'])

    # Gather all our files in Experiments, Simulations, and Asset Collections
    files, files_from_ac = filter_files_and_assets(args, entity_filter_func, wi, fn_format_func)
    ensure_no_duplicates(files_from_ac, files)

    if args.dry_run:
        print_results(files_from_ac, files)
    else:
        create_archive_from_files(args, files, files_from_ac)
