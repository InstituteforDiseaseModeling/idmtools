import os
import sys

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from idmtools_test.utils.cli import run_command


if __name__ == "__main__":

    platform = Platform('Bayesian')
    wi = SSMTWorkItem(item_name=os.path.split(sys.argv[0])[1], command="anything")
    wi.transient_assets.add_asset(os.path.join("climate", "site_details.csv"))
    wi.load_work_order(os.path.join("climate", "WorkOrder.json"))
    platform.run_items(wi)
    platform.wait_till_done(wi)
    wi_id = wi.id
    print(wi_id)
    # download generated er5 climate files to local "output_er5" folder by download cli util
    result = run_command('comps', 'Bayesian', 'download', '--work-item', wi_id,
                         '--name', 'download_er5_climate', '--output-path', 'output_er5', '--pattern', '**/*.json', '--pattern',
                         '**/*.bin')

