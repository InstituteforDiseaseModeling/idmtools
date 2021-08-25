"""idmtools comps cli comands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: D301
import glob
import json as json_parser
import os
import sys
from typing import Optional, List
import tabulate
from getpass import getpass
from logging import getLogger
from COMPS.CredentialPrompt import CredentialPrompt
import json as je
from idmtools.assets import AssetCollection
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

logger = getLogger(__name__)
user_logger = getLogger('user')


def add_item(assets: AssetCollection, file: str):
    """
    Add Item.

    Args:
        assets: Assets
        file: File or Directory

    Returns:
        None

    Raises:
        FileNotFoundError if file cannot be found.
    """
    if os.path.isdir(file):
        assets.add_directory(file)
    elif os.path.isfile(file):
        assets.add_asset(file)
    else:
        user_logger.error(f"Cannot find file {file}")
        raise FileNotFoundError(f"Cannot find file {file}")


try:

    class StaticCredentialPrompt(CredentialPrompt):
        """Provides a class to allow login to comps from a username password that is static or provided."""
        def __init__(self, comps_url, username, password):
            """Constructor."""
            if (comps_url is None) or (username is None) or (password is None):
                raise RuntimeError('Missing comps_url, or username or password')
            self._times_prompted = 0
            self.comps_url = comps_url
            self.username = username
            self.password = password

        def prompt(self):
            """Return our stores username and password."""
            self._times_prompted = self._times_prompted + 1
            if self._times_prompted > 3:
                raise PermissionError('Failure authenticating')
            return {'Username': self.username, 'Password': self.password}

    os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = '1'
    from idmtools.core.platform_factory import Platform
    import click
    from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput
    from idmtools_platform_comps.utils.file_filter_workitem import DEFAULT_EXCLUDES
    from idmtools_platform_comps.comps_platform import COMPSPlatform

    @click.group(short_help="COMPS Related Commands")
    @click.argument('config-block')
    @click.pass_context
    def comps(ctx: click.Context, config_block):
        """
        Commands related to managing the COMPS platform.

        CONFIG_BLOCK - Name of configuration section or alias to load COMPS connection information from
        """
        ctx.obj = dict(config_block=config_block)

    @comps.command(help="Login to COMPS")
    @click.option('--username', required=True, help="Username")
    @click.option('--password', help="Password")
    @click.pass_context
    def login(ctx: click.Context, username, password):  # noqa D103
        from COMPS import Client
        from idmtools.core.logging import SUCCESS
        os.environ['IDMTOOLS_LOGGING_USER_OUTPUT'] = '0'
        if password:
            user_logger.warning("Password the password via the command line is considered insecure")
        else:
            password = getpass("Password:")
        # make platform object to load info from alias or config but don't login
        platform = Platform(ctx.obj['config_block'], _skip_login=True)

        try:
            Client.login(platform.endpoint,
                         StaticCredentialPrompt(comps_url=platform.endpoint, username=username, password=password))
            user_logger.log(SUCCESS, "Login succeeded")
        except PermissionError:
            user_logger.error(f"Could not loging to {platform.endpoint}")
            sys.exit(-1)

    @comps.command(help="Allows Downloading outputs from the command line")
    @click.option('--pattern', default=[], multiple=True, help="File patterns")
    @click.option('--exclude-pattern', default=DEFAULT_EXCLUDES, multiple=True, help="File patterns")
    @click.option('--experiment', default=[], multiple=True, help="Experiment ids to filter for files to download")
    @click.option('--simulation', default=[], multiple=True, help="Simulation ids to filter for files to download")
    @click.option('--work-item', default=[], multiple=True, help="WorkItems ids to filter for files to download")
    @click.option('--asset-collection', default=[], multiple=True,
                  help="Asset Collection ids to filter for files to download")
    @click.option('--dry-run/--no-dry-run', default=False,
                  help="Gather a list of files that would be downloaded instead of actually downloading")
    @click.option('--wait/--no-wait', default=True, help="Wait on item to finish")
    @click.option('--include-assets/--no-include-assets', default=False,
                  help="Scan common assets of WorkItems and Experiments when filtering")
    @click.option('--verbose/--no-verbose', default=True, help="Enable verbose output in worker")
    @click.option('--json/--no-json', default=False, help="Outputs File list as JSON when used with dry run")
    @click.option('--simulation-prefix-format-str', default=None,
                  help="Simulation Prefix Format str. Defaults to '{simulation.id}'. For no prefix, pass a empty string")
    @click.option('--work-item-prefix-format-str', default=None, help="WorkItem Prefix Format str. Defaults to ''")
    @click.option('--name', default=None, help="Name of Download Workitem. If not provided, one will be generated")
    @click.option('--output-path', default=os.getcwd(), help="Output path to save zip")
    @click.option('--delete-after-download/--no-delete-after-download', default=True,
                  help="Delete the workitem used to gather files after download")
    @click.option('--extract-after-download/--no-extract-after-download', default=True,
                  help="Extract zip after download")
    @click.option('--zip-name', default="output.zip", help="Name of zipfile")
    @click.pass_context
    def download(  # noqa D103
            ctx: click.Context, pattern, exclude_pattern, experiment, simulation, work_item, asset_collection, dry_run,
            wait,
            include_assets, verbose, json, simulation_prefix_format_str, work_item_prefix_format_str, name, output_path,
            delete_after_download,
            extract_after_download, zip_name
    ):
        from idmtools_platform_comps.utils.download.download import DownloadWorkItem

        if json and not dry_run:
            user_logger.error("You cannot return JSON without enabling dry-run mode")
            sys.exit(-1)

        if dry_run and delete_after_download:
            user_logger.warning(
                "You are using dry-run with delete after download. This will most result in an empty file list since "
                "the item will be deleted before the output can be fetched.")

        # ensure no output is enabled when using --json
        if json:
            os.environ['IDMTOOLS_LOGGING_USER_OUTPUT'] = '0'
            os.environ['IDMTOOLS_DISABLE_PROGRESS_BAR'] = '1'

        p: COMPSPlatform = Platform(ctx.obj['config_block'])

        dl_wi = DownloadWorkItem(
            output_path=output_path,
            delete_after_download=delete_after_download,
            extract_after_download=extract_after_download,
            zip_name=zip_name
        )

        if name:
            dl_wi.name = name
        if pattern:
            dl_wi.file_patterns = list(pattern)
        if exclude_pattern:
            dl_wi.exclude_patterns = exclude_pattern if isinstance(exclude_pattern, list) else list(exclude_pattern)

        dl_wi.related_experiments = list(experiment)
        dl_wi.related_simulations = list(simulation)
        dl_wi.related_work_items = list(work_item)
        dl_wi.related_asset_collections = list(asset_collection)
        dl_wi.include_assets = include_assets
        dl_wi.dry_run = dry_run
        dl_wi.verbose = verbose
        if simulation_prefix_format_str is not None:
            if simulation_prefix_format_str.strip() == "":
                dl_wi.no_simulation_prefix = True
            else:
                dl_wi.simulation_prefix_format_str = simulation_prefix_format_str
        if work_item_prefix_format_str is not None:
            dl_wi.work_item_prefix_format_str = work_item_prefix_format_str

        if dl_wi.total_items_watched() == 0:
            user_logger.error("You must specify at least one item to download")

        dl_wi.run(wait_until_done=False, platform=p)
        if not json and not delete_after_download:
            user_logger.info(f"Item can be viewed at {p.get_workitem_link(dl_wi)}")
        if wait:
            dl_wi.wait(wait_on_done_progress=wait)
        if dl_wi.succeeded:
            if dl_wi.dry_run and not delete_after_download:
                file = p.get_files(dl_wi, ['file_list.json'])
                file = file['file_list.json'].decode('utf-8')
                if json:
                    user_logger.info(file)
                else:
                    file = json_parser.loads(file)
                    user_logger.info(tabulate.tabulate([x.values() for x in file], file[0].keys()))
            else:
                pass
        elif dl_wi.failed:
            user_logger.error("Download failed. Check logs in COMPS")
            if dl_wi.failed:
                dl_wi.fetch_error()
            sys.exit(-1)

    @comps.command(help="Allows assetizing outputs from the command line")
    @click.option('--pattern', default=[], multiple=True, help="File patterns")
    @click.option('--exclude-pattern', default=DEFAULT_EXCLUDES, multiple=True, help="File patterns")
    @click.option('--experiment', default=[], multiple=True, help="Experiment ids to assetize")
    @click.option('--simulation', default=[], multiple=True, help="Simulation ids to assetize")
    @click.option('--work-item', default=[], multiple=True, help="WorkItems ids to assetize")
    @click.option('--asset-collection', default=[], multiple=True, help="Asset Collection ids to assetize")
    @click.option('--dry-run/--no-dry-run', default=False,
                  help="Gather a list of files that would be assetized instead of actually assetizing")
    @click.option('--wait/--no-wait', default=True, help="Wait on item to finish")
    @click.option('--include-assets/--no-include-assets', default=False,
                  help="Scan common assets of WorkItems and Experiments when filtering")
    @click.option('--verbose/--no-verbose', default=True, help="Enable verbose output in worker")
    @click.option('--json/--no-json', default=False, help="Outputs File list as JSON when used with dry run")
    @click.option('--simulation-prefix-format-str', default=None,
                  help="Simulation Prefix Format str. Defaults to '{simulation.id}'. For no prefix, pass a empty string")
    @click.option('--work-item-prefix-format-str', default=None, help="WorkItem Prefix Format str. Defaults to ''")
    @click.option('--tag', default=[], type=(str, str), multiple=True,
                  help="Tags to add to the created asset collection as pairs.")
    @click.option('--name', default=None, help="Name of AssetizeWorkitem. If not provided, one will be generated")
    @click.option('--id-file/--no-id-file', default=False, help="Enable or disable writing out an id file")
    @click.option('--id-filename', default=None,
                  help="Name of ID file to save build as. Required when id file is enabled")
    @click.pass_context
    def assetize_outputs(  # noqa D103
            ctx: click.Context, pattern, exclude_pattern, experiment, simulation, work_item, asset_collection, dry_run,
            wait,
            include_assets, verbose, json, simulation_prefix_format_str, work_item_prefix_format_str, tag, name,
            id_file, id_filename
    ):

        if id_file and id_filename is None:
            user_logger.error("--id-filename is required when filename is not provided")
            sys.exit(-1)
        if json:
            os.environ['IDMTOOLS_LOGGING_USER_OUTPUT'] = '0'
            os.environ['IDMTOOLS_DISABLE_PROGRESS_BAR'] = '1'

        p: COMPSPlatform = Platform(ctx.obj['config_block'])
        ao = AssetizeOutput()
        if name:
            ao.name = name
        if pattern:
            ao.file_patterns = list(pattern)
        if exclude_pattern:
            ao.exclude_patterns = exclude_pattern if isinstance(exclude_pattern, list) else list(exclude_pattern)
        ao.related_experiments = list(experiment)
        ao.related_simulations = list(simulation)
        ao.related_work_items = list(work_item)
        ao.related_asset_collections = list(asset_collection)
        ao.include_assets = include_assets
        ao.dry_run = dry_run
        ao.verbose = verbose
        if simulation_prefix_format_str is not None:
            if simulation_prefix_format_str.strip() == "":
                ao.no_simulation_prefix = True
            else:
                ao.simulation_prefix_format_str = simulation_prefix_format_str
        if work_item_prefix_format_str is not None:
            ao.work_item_prefix_format_str = work_item_prefix_format_str
        if tag:
            for name, value in tag:
                ao.asset_tags[name] = value
        if ao.total_items_watched() == 0:
            user_logger.error("You must specify at least one item to assetize")
        ao.run(wait_until_done=False, platform=p)
        if not json:
            user_logger.info(f"Item can be viewed at {p.get_workitem_link(ao)}")
        if wait:
            ao.wait(wait_on_done_progress=wait)
        if ao.succeeded:
            if ao.dry_run:
                file = p.get_files(ao, ['file_list.json'])
                file = file['file_list.json'].decode('utf-8')
                if json:
                    user_logger.info(file)
                else:
                    file = json_parser.loads(file)
                    user_logger.info(tabulate.tabulate([x.values() for x in file], file[0].keys()))
            else:
                if id_file:
                    ao.asset_collection.to_id_file(id_filename)
                if json:
                    result = [i.short_remote_path() for i in ao.asset_collection.assets]
                    user_logger.info(je.dumps(result))
                else:
                    user_logger.info(f"Created {ao.asset_collection.id}")
                    user_logger.info(f"It can be viewed at {p.get_asset_collection_link(ao.asset_collection)}")
                    user_logger.info("Items in Asset Collection")
                    user_logger.info("-------------------------")
                    for asset in ao.asset_collection:
                        user_logger.info(asset.short_remote_path())
        elif ao.failed:
            user_logger.error("Assetized failed. Check logs in COMPS")
            if ao.failed:
                ao.fetch_error()
            sys.exit(-1)

    @comps.command(help="""
        \b
        Create ac from requirement file
        Args:
            asset_tag: tag to be added to ac
            pkg: package name (along with version)
            wheel: package wheel file
        """)
    @click.argument('requirement', type=click.Path(exists=True), required=False)
    @click.option('--asset_tag', multiple=True, help="Tag to be added to AC. Format: 'key:value'")
    @click.option('--pkg', multiple=True, help="Package for override. Format: 'key==value'")
    @click.option('--wheel', multiple=True, help="Local wheel file")
    @click.pass_context
    def req2ac(ctx: click.Context, requirement: str = None, asset_tag: Optional[List[str]] = None,  # noqa D103
               pkg: Optional[List[str]] = None,
               wheel: Optional[List[str]] = None):
        from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection

        pkg_list = list(pkg)
        wheel_list = [os.path.abspath(w) for w in wheel]
        tags = dict()
        for t in asset_tag:
            parts = t.split(':')
            tags[parts[0]] = parts[1]

        p: COMPSPlatform = Platform(ctx.obj['config_block'])
        pl = RequirementsToAssetCollection(p, requirements_path=requirement, pkg_list=pkg_list,
                                           local_wheels=wheel_list, asset_tags=tags)
        ac_id = pl.run()
        print(ac_id)

    @comps.command(help="""
        \b
        Check ac existing based on requirement file
        Args:
            pkg: package name (along with version)
            wheel: package wheel file
        """)
    @click.argument('requirement', type=click.Path(exists=True), required=False)
    @click.option('--pkg', multiple=True, help="Package used for override. Format: say, 'key==value'")
    @click.option('--wheel', multiple=True, help="Local wheel file")
    @click.pass_context
    def ac_exist(ctx: click.Context, requirement: str = None, pkg: Optional[List[str]] = None, wheel: Optional[List[str]] = None):  # noqa D103
        # TODO rename this and move to a subcommand for all the requirements functions
        from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection

        pkg_list = list(pkg)
        wheel_list = [os.path.abspath(w) for w in wheel]
        p: COMPSPlatform = Platform(ctx.obj['config_block'])
        pl = RequirementsToAssetCollection(p, requirements_path=requirement, pkg_list=pkg_list, local_wheels=wheel_list)
        # Check if ac with md5 exists
        ac = pl.retrieve_ac_by_tag()
        if ac:
            print("AC exist: ", ac.id)
        else:
            print("AC doesn't exist")

    @comps.group(help="Singularity commands")
    def singularity():  # noqa D103
        pass

    @singularity.command(help="Build Singularity Image")
    @click.option('--common-input', default=[], multiple=True, help="Files")
    @click.option('--common-input-glob', default=[], multiple=True, help="File patterns")
    @click.option('--transient-input', default=[], multiple=True, help="Transient Files (Paths)")
    @click.option('--transient-input-glob', default=[], multiple=True, help="Transient Files Glob Patterns")
    @click.argument('definition_file')
    @click.option('--wait/--no-wait', default=True, help="Wait on item to finish")
    @click.option('--tag', default=[], type=(str, str), multiple=True,
                  help="Extra Tags as Value Pairs for the Resulting AC")
    @click.option('--workitem-tag', default=[], type=(str, str), multiple=True,
                  help="Extra Tags as Value Pairs for the WorkItem")
    @click.option('--name', default=None, help="Name of WorkItem. If not provided, one will be generated")
    @click.option('--force/--no-force', default=False, help="Force build, ignoring build context")
    @click.option('--image-name', default=None, help="Name of resulting image")
    @click.option('--id-file/--no-id-file', default=True,
                  help="Enable or disable writing out an ID file that points to the created asset collection")
    @click.option('--id-filename', default=None,
                  help="Name of ID file to save build as. If not specified, and id-file is enabled, a name is calculated")
    @click.option('--id-workitem/--no-id-workitem', default=True,
                  help="Enable or disable writing out an id file for the workitem")
    @click.option('--id-workitem-failed/--no-id-workitem-failed', default=False,
                  help="Write id of the workitem even if it failed. You need to enable --id-workitem for this is be active")
    @click.option('--id-workitem-filename', default=None,
                  help="Name of ID file to save workitem to. You need to enable --id-workitem for this is be active")
    @click.pass_context
    def build(ctx: click.Context, common_input, common_input_glob, transient_input, transient_input_glob,  # noqa D103
              definition_file, wait, tag, workitem_tag, name, force, image_name: str,
              id_file: str, id_filename: str, id_workitem: bool, id_workitem_failed: bool, id_workitem_filename: str):
        p: COMPSPlatform = Platform(ctx.obj['config_block'])
        sb = SingularityBuildWorkItem(definition_file=definition_file, name=name, force=force, image_name=image_name)

        if tag:
            for name, value in tag:
                sb.image_tags[name] = value

        if workitem_tag:
            for name, value in tag:
                sb.tags[name] = value

        # Add inputs from files
        for assets, inputs in [(sb.assets, common_input), (sb.transient_assets, transient_input)]:
            for file in inputs:
                add_item(assets, file)

        # And then from glob patterns
        for assets, patterns in [(sb.assets, common_input_glob), (sb.transient_assets, transient_input_glob)]:
            for pattern in patterns:
                for file in glob.glob(pattern):
                    add_item(assets, file)

        sb.run(wait_until_done=wait, platform=p)
        if sb.succeeded and id_file:
            if id_filename is None:
                id_filename = sb.get_id_filename()
            user_logger.info(f"Saving the Asset collection ID that contains the image to {id_filename}")
            sb.asset_collection.to_id_file(id_filename, save_platform=True)
        if id_workitem:
            # TODO when we should use platform id but that need to be updated through the code base
            if sb.succeeded and sb._uid is None:
                user_logger.warning(
                    "Cannot save workitem id because an existing container was found with the same inputs. You can force run using --force, but it is recommended to use the container used.")
            elif id_workitem_failed or sb.succeeded:
                if id_workitem_filename is None:
                    id_workitem_filename = sb.get_id_filename(prefix="builder.")
                user_logger.info(f"Saving the Builder Workitem ID that contains the image to {id_workitem_filename}")
                sb.to_id_file(id_workitem_filename, save_platform=True)
        sys.exit(0 if sb.succeeded else -1)

    @singularity.command(help="Pull Singularity Image")
    @click.argument('image_url')
    @click.option('--wait/--no-wait', default=True, help="Wait on item to finish")
    @click.option('--tag', default=[], type=(str, str), multiple=True,
                  help="Extra Tags as Value Pairs for the Resulting AC")
    @click.option('--workitem-tag', default=[], type=(str, str), multiple=True,
                  help="Extra Tags as Value Pairs for the WorkItem")
    @click.option('--name', default=None, help="Name of WorkItem. If not provided, one will be generated")
    @click.option('--force/--no-force', default=False, help="Force build, ignoring build context")
    @click.option('--image-name', default=None, help="Name of resulting image")
    @click.option('--id-file/--no-id-file', default=True, help="Enable or disable writing out an id file")
    @click.option('--id-filename', default=None,
                  help="Name of ID file to save build as. If not specified, and id-file is enabled, a name is calculated")
    @click.option('--id-workitem/--no-id-workitem', default=True,
                  help="Enable or disable writing out an id file for the workitem")
    @click.option('--id-workitem-failed/--no-id-workitem-failed', default=False,
                  help="Write id of the workitem even if it failed. You need to enable --id-workitem for this is be active")
    @click.option('--id-workitem-filename', default=None,
                  help="Name of ID file to save workitem to. You need to enable --id-workitem for this is be active")
    @click.pass_context
    def pull(ctx: click.Context, image_url, wait, tag, workitem_tag, name, force, image_name: str, id_file: str,  # noqa D103
             id_filename: str,
             id_workitem: bool, id_workitem_failed: bool, id_workitem_filename: str):
        p: COMPSPlatform = Platform(ctx.obj['config_block'])
        sb = SingularityBuildWorkItem(image_url=image_url, force=force, image_name=image_name)
        sb.name = f"Pulling {image_url}" if name is None else name

        if tag:
            for name, value in tag:
                sb.image_tags[name] = value

        if workitem_tag:
            for name, value in tag:
                sb.tags[name] = value

        sb.run(wait_until_done=wait, platform=p)
        if sb.succeeded and id_file:
            if id_filename is None:
                id_filename = sb.get_id_filename()
            user_logger.info(f"Saving ID to {id_filename}")
            sb.asset_collection.to_id_file(id_filename, save_platform=True)

        if id_workitem and sb.succeeded and sb._uid is None:
            user_logger.warning(
                "Cannot save workitem id because an existing container was found with the same inputs. You can force run using --force, but it is recommended to use the container used.")
        elif id_workitem_failed or sb.succeeded:
            if id_workitem_filename is None:
                id_workitem_filename = sb.get_id_filename(prefix="builder.")
            user_logger.info(f"Saving the Builder Workitem ID that contains the image to {id_workitem_filename}")
            sb.to_id_file(id_workitem_filename, save_platform=True)
        sys.exit(0 if sb.succeeded else -1)

except ImportError as e:
    logger.warning(f"COMPS CLI not enabled because a dependency is missing. Most likely it is either click or idmtools cli {e.args}")
