import click

from idmtools.entities.IPlatformCli import IPlatformCLI

pass_platform_cli = click.make_pass_decorator(IPlatformCLI)


@click.group()
def cli():
    """
    Allows you to perform multiple idmtools commands

    """
    pass