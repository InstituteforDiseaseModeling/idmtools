

# https://prod-81.westus.logic.azure.com:443/workflows/4810212b690b457f90bb9eb287261735/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ViHXsdtZqaVnUQS-j3uqPNgWKO1DkbQrg_QgMXA-jw4
import os
from collections import defaultdict
from logging import getLogger

from idmtools.assets.file_list import FileList
from idmtools_platform_comps.utils.notifiers.utils import parse_relation

user_logger = getLogger('user')


def notify_microsoft_flow_when_done(items, message, title=None, url=None) -> 'SSMTWorkItem':  # noqa: F821
    from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
    command = f"python microsoft_flow.py --url '{url}' --message '{message}'"
    if title:
        command += f" --title '{title}'"
    extra_args = defaultdict(list)
    name = "Notify Microsoft Flow"

    if isinstance(items, list):
        for sub_item in items:
            parse_relation(extra_args, sub_item)

    else:
        parse_relation(extra_args, items)
        name = f"Notify Microsoft Flow on {items.name}" if getattr(items, 'name', None) else ""

    files = FileList()
    current_dir = os.path.dirname(__file__)
    files.add_file(os.path.join(current_dir, "deploy_scripts", "microsoft_flow.py"))

    wi = SSMTWorkItem(
        item_name=f"Notify Microsoft Flow on {name}",
        command=command,
        user_files=files,
        **extra_args)
    wi.run()

    return wi