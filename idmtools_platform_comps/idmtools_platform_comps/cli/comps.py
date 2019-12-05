import click

from idmtools.core.platform_factory import Platform
from idmtools_cli.cli import cli
from idmtools_platform_comps.comps_platform import COMPSPlatform

pass_comps = click.make_pass_decorator(COMPSPlatform)


@cli.group(help="Commands related to managing the local platform")
@click.option('--config-block', help="COMPS Configuration block to use")
@click.pass_context
def comps(ctx, config_block):
    ctx.obj = Platform(config_block)
