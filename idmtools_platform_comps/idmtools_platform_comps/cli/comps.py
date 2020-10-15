from getpass import getpass
import sys
from logging import getLogger
import tabulate
import os
from COMPS.CredentialPrompt import CredentialPrompt
import json as json_parser

logger = getLogger(__name__)
user_logger = getLogger('user')
try:

    class StaticCredentialPrompt(CredentialPrompt):
        def __init__(self, comps_url, username, password):
            if (comps_url is None) or (username is None) or (password is None):
                raise RuntimeError('Missing comps_url, or username or password')
            self._times_prompted = 0
            self.comps_url = comps_url
            self.username = username
            self.password = password

        def prompt(self):
            self._times_prompted = self._times_prompted + 1
            if self._times_prompted > 3:
                raise PermissionError('Failure authenticating')
            return {'Username': self.username, 'Password': self.password}

    os.environ['IDMTOOLS_NO_CONFIG_WARNING'] = '1'
    from idmtools.core.platform_factory import Platform
    import click
    from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput, DEFAULT_EXCLUDES
    from idmtools_platform_comps.comps_platform import COMPSPlatform

    @click.group(help="Commands related to managing the local platform")
    @click.argument('config-block')
    @click.pass_context
    def comps(ctx: click.Context, config_block):
        ctx.obj = dict(config_block=config_block)

    @comps.command(help="Login to COMPS")
    @click.option('--username', required=True, help="Username")
    @click.option('--password', help="Password")
    @click.pass_context
    def login(ctx: click.Context, username, password):
        from COMPS import Client
        from idmtools.core.logging import SUCCESS
        os.environ['IDMTOOLS_SUPPRESS_OUTPUT'] = '1'
        if password:
            user_logger.warning("Password the password via the command line is considered insecure")
        else:
            password = getpass("Password")
        # make platform object to load info from alias or config but don't login
        platform = Platform(ctx.obj['config_block'], _skip_login=True)

        try:
            Client.login(platform.endpoint, StaticCredentialPrompt(comps_url=platform.endpoint, username=username, password=password))
            user_logger.log(SUCCESS, "Login succeeded")
        except PermissionError:
            user_logger.error(f"Could not loging to {platform.endpoint}")
            sys.exit(-1)

    @comps.command(help="Allows assetizing outputs from the command line")
    @click.option('--pattern', default=[], multiple=True, help="File patterns")
    @click.option('--exclude-pattern', default=DEFAULT_EXCLUDES, multiple=True, help="File patterns")
    @click.option('--experiment', default=[], multiple=True, help="Experiment ids to assetize")
    @click.option('--simulation', default=[], multiple=True, help="Simulation ids to assetize")
    @click.option('--work-item', default=[], multiple=True, help="WorkItems ids to assetize")
    @click.option('--asset-collection', default=[], multiple=True, help="Asset Collection ids to assetize")
    @click.option('--dry-run/--no-dry-run', default=False, help="Gather a list of files that would be assetized instead of actually assetizing")
    @click.option('--wait/--no-wait', default=True, help="Wait on item to finish")
    @click.option('--include-assets/--no-include-assets', default=False, help="Scan common assets of WorkItems and Experiments when filtering")
    @click.option('--verbose/--no-verbose', default=True, help="Enable verbose output in worker")
    @click.option('--json/--no-json', default=False, help="Outputs File list as JSON when used with dry run")
    @click.option('--simulation-prefix-format-str', default=None, help="Simulation Prefix Format str. Defaults to '{simulation.id}'. For no prefix, pass a empty string")
    @click.option('--work-item-prefix-format-str', default=None, help="WorfkItem Prefix Format str. Defaults to ''")
    @click.option('--tag', default=[], type=(str, str), multiple=True, help="Tags to add the created asset collection as pairs")
    @click.option('--name', default=None, help="Name of AssetizeWorkitem. If not provided, one will be generated")
    @click.pass_context
    def assetize_outputs(ctx: click.Context, pattern, exclude_pattern, experiment, simulation, work_item, asset_collection, dry_run, wait, include_assets, verbose, json, simulation_prefix_format_str, work_item_prefix_format_str, tag, name):
        from idmtools.utils.info import get_help_version_url
        if json:
            os.environ['IDMTOOLS_SUPPRESS_OUTPUT'] = '1'

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
                user_logger.info(f"Created {ao.asset_collection.id}")
                user_logger.info(f"It can be viewed at {p.get_asset_collection_link(ao.asset_collection)}")
                user_logger.info("Items in Asset Collection")
                user_logger.info("-------------------------")
                for asset in ao.asset_collection:
                    user_logger.info(asset.short_remote_path())
        elif ao.failed:
            user_logger.error("Assetized failed. Check logs in COMPS")
            if ao.failed:
                try:
                    file = p.get_files(ao, ['error_reason.json'])
                    file = file['error_reason.json'].decode('utf-8')
                    file = json_parser.loads(file)
                    user_logger.error(f'Error from server: {file["args"][0]}')
                    if 'doc_link' in file:
                        user_logger.error(get_help_version_url(file['doc_link']))
                    else:
                        user_logger.error(user_logger.error('\n'.join(file['tb'])))
                except Exception as e:
                    logger.exception(e)
            sys.exit(-1)

except ImportError as e:
    logger.warning(f"COMPS CLI not enabled because a dependency is missing. Most likely it is either click or idmtools cli {e.args}")
