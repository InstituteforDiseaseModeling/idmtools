from dataclasses import dataclass, field
from typing import Any, Tuple, List, Dict, Type
from uuid import UUID
from COMPS.Data import Simulation as COMPSSimulation, QueryCriteria, Experiment as COMPSExperiment, SimulationFile, \
    Configuration

from idmtools.core import ItemType
from idmtools.entities import ISimulation
from idmtools.entities.iplatform_metadata import IPlatformSimulationOperations
from idmtools_platform_comps.utils import convert_COMPS_status, get_asset_for_comps_item


@dataclass
class CompsPlatformSimulationOperations(IPlatformSimulationOperations):
    platform: 'COMPSPlaform'
    platform_type: Type = field(default=COMPSSimulation)

    def get(self, simulation_id: UUID, **kwargs) -> COMPSSimulation:
        cols = kwargs.get('columns')
        children = kwargs.get('children')
        cols = cols or ["id", "name", "experiment_id", "state"]
        children = children if children is not None else ["tags", "configuration"]
        return COMPSSimulation.get(id=simulation_id,
                                   query_criteria=QueryCriteria().select(cols).select_children(children))

    def create(self, simulation: ISimulation, **kwargs) -> Tuple[COMPSSimulation, UUID]:
        s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.parent_id,
                            configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))
        self.send_assets(simulation, s)
        s.set_tags(simulation.tags)
        COMPSSimulation.save(s, save_semaphore=COMPSSimulation.get_save_semaphore())
        return s, s.id

    def batch_create(self, sims: List[ISimulation], **kwargs) -> List[Tuple[COMPSSimulation, UUID]]:
        created_simulations = []
        for simulation in sims:
            s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.parent_id,
                                configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))
            simulation._platform_object = s
            self.send_assets(simulation)
            s.set_tags(simulation.tags)
            created_simulations.append(s)
        COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())
        return [(s, s.id) for s in created_simulations]

    def get_parent(self, simulation: Any, **kwargs) -> COMPSExperiment:
        return self.platform._experiments.get(simulation.experiment_id,  **kwargs) if simulation.experiment_id else None

    def run_item(self, simulation: ISimulation):
        pass

    def send_assets(self, simulation: ISimulation, comps_sim: COMPSSimulation = None):
        if comps_sim is None:
            comps_sim = simulation.get_platform_object()
        for asset in simulation.assets:
            comps_sim.add_file(simulationfile=SimulationFile(asset.filename, 'input'),  data=asset.bytes)

    def refresh_status(self, simulation: ISimulation):
        s = COMPSSimulation.get(id=simulation.uid, query_criteria=QueryCriteria().select(['state']))
        simulation.status = convert_COMPS_status(s.state)

    def to_entity(self, simulation: Any, **kwargs) -> ISimulation:
        # Recreate the experiment if needed
        experiment = kwargs.get('experiment') or self.platform.get_item(simulation.experiment_id,
                                                                        item_type=ItemType.EXPERIMENT)
        # Get a simulation
        obj = experiment.simulation()
        # Set its correct attributes
        obj.uid = simulation.id
        obj.tags = simulation.tags
        obj.status = convert_COMPS_status(simulation.state)
        return obj

    def get_assets(self, simulation: ISimulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        return get_asset_for_comps_item(self.platform, simulation, files, self.cache)

    def list_assets(self, simulation: ISimulation) -> List[str]:
        comps_sim: COMPSSimulation = simulation.get_platform_object(True, children=["files", "configuration"])
        return comps_sim.files


