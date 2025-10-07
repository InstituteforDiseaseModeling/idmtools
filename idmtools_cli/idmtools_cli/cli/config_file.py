"""Defines the config cli group and commands."""
import configparser
import dataclasses
import os
import re
import click
from click import secho
from colorama import Fore, Style
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools_cli.cli.entrypoint import cli

IGNORED_PLATFORMS = ["Test", "Slurm", "File", "Container", "SSMT", "TestExecute", "Process"]
AVAILABLE_PLATFORMS = PlatformPlugins().get_plugin_map()
for platform in IGNORED_PLATFORMS:
    if platform in AVAILABLE_PLATFORMS:
        del AVAILABLE_PLATFORMS[platform]
HIDDEN_FIELD_REGEX = re.compile('^_.+$')
FIELD_BLACKLIST = ['platform_type_map', 'supported_types', 'plugin_key', 'docker_image']


@cli.group()
@click.option("--config_path", prompt="Path to the idmtools.ini file",
              help="Path to the idmtools.ini file",
              default=os.path.join(os.getcwd(), "idmtools.ini"),
              type=click.Path(dir_okay=False, file_okay=True, exists=False, writable=True, resolve_path=True))
@click.option("--global-config/--no-global-config", default=False, help="Allow generating config in the platform default global location")
@click.pass_context
def config(ctx, config_path, global_config):
    """
    Contains commands related to the creation of idmtools.ini.

    With the config command, you can :
     - Generate an idmtools.ini file in the current directory
     - Add a configuration block
    """
    ctx.ensure_object(dict)
    if global_config:
        from idmtools import IdmConfigParser
        config_path = IdmConfigParser.get_global_configuration_name()

    # Create a config parser and read the file if it exist
    # The comment prefixes and allow_no_value is a truck to keep the comments even while editing
    cp = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    if os.path.exists(config_path):
        cp.read_file(open(config_path))

    # Store the config parser in the context
    ctx.obj["cp"] = cp
    ctx.obj["path"] = config_path


def slugify(value):
    """
    Slugify the option.

    This means upper-casing and replacing spaces with "-"

    Args:
        value: Item to slugify

    Returns:
        Slugified string
    """
    value = value.upper()
    value = value.replace(" ", "_")
    return value


def validate_block_name(context, value):
    """
    Validate if a block name exists, and if so, should we overwrite it.

    Args:
        context: Context object
        value: Value to check

    Returns:
        Slugified value name
    """
    cp = context.obj["cp"]
    value = slugify(value)
    if value in cp.sections():
        secho(f"The {value} block already exists in the selected ini file.", fg="bright_yellow")
        click.confirm(click.style("Do you want to continue and overwrite the existing block?", fg="bright_yellow"), default=False, abort=True)

        # Remove the block from the config parser
        del cp[value]

    context.obj['cp'] = cp

    return value


@config.command()
@click.option("--block_name", prompt="New block name",
              help="Name of the new block in the file",
              callback=lambda c, p, v: validate_block_name(c, v),
              type=click.STRING)
@click.option('--platform', default='COMPS', type=click.Choice(AVAILABLE_PLATFORMS.keys()), prompt="Platform type")
@click.pass_context
def block(ctx, block_name, platform):
    """
    Command to create/replace a block in the selected idmtools.ini.

    Args:
        ctx: Context containing the path of idmtools.ini and the associated configparser
        block_name:  Name of the block to create/replace
        platform:  Selected platform
    """
    config_path = ctx.obj['path']
    print("\n" + Style.BRIGHT + "-" * 50)
    print("idmtools.ini Utility")
    print(f"- INI Location: {config_path}")
    print(f"- Selected block: {block_name}")
    print(f"- Selected platform: {platform}")
    print("-" * 50 + Style.NORMAL + "\n")

    # Retrieve the platform and its associated fields
    platform_obj = AVAILABLE_PLATFORMS[platform]
    fields = dataclasses.fields(platform_obj.get_type())

    # Dictionary to store user choices and field defaults
    # Store both to allow the fields callback functions to access the previous user choices regardless of defaults
    values = {"type": platform}
    defaults = {}

    # Ask about each field
    # The field needs to contain a `help` section in the metadata to be considered
    for field in filter(lambda f: "help" in f.metadata, fields):

        # Display the help message
        print(f"{Fore.CYAN}{field.metadata['help']}{Fore.RESET}")

        # Retrieve the metadata
        md = dict(field.metadata)

        # If a callback exists -> execute it
        if "callback" in md:
            md.update(md["callback"](values, field))

        # Create the default
        field_default = md.get("default", field.default if field.default is not None else '')
        defaults[field.name] = field.default

        # Handle the choices if any
        prompt_type = click.Choice(md["choices"]) if "choices" in md else field.type

        # Retrieve the validation function if any
        if "validate" in md:
            validation = md["validate"]
        else:
            validation = lambda v: (True, None)  # noqa: E731

        # Prompt the user
        while True:
            user_input = click.prompt(field.name, type=prompt_type, default=field_default, prompt_suffix=f": {Fore.GREEN}")

            # Call the validation
            result, msg = validation(user_input)

            # If positive, get out
            if result:
                break

            # Else display the error message
            secho(msg, fg="bright_red")

        # Store the value
        values[field.name] = user_input if user_input != "" else None
        print(Fore.RESET)

    # Remove the default values from the values
    for k, d in defaults.items():
        if values[k] == d:
            del values[k]

    # Display a validation prompt
    print("The following block will be added to the file:\n")
    longest_param = max(len(p) for p in values)
    block_parameters = "\n".join(f"{param.ljust(longest_param)} = {value}" for param, value in values.items())
    block_headers = f"[{block_name}]"
    block = block_headers + "\n" + block_parameters
    secho(f"{block}\n", fg="bright_blue")

    # If we decide to go ahead -> write to file
    if click.confirm("Do you want to write this block to the file?", default=True):
        # First re-write the content of the config parser
        cp = ctx.obj["cp"]
        with open(config_path, 'w') as fp:
            cp.write(fp)
            fp.writelines("\n" + block)

        secho("Block written successfully!", fg="bright_green")
    else:
        secho("Aborted...", fg="bright_red")


if __name__ == '__main__':
    config(["block", '--block_name', 'test'])
