import os
from collections import defaultdict
from logging import getLogger
from typing import List, Dict

from idmtools.assets.file_list import FileList
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation

user_logger = getLogger('user')


def parse_relation(extra_args: Dict[str, List], item):
    from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
    if isinstance(item, Experiment):
        extra_args['related_experiments'].append(item.id)
    elif isinstance(item, Suite):
        extra_args['related_suites'].append(item.id)
    elif isinstance(item, Simulation):
        extra_args['related_simulations'].append(item.id)
    elif isinstance(item, SSMTWorkItem):
        extra_args['related_work_items'].append(item.id)


def notify_pushover_when_done(items, message, title=None, token=None, user=None) -> 'SSMTWorkItem':  # noqa: F821
    from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
    user_token = token
    user = user
    command = f"python pushover_script.py --token {user_token} --user-key {user} --message '{message}'"
    if title:
        command += f" --title '{title}'"
    extra_args = defaultdict(list)
    name = "Notify Pushover"
    if isinstance(items, list):
        for sub_item in items:
            parse_relation(extra_args, sub_item)

    else:
        parse_relation(extra_args, items)
        name = f"Notify Pushover on {items.name}" if getattr(items, 'name', None) else ""

    files = FileList()
    current_dir = os.path.dirname(__file__)
    files.add_file(os.path.join(current_dir, "pushover_script.py"))
    # add pushover client
    try:
        import pushover
    except ImportError:
        user_logger.error("You are missing the pushover plugin. Please install manually using\n"
                          "pip install python-pushover\n"
                          "or reinstall idmtools-platform-comps using\n"
                          "pip install idmtools-platform-comps[pushover]")
        # TODO: Should we fail or gracefully ignore?
        return None

    files.add_file(pushover.__file__)

    wi = SSMTWorkItem(
        item_name=f"Notify Pushover on {name}",
        command=command,
        user_files=files,
        **extra_args)
    wi.run()

    return wi
