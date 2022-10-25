"""idmtools CompsWorkOrderTask.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from idmtools.assets import AssetCollection
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.ssmt_work_items.work_order import IWorkOrder


@dataclass
class CompsWorkOrderTask(ITask):
    """
    Defines a task that is purely work order driven, like Singularity build.
    """
    work_order: IWorkOrder = field(default=None)

    def gather_common_assets(self) -> AssetCollection:
        """Gather common assets."""
        pass

    def gather_transient_assets(self) -> AssetCollection:
        """Gather transient assets."""
        pass

    def reload_from_simulation(self, simulation: Simulation):
        """Reload simulation."""
        pass
