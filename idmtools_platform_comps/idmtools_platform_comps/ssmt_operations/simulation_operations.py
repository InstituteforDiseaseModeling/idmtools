"""idmtools simulation operations for ssmt.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import List, Dict
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.comps_operations.simulation_operations import CompsPlatformSimulationOperations


class SSMTPlatformSimulationOperations(CompsPlatformSimulationOperations):
    """
    SSMTPlatformSimulationOperations provides Simulation operations to SSMT.

    In this case, we only have to redefine get_assets to optimize file usage.
    """

    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get assets for Simulation.

        Args:
            simulation: Simulation to fetch
            files: Files to get
            **kwargs: Any keyword arguments

        Returns:
            Files fetched
        """
        raise NotImplementedError("Fetching files for simulation is not currently implemented for SSMT")
