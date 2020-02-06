from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.idm_work_item import VisToolsWorkItem

wi_name = "Vistools sample 1"
# Change to your simulation
sim_id = "e4c4c425-7747-ea11-a2be-f0921c167861"
tags = {'SimulationId': sim_id}
node_type = 'Points'
data = {"SimulationId": "" + str(sim_id) + "", "NodesRepresentation": node_type}

if __name__ == "__main__":
    platform = Platform('COMPS2')
    # wi = VisToolsWorkItem(item_name=wi_name, tags=tags, related_simulations=[sim_id])
    # wi.set_work_order(data)
    # Or directly pass work_order
    wi = VisToolsWorkItem(item_name=wi_name, tags=tags, work_order=data, related_simulations=[sim_id])

    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)
