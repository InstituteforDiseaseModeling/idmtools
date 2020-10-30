from dataclasses import dataclass, field
from idmtools.assets import AssetCollection
from idmtools.entities.itask import ITask
from idmtools_platform_comps.ssmt_work_items.work_order import IWorkOrder


@dataclass
class CompsWorkOrderTask(ITask):
    work_order: IWorkOrder = field(default=None)

    def gather_common_assets(self) -> AssetCollection:
        pass

    def gather_transient_assets(self) -> AssetCollection:
        pass

    def reload_from_simulation(self, simulation: 'Simulation'):
        pass
