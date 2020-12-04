import os
from logging import getLogger
from typing import TYPE_CHECKING

from idmtools import IdmConfigParser
from idmtools.assets import AssetCollection
from idmtools.core import TRUTHY_VALUES
from idmtools.entities import Suite
from idmtools.registry.hook_specs import function_hook_impl

if TYPE_CHECKING:
    from idmtools.core.interfaces.ientity import IEntity

logger = getLogger(__name__)
user_logger = getLogger('user')


@function_hook_impl
def idmtools_platform_pre_create_item(item: 'IEntity', **kwargs):
    from idmtools.entities.experiment import Experiment
    from idmtools.entities.simulation import Simulation
    from idmtools.entities.iworkflow_item import IWorkflowItem
    if IdmConfigParser.get_option("git_tag", "add_to_all", 'f') in TRUTHY_VALUES or (isinstance(item, Experiment) and IdmConfigParser.get_option("git_tag", "add_to_experiments", 'f') in TRUTHY_VALUES) or \
            (isinstance(item, Simulation) and IdmConfigParser.get_option("git_tag", "add_to_simulations", 'f') in TRUTHY_VALUES) or \
            (isinstance(item, IWorkflowItem) and IdmConfigParser.get_option("git_tag", "add_to_workitems", 'f') in TRUTHY_VALUES) or \
            (isinstance(item, Suite) and IdmConfigParser.get_option("git_tag", "add_to_suite", 'f') in TRUTHY_VALUES) or \
            (isinstance(item, AssetCollection) and IdmConfigParser.get_option("git_tag", "add_to_asset_collection", 'f') in TRUTHY_VALUES):
        success = add_details_using_gitpython(item)
        if not success and not add_details_using_pygit(item):
            user_logger.warning("You need gitpython or pygit2 installed to have this functionality")


def add_details_using_gitpython(item):
    try:
        import git
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        item.tags['git_hash'] = sha
        item.tags['git_url'] = repo.head.remote_head
        if repo.head.tracking_branch():
            item.tags['git_branch'] = repo.head.tracking_branch()
        return True
    except ImportError:
        return False


def add_details_using_pygit(item):
    try:
        import pygit2
        repo_base = pygit2.discover_repository(os.getcwd())
        if repo_base:
            repo = pygit2.Repository(repo_base)
            sha = repo.head.target.hex
            item.tags['git_hash'] = sha
            if len(repo.remotes) > 0:
                item.tags['git_url'] = repo.remotes[0].url
            if repo.head.shorthand:
                item.tags['git_branch'] = repo.head.shorthand
            return True
    except ImportError:
        return False
