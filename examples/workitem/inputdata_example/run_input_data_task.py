import os
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import InputDataWorkItem

wi_name = "InputDataWorker sample 1"
sim_id = "8db8ae8f-793c-ea11-a2be-f0921c167861"
tags = {'SimulationId': sim_id}

if __name__ == "__main__":
    platform = Platform('COMPS2')
    wi = InputDataWorkItem(item_name=wi_name, tags=tags)
    wi.load_work_order(os.path.join('..', 'files', 'inputdataworker_workorder.json'))
    wi.run(wait_on_done=True)
