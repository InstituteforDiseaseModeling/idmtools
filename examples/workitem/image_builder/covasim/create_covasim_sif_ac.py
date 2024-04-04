import os
import sys

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import InputDataWorkItem


if __name__ == "__main__":
    platform = Platform('CALCULON')
    wi = InputDataWorkItem(name=os.path.split(sys.argv[0])[1], tags={'idmtools': 'ImageBuilderWorker'}, work_item_type="ImageBuilderWorker")
    wi.load_work_order(os.path.join('inputs', 'covasim_wo.json'))
    wi.run(wait_until_done=True)