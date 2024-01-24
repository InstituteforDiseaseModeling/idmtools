import os
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import InputDataWorkItem

wi_name = "InputDataWorker sample 1"
sim_id = "b816f387-cb04-eb11-a2c7-c4346bcb1553"
tags = {'SimulationId': sim_id}

if __name__ == "__main__":
    platform = Platform('BELEGOST')
    wi = InputDataWorkItem(name=wi_name, tags=tags)
    wi.load_work_order(os.path.join('..', 'files', 'inputdataworker_workorder.json'))
    wi.run(wait_until_done=True)
