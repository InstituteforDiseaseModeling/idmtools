from logging import getLogger
from idmtools import IdmConfigParser
from idmtools.assets import AssetCollection
from idmtools.entities import Suite
from idmtools.registry.hook_specs import pre_create_item_impl

logger = getLogger(__name__)
user_logger = getLogger('user')


@pre_create_item_impl
def git_add_tag(item: 'IEntity', **kwargs):
    from idmtools.entities.experiment import Experiment
    from idmtools.entities.simulation import Simulation
    from idmtools.entities.iworkflow_item import IWorkflowItem
    if IdmConfigParser.get_option("git_tag", "add_to_all", False) or (isinstance(item, Experiment) and IdmConfigParser.get_option("git_tag", "add_to_experiments", False)) or \
            (isinstance(item, Simulation) and IdmConfigParser.get_option("git_tag", "add_to_simulations", False)) or \
            (isinstance(item, IWorkflowItem) and IdmConfigParser.get_option("git_tag", "add_to_workitems", False)) or \
            (isinstance(item, Suite) and IdmConfigParser.get_option("git_tag", "add_to_suite", False)) or \
            (isinstance(item, AssetCollection) and IdmConfigParser.get_option("git_tag", "add_to_asset_collection", False)):
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            sha = repo.head.object.hexsha
            item.tags['git_hash'] = sha
            item.tags['git_url'] = repo.head.remote_head
            if repo.head.tracking_branch():
                item.tags['git_branch'] = repo.head.tracking_branch()
        except ImportError:
            user_logger.warning("You need gitpython installed to have this functionality")


from idmtools.registry.functions import FunctionPluginManager

pl = FunctionPluginManager()
pl.register(git_add_tag)
pl.hook.pre_create_item_spec(None)
