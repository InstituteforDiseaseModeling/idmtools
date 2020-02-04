from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem

wi_name = "Vistools sample 2"
# Change to your simulation
sim_id = "e4c4c425-7747-ea11-a2be-f0921c167861"
tags = {'SimulationId': sim_id}
node_type = 'Points'
data = {"WorkItem_Type": "VisTools", "SimulationId": "" + str(sim_id) + "", "NodesRepresentation": node_type}

if __name__ == "__main__":
    platform = Platform('COMPS2')
    # wi = SSMTWorkItem(item_name=wi_name, tags=tags, work_item_type='VisTools', related_simulations=[sim_id])
    # wi.set_work_order(data)
    # Or directly pass work_order
    wi = SSMTWorkItem(item_name=wi_name, tags=tags, work_item_type='VisTools', work_order=data,
                      related_simulations=[sim_id])

    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)
