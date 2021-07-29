# Example shows how to use WorkOrder.json to create SSMTWorkItem for generating ER5 climate data
# In SSMTWorkItem, you still need to pass command, but it will be override its value in WorkOrder.json
# custom docker image and AddtionalMounts can be also defined in WorkOrder.json

import os
import sys

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from idmtools_test.utils.cli import run_command


if __name__ == "__main__":

    platform = Platform('Bayesian')
    wi = SSMTWorkItem(item_name=os.path.split(sys.argv[0])[1], command="anything")
    # upload site_details.csv to workitem's root dir in COMPS
    wi.transient_assets.add_asset(os.path.join("climate", "site_details.csv"))
    # upload WorkOrder.json to workitem's root dir in COMPS
    wi.load_work_order(os.path.join("climate", "WorkOrder.json"))
    wi.run(wait_on_done=True)
    wi_id = wi.id
    print(wi_id)
    # download generated er5 climate files to local "output_er5" folder by download cli util
    result = run_command('comps', 'Bayesian', 'download', '--work-item', wi_id,
                         '--name', 'download_er5_climate', '--output-path', 'output_er5', '--pattern', '**/*.json', '--pattern',
                         '**/*.bin')
