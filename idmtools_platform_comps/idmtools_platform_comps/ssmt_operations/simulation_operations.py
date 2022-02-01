"""idmtools simulation operations for ssmt.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from uuid import UUID
from typing import List, Dict, Optional
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.comps_operations.simulation_operations import CompsPlatformSimulationOperations
from COMPS.Data.Simulation import Simulation as COMPSSimulation
from COMPS.Data import QueryCriteria
from logging import getLogger, DEBUG

logger = getLogger(__name__)


class SSMTPlatformSimulationOperations(CompsPlatformSimulationOperations):
    """
    SSMTPlatformSimulationOperations provides Simulation operations to SSMT.

    In this case, we only have to redefine get_assets to optimize file usage.
    """

    def get(self, simulation_id: UUID, columns: Optional[List[str]] = None, load_children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> COMPSSimulation:
        """
        Get Simulation from Comps.

        Args:
            simulation_id: ID
            columns: Optional list of columns to load. Defaults to "id", "name", "experiment_id", "state"
            load_children: Optional children to load. Defaults to "tags", "configuration"
            query_criteria: Optional query_criteria object to use your own custom criteria object
            **kwargs:

        Returns:
            COMPSSimulation
        """
        # ensure hpc_jobs is in children
        if load_children:
            load_children.append('hpc_jobs')
        # when query criteria is specified, we need to ensure our desired criteria are followed
        elif query_criteria is not None:
            if 'hpc_jobs' not in query_criteria._children:
                query_criteria._children.append('hpc_jobs')
        else:
            load_children = ['hpc_jobs']

        return super().get(simulation_id, load_children=load_children, query_criteria=query_criteria)

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
        files = [f.replace("\\", '/') for f in files]
        po: COMPSSimulation = simulation.get_platform_object(load_children=["files", "configuration", "hpc_jobs"])
        working_directory = po.hpc_jobs[0].working_directory
        results = dict()
        for file in files:
            full_path = os.path.join(working_directory, file)
            full_path = full_path.replace("\\", '/')
            if not os.path.exists(full_path):
                msg = f"Cannot find the file {file} at {full_path}"
                logger.error(msg)
                raise FileNotFoundError(msg)
            if logger.isEnabledFor(DEBUG):
                logger.debug(full_path)
            with open(full_path, 'rb') as fin:
                results[file] = fin.read()
        return results
