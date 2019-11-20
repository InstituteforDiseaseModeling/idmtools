import itertools
import logging
import os
from logging import getLogger
import urllib.request, json
from typing import NoReturn

from idmtools.config import IdmConfigParser
from idmtools.registry.plugin_specification import ProjectTemplate
from idmtools_cli.cli import cli

logger = getLogger(__name__)


@cli.group(help="Commands to help start or extend projects through templating.")
def init():
    pass


def define_cookiecutter_project_command(project_details: ProjectTemplate):

    @init.command(name=project_details.name, help=project_details.description)
    def run_project():
        from cookiecutter.main import cookiecutter
        if not isinstance(project_details.url, list):
            project_details.url = [project_details.url]
        for url in project_details.url:
            cookiecutter(url)

    return run_project


def build_project_list() -> NoReturn:
    """
    Build a list of cookie cutter options for menu
    Returns:

    """
    from idmtools.registry.model_specification import ModelPlugins
    from idmtools.registry.platform_specification import PlatformPlugins

    # fetch
    items = list()
    f_dir = os.path.dirname(__file__)
    with open(os.path.join(f_dir, 'common_project_templates.json'), 'rb') as fin:
        read_templates_from_json_stream(items, fin)
    for pm in [ModelPlugins().get_plugins(), PlatformPlugins().get_plugins()]:
        items.extend(list(itertools.chain(*map(lambda pl: pl.get_project_templates(), pm))))

    # check for values in config
    url = IdmConfigParser.get_option('Templating', 'url')
    if url:
        logger.debug(f'Loading templates from url: {url}')
        with urllib.request.urlopen(url) as s:
            read_templates_from_json_stream(items, s)
    result = {x.name: x for x in items}

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f'Cookie cutter project list: {result}')

    # Now define all the cookie cutter projects
    for name, details in result.items():
        define_cookiecutter_project_command(details)


def read_templates_from_json_stream(items, s):
    data = json.loads(s.read().decode())
    for item in data:
        items.append(ProjectTemplate(**item))
