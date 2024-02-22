from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import VisToolsWorkItem

wi_name = "Vistools sample 1"
# Change to your simulation
sim_id = "7b6ea5c8-d104-eb11-a2c7-c4346bcb1553"
tags = {'SimulationId': sim_id}
node_type = 'Points'
data = {"SimulationId": "" + str(sim_id) + "", "NodesRepresentation": node_type}

if __name__ == "__main__":
    platform = Platform('BELEGOST')
    # wi = VisToolsWorkItem(item_name=wi_name, tags=tags, related_simulations=[sim_id])
    # wi.set_work_order(data)
    # Or directly pass work_order
    wi = VisToolsWorkItem(name=wi_name, tags=tags, work_order=data, related_simulations=[sim_id])
    wi.run(wait_until_done=True)
