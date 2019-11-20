import click
from idmtools_platform_comps.cli.comps import pass_comps, comps
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.utils.disk_usage import DiskSpaceUsage


@comps.command()
@click.option("--top", default=15, type=int)
@click.argument("users", nargs=-1)
@pass_comps
def disk_usage(platform: COMPSPlatform, users, top):
    DiskSpaceUsage.display(platform, users, top)
