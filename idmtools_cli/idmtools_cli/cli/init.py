"""Defines the init(templates) cli command."""
import itertools
import json
import logging
import os
import urllib.request
from logging import getLogger
from typing import Dict, List
from idmtools.config import IdmConfigParser
from idmtools.registry.plugin_specification import ProjectTemplate
from idmtools_cli.cli.entrypoint import cli

logger = getLogger(__name__)


@cli.group(help="Commands to help start or extend projects through templating.")
def init():
    """Base init group command."""
    pass


@cli.command(help="Export list of project templates")
def init_export():
    """Export project templates."""
    with open('templates.json', 'w') as o:
        import dataclasses
        result = get_project_list()
        result = {x: dataclasses.asdict(v) for x, v in result.items()}
        json.dump(result, o)


def define_cookiecutter_project_command(project_details: ProjectTemplate):
    """
    Defines the specific project cookie cutter command.

    Args:
        project_details:

    Returns:
        Define a dynamic cookie cutter command around a template
    """

    @init.command(name=project_details.name, help=project_details.description)
    def run_project():
        from cookiecutter.main import cookiecutter
        if not isinstance(project_details.url, list):
            project_details.url = [project_details.url]
        for url in project_details.url:
            cookiecutter(url)

    return run_project


def get_project_list() -> Dict[str, ProjectTemplate]:
    """
    Build a list of cookie cutter options for menu.

    Returns:
        Return list of project templates
    """
    from idmtools.registry.experiment_specification import ExperimentPlugins
    from idmtools.registry.platform_specification import PlatformPlugins

    # fetch
    items = list()
    f_dir = os.path.dirname(__file__)
    with open(os.path.join(f_dir, 'common_project_templates.json'), 'rb') as fin:
        items.extend(ProjectTemplate.read_templates_from_json_stream(fin))

    for pm in [ExperimentPlugins().get_plugins(), PlatformPlugins().get_plugins()]:
        items.extend(list(itertools.chain(*map(lambda pl: pl.get_project_templates(), pm))))

    # check for values in config
    url = IdmConfigParser.get_option('Templating', 'url')
    if url:
        logger.debug(f'Loading templates from url: {url}')
        with urllib.request.urlopen(url) as s:
            items.extend(ProjectTemplate.read_templates_from_json_stream(s))
    result = {x.name: x for x in items}

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f'Cookie cutter project list: {result}')

    return result


def build_project_commands():
    """
    Builds the cookie cutter cli commands.

    Returns:
        None
    """
    result = get_project_list()
    # Now define all the cookie cutter projects
    for _name, details in result.items():
        define_cookiecutter_project_command(details)


def read_templates_from_json_stream(items: List[ProjectTemplate], s):
    """
    Read Project Template from stream onto the list.

    Args:
        items: List to append data to
        s: Stream where json data resides

    Returns:
        None
    """
    data = json.loads(s.read().decode())
    for item in data:
        items.append(ProjectTemplate(**item))
