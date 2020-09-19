from logging import getLogger, DEBUG

from typing import List, Dict
from COMPS.Data import Simulation as COMPSSimulation
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.comps_operations.simulation_operations import CompsPlatformSimulationOperations
from idmtools_platform_comps.utils.general import get_asset_for_comps_item

logger = getLogger(__name__)
user_logger = getLogger('user')


class SSMTPlatformSimulationOperations(CompsPlatformSimulationOperations):
    def get_assets(self, simulation: Simulation, files: List[str], include_experiment_assets: bool = True, **kwargs) -> Dict[str, bytearray]:
        """
        Fetch the files associated with a simulation

        Args:
            simulation: Simulation
            files: List of files to download
            include_experiment_assets: Should we also load experiment assets?
            **kwargs:

        Returns:
            Dictionary of filename -> ByteArray
        """
        # We need to load hpc jobs and configuration here
        comps_sim: COMPSSimulation = simulation.get_platform_object(load_children=["files", "configuration", "hpc_jobs"])
        if include_experiment_assets and (comps_sim.configuration is None or comps_sim.configuration.asset_collection_id is None):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Gathering assets from experiment first")
            exp_assets = get_asset_for_comps_item(self.platform, simulation.experiment, files, self.cache, load_children=["configuration", "hpc_jobs"])
            if exp_assets is None:
                exp_assets = dict()
        else:
            exp_assets = dict()
        exp_assets.update(get_asset_for_comps_item(self.platform, simulation, files, self.cache, comps_item=comps_sim))
        return exp_assets
