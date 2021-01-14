from logging import getLogger
import click
from typing import Optional, List
from idmtools_cli.cli.entrypoint import cli

user_logger = getLogger('user')


@cli.group(short_help="Contains commands related to package versions")
def pkg():
    pass


@pkg.command()
@click.option('--name', required=True, type=str, help="package name")
def latest(name: Optional[str]):
    """
    \b
    Display all idmtools available examples
    Args:
        name: package name
    """
    from idmtools_platform_comps.utils.package_version import get_latest_version
    v = get_latest_version(name)
    print(v)


@pkg.command()
@click.option('--name', required=True, type=str, help="package name")
@click.option('--base_version', required=True, default=None, type=str, help="package version")
def compatible(name: Optional[str], base_version: Optional[str]):
    """
    \b
    Display all idmtools available examples
    Args:
        name: package name
        base_version: package version
    """
    from idmtools_platform_comps.utils.package_version import get_latest_compatible_version
    v = get_latest_compatible_version(name, base_version)
    print(v)


@pkg.command()
@click.option('--name', required=True, type=str, help="package name")
@click.option('--all', type=bool, default=True, help="package version")
def view(name: Optional[str], all: Optional[bool]):
    """
    \b
    Display all idmtools available examples
    Args:
        name: package name
        all: True/False - return all or only released versions
    """
    from idmtools_platform_comps.utils.package_version import fetch_package_versions
    versions = fetch_package_versions(name, all)
    print(versions)


@pkg.command(help="Build Updated_Requirements from requirement file")
@click.argument('requirement')
@click.option('--tag', multiple=True, help="Tag to be added to AC. Format: 'key:value'")
@click.option('--pkg', multiple=True, help="Package for override. Format: 'key==value'")
@click.option('--wheel', multiple=True, help="Local wheel file")
def updated_requirements(requirement, tag: Optional[List[str]], pkg: Optional[List[str]], wheel: Optional[List[str]]):
    from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
        RequirementsToAssetCollection

    tags, pkg_list, wheel_list = _validate_inputs(tag, pkg, wheel)
    pl = RequirementsToAssetCollection(None, requirements_path=requirement, pkg_list=pkg_list,
                                       local_wheels=wheel_list, tags=tags)
    pl.save_updated_requirements()
    req = open('requirements_updated.txt').read()
    print(req)


@pkg.command(help="Construct checksum from requirement file")
@click.argument('requirement')
@click.option('--tag', multiple=True, help="Tag to be added to AC. Format: 'key:value'")
@click.option('--pkg', multiple=True, help="Package for override. Format: 'key==value'")
@click.option('--wheel', multiple=True, help="Local wheel file")
def checksum(requirement, tag: Optional[List[str]], pkg: Optional[List[str]], wheel: Optional[List[str]]):
    from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
        RequirementsToAssetCollection

    tags, pkg_list, wheel_list = _validate_inputs(tag, pkg, wheel)
    pl = RequirementsToAssetCollection(None, requirements_path=requirement, pkg_list=pkg_list,
                                       local_wheels=wheel_list, tags=tags)
    print(pl.checksum)


def _validate_inputs(tag_list, pkg_list, wheel_list):
    tags = dict()
    for t in tag_list:
        parts = t.split(':')
        tags[parts[0]] = parts[1]

    pkg_list = list(pkg_list)
    wheel_list = [os.path.abspath(w) for w in wheel_list]

    return tags, pkg_list, wheel_list
