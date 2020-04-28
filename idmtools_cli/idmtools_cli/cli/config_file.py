import configparser
import dataclasses
import os
import re

import click
from click import secho
from colorama import Fore, Style

from idmtools.registry.platform_specification import PlatformPlugins
from idmtools_cli.cli.entrypoint import cli

IGNORED_PLATFORMS = ["Test"]
AVAILABLE_PLATFORMS = PlatformPlugins().get_plugin_map()
for platform in IGNORED_PLATFORMS:
    del AVAILABLE_PLATFORMS[platform]
HIDDEN_FIELD_REGEX = re.compile('^_.+$')
FIELD_BLACKLIST = ['platform_type_map', 'supported_types', 'plugin_key', 'docker_image']


@cli.group()
@click.option("--config_path", prompt="Path to the idmtools.ini file",
              help="Path to the idmtools.ini file",
              default=os.path.join(os.getcwd(), "idmtools.ini"),
              type=click.Path(dir_okay=False, file_okay=True, exists=False, writable=True, resolve_path=True))
@click.pass_context
def config(ctx, config_path):
    """
    Contains commands related to the creation of idmtools.ini for your project.

    With the config command, you can :
     - Generate an idmtools.ini file in the current directory
     - Add a configuration block
    """
    ctx.ensure_object(dict)
    print('-' * 30)
    print(Style.BRIGHT + "idmtools.ini Utility" + Style.NORMAL)
    print(f"- INI Location: {config_path}")
    print('-' * 30)

    # Create a config parser and read the file if it exist
    # The comment prefixes and allow_no_value is a truck to keep the comments even while editing
    cp = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    if os.path.exists(config_path):
        cp.read_file(open(config_path))

    # Store the config parser in the context
    ctx.obj["cp"] = cp
    ctx.obj["path"] = config_path


def slugify(value):
    value = value.upper()
    value = value.replace(" ", "_")
    return value


def validate_block_name(context, value):
    cp = context.obj["cp"]
    value = slugify(value)
    if value in cp.sections():
        secho(f"The {value} block already exists in the selected ini file.", fg="bright_yellow")
        click.confirm(click.style("Do you want to continue and overwrite the existing block?",fg="bright_yellow"),
                      default=False, abort=True)

        # Remove the block from the config parser
        del cp[value]

    context.obj['cp'] = cp

    return value


@config.command()
@click.option("--block_name", prompt="New block name",
              help="Name of the new block in the file",
              callback=lambda c, p, v: validate_block_name(c, v),
              type=click.STRING)
@click.option('--platform', default=None, type=click.Choice(AVAILABLE_PLATFORMS.keys()), prompt="Platform type")
@click.pass_context
def block(ctx, block_name, platform):
    secho(f"[{block_name}] block for platform {platform}", fg="bright_white")

    # Retrieve the platform and its associated fields
    platform_obj = AVAILABLE_PLATFORMS[platform]
    fields = dataclasses.fields(platform_obj.get_type())

    # Dictionary to store user choices
    values = {"type": platform}

    # Ask about each field
    for field in fields:
        # If the field does not include a help text, skip it
        if "help" not in field.metadata:
            continue

        # Display the help message
        print(f"{Fore.CYAN}{field.metadata['help']}{Fore.RESET}")

        # Create the default
        field_default = field.default if field.default is not None else "None"

        # Handle the choices if any
        if "choices" in field.metadata:
            prompt_type = click.Choice(field.metadata["choices"])
        else:
            prompt_type = field.type

        user_input = click.prompt(field.name, type=prompt_type, default=field_default)
        if user_input != field_default:
            values[field.name] = user_input

    # Display a validation prompt
    print("-" * 30)
    print("The following block will be added to the file:")
    longest_param = max(len(p) for p in values)
    block_parameters = "\n".join(f"{param.ljust(longest_param)} = {value}" for param, value in values.items())
    block_headers = f"[{block_name}]"
    block = block_headers + "\n" + block_parameters
    secho(f"{block}", fg="bright_yellow")

    # If we decide to go ahead -> write to file
    if click.confirm("Do you want to write this block to the file?", default=True):
        # First re-write the content of the config parser
        cp = ctx.obj["cp"]
        with open(ctx.obj["path"], 'w') as fp:
            cp.write(fp)
            fp.writelines("\n" + block)

        secho("Block written successfully!", fg="bright_green")
    else:
        secho("Aborted...", fg="bright_red")
