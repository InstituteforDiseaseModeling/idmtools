import os
from dataclasses import dataclass, field
from typing import Any, List, Tuple, Type
from uuid import UUID
from COMPS.Data import Experiment as COMPSExperiment, QueryCriteria, AssetCollection as COMPSAssetCollection, \
    AssetCollectionFile, Configuration
from idmtools.core import ItemType
from idmtools.core.experiment_factory import experiment_factory
from idmtools.entities import IExperiment
from idmtools.entities.iexperiment import StandardExperiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.utils.time import timestamp
from idmtools_platform_comps.utils.general import clean_experiment_name, convert_COMPS_status


@dataclass
class CompsPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=COMPSExperiment)

    def get(self, experiment_id: UUID, **kwargs) -> COMPSExperiment:
        cols = kwargs.get('columns')
        children = kwargs.get('children')
        cols = cols or ["id", "name", "suite_id"]
        children = children if children is not None else ["tags", "configuration"]
        return COMPSExperiment.get(id=experiment_id,
                                   query_criteria=QueryCriteria().select(cols).select_children(children))

    def platform_create(self, experiment: IExperiment, **kwargs) -> Tuple[COMPSExperiment, UUID]:
        if not self.platform.is_supported_experiment(experiment):
            raise ValueError("The specified experiment is not supported on this platform")

        # Cleanup the name
        experiment_name = clean_experiment_name(experiment.name)

        # Define the subdirectory
        subdirectory = experiment_name[0:self.platform.MAX_SUBDIRECTORY_LENGTH] + '_' + timestamp()

        config = Configuration(
            environment_name=self.platform.environment,
            simulation_input_args=experiment.command.arguments + " " + experiment.command.options,
            working_directory_root=os.path.join(self.platform.simulation_root, subdirectory).replace('\\', '/'),
            executable_path=experiment.command.executable,
            node_group_name=self.platform.node_group,
            maximum_number_of_retries=self.platform.num_retires,
            priority=self.platform.priority,
            min_cores=self.platform.num_cores,
            max_cores=self.platform.num_cores,
            exclusive=self.platform.exclusive
        )

        e = COMPSExperiment(name=experiment_name,
                            configuration=config,
                            suite_id=experiment.parent_id)

        # Add tags if present
        if experiment.tags:
            e.set_tags(experiment.tags)

        # Save the experiment
        e.save()

        # Set the ID back in the object
        experiment.uid = e.id

        # Send the assets for the experiment
        self.send_assets(experiment)
        return e, experiment.uid

    def get_children(self, experiment: COMPSExperiment, **kwargs) -> List[Any]:
        cols = kwargs.get("cols")
        children = kwargs.get("children")
        cols = cols or ["id", "name", "experiment_id", "state"]
        children = children if children is not None else ["tags"]

        children = experiment.get_simulations(query_criteria=QueryCriteria().select(cols).select_children(children))
        return children

    def get_parent(self, experiment: COMPSExperiment, **kwargs) -> Any:
        if experiment.suite_id is None:
            return None
        return self.platform._suites.get(experiment.suite_id, **kwargs)

    def run_item(self, experiment: IExperiment):
        experiment.get_platform_object().commission()

    def send_assets(self, experiment: IExperiment):
        if experiment.assets.count == 0:
            return

        ac, aid = self.platform._assets.create(experiment.assets)
        print("Asset collection for experiment: {}".format(ac.id))

        # associate the assets with the experiment in COMPS
        e = COMPSExperiment.get(id=experiment.uid)
        e.configuration = Configuration(asset_collection_id=ac.id)
        e.save()

    def refresh_status(self, experiment: IExperiment):
        simulations = self.get_children(experiment.get_platform_object(), force=True, cols=["id", "state"], children=[])
        for s in simulations:
            experiment.simulations.set_status_for_item(s.id, convert_COMPS_status(s.state))

    def to_entity(self, experiment: COMPSExperiment, **kwargs) -> IExperiment:
        # Recreate the suite if needed
        if experiment.suite_id is None:
            suite = kwargs.get('suite')
        else:
            suite = kwargs.get('suite') or self.platform.get_item(experiment.suite_id, item_type=ItemType.SUITE)

        # Create an experiment
        obj = experiment_factory.create(experiment.tags.get("type"), tags=experiment.tags, name=experiment.name,
                                        fallback=StandardExperiment)

        # Set parent
        obj.parent = suite

        # Set the correct attributes
        obj.uid = experiment.id
        obj.comps_experiment = experiment
        return obj
