import click

from idmtools_cli.IPlatformCli import IPlatformCLI

# Decorator for CLI functions that will require a platform object passed down to them
pass_platform_cli = click.make_pass_decorator(IPlatformCLI)


@click.group()
def cli():
    """
    Allows you to perform multiple idmtools commands

    """
    pass
