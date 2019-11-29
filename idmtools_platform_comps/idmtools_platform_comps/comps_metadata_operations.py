from dataclasses import dataclass
from typing import NoReturn, Any, List
from uuid import UUID

from COMPS.Data import Suite as COMPSSuite, QueryCriteria, Experiment as COMPSExperiment, Simulation as COMPSSimulation, \
    AssetCollection as COMPSAssetCollection

from idmtools.core import ItemType, EntityContainer
from idmtools.core.experiment_factory import experiment_factory
from idmtools.entities import IExperiment, Suite
from idmtools.entities.iexperiment import StandardExperiment
from idmtools.entities.iplatform import IPlaformMetdataOperations
from idmtools_platform_comps.utils import convert_COMPS_status


@dataclass()
class COMPSMetaDataOperations(IPlaformMetdataOperations):

    def refresh_status(self, item) -> NoReturn:
        if isinstance(item, IExperiment):
            simulations = self.get_children(item.uid, ItemType.EXPERIMENT, force=True, raw=True, cols=["id", "state"],
                                            children=[])
            for s in simulations:
                item.simulations.set_status_for_item(s.id, convert_COMPS_status(s.state))

            return

        raise NotImplementedError("comps_platform.refresh_status only implemented for Experiments")

    def get_platform_item(self, item_id: UUID, item_type: ItemType, **kwargs) -> Any:
        # Retrieve the eventual columns/children arguments
        cols = kwargs.get('columns')
        children = kwargs.get('children')

        self.parent._login()

        if item_type == ItemType.SUITE:
            cols = cols or ["id", "name"]
            children = children if children is not None else ["tags", "configuration"]
            return COMPSSuite.get(id=item_id,
                                  query_criteria=QueryCriteria().select(cols).select_children(children))

        if item_type == ItemType.EXPERIMENT:
            cols = cols or ["id", "name", "suite_id"]
            children = children if children is not None else ["tags", "configuration"]
            return COMPSExperiment.get(id=item_id,
                                       query_criteria=QueryCriteria().select(cols).select_children(children))

        if item_type == ItemType.SIMULATION:
            cols = cols or ["id", "name", "experiment_id", "state"]
            children = children if children is not None else ["tags"]
            return COMPSSimulation.get(id=item_id,
                                       query_criteria=QueryCriteria().select(cols).select_children(children))

        if item_type == ItemType.ASSETCOLLECTION:
            children = children if children is not None else ["assets"]
            return COMPSAssetCollection.get(id=item_id, query_criteria=QueryCriteria().select_children(children))

    def get_children_for_platform_item(self, platform_item: Any, raw: bool = False, **kwargs) -> List[Any]:
        if isinstance(platform_item, COMPSExperiment):
            cols = kwargs.get("cols")
            children = kwargs.get("children")
            cols = cols or ["id", "name", "experiment_id", "state"]
            children = children if children is not None else ["tags"]

            children = platform_item.get_simulations(
                query_criteria=QueryCriteria().select(cols).select_children(children))
            if not raw:
                experiment = self._platform_item_to_entity(platform_item)
                return EntityContainer([self._platform_item_to_entity(s, experiment=experiment) for s in children])
            else:
                return children
        elif isinstance(platform_item, COMPSSuite):
            cols = kwargs.get("cols")
            children = kwargs.get("children")
            cols = cols or ["id", "name", "suite_id"]
            children = children if children is not None else ["tags"]

            children = platform_item.get_experiments(
                query_criteria=QueryCriteria().select(cols).select_children(children))
            if not raw:
                suite = self._platform_item_to_entity(platform_item)
                return EntityContainer([self._platform_item_to_entity(e, suite=suite) for e in children])
            else:
                return children

        return None

    def get_parent_for_platform_item(self, platform_item: Any, raw: bool = False, **kwargs) -> Any:
        if isinstance(platform_item, COMPSExperiment):
            # For experiment -> find the suite
            return self.get_item(platform_item.suite_id, item_type=ItemType.SUITE, raw=raw,
                                 **kwargs) if platform_item.suite_id else None
        if isinstance(platform_item, COMPSSimulation):
            # For a simulation, find the experiment
            return self.get_item(platform_item.experiment_id, item_type=ItemType.EXPERIMENT,
                                 raw=raw, **kwargs) if platform_item.experiment_id else None
        # If Suite return None
        return None

    def _platform_item_to_entity(self, platform_item, **kwargs):
        if isinstance(platform_item, COMPSExperiment):
            # Recreate the suite if needed
            if platform_item.suite_id is None:
                suite = kwargs.get('suite')
            else:
                suite = kwargs.get('suite') or self.get_item(platform_item.suite_id,
                                                             item_type=ItemType.SUITE)

            # Create an experiment
            obj = experiment_factory.create(platform_item.tags.get("type"), tags=platform_item.tags,
                                            name=platform_item.name, fallback=StandardExperiment)

            # Set parent
            obj.parent = suite

            # Set the correct attributes
            obj.uid = platform_item.id
            obj.comps_experiment = platform_item
        elif isinstance(platform_item, COMPSSimulation):
            # Recreate the experiment if needed
            experiment = kwargs.get('experiment') or self.get_item(platform_item.experiment_id,
                                                                   item_type=ItemType.EXPERIMENT)
            # Get a simulation
            obj = experiment.simulation()
            # Set its correct attributes
            obj.uid = platform_item.id
            obj.tags = platform_item.tags
            obj.status = convert_COMPS_status(platform_item.state)
        elif isinstance(platform_item, COMPSSuite):
            # Creat a suite
            obj = Suite()

            # Set its correct attributes
            obj.uid = platform_item.id
            obj.name = platform_item.name
            obj.description = platform_item.description
            obj.tags = platform_item.tags
            obj.comps_suite = platform_item

        # Associate the platform
        obj.platform = self.parent
        return obj
