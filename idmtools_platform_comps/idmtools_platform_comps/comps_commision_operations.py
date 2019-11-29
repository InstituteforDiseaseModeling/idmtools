import os
from dataclasses import dataclass
from typing import NoReturn, List
from uuid import UUID
from COMPS.Data import Simulation as COMPSSimulation, Configuration, Suite as COMPSSuite, Experiment as COMPSExperiment
from idmtools.core import ItemType
from idmtools.core.interfaces.ientity import IEntityList
from idmtools.core.interfaces.iitem import IItemList
from idmtools.entities import Suite, IExperiment
from idmtools.entities.iplatform import IPlatformCommissioningOperations
from idmtools.utils.time import timestamp


@dataclass
class COMPSPlatformCommissionOperations(IPlatformCommissioningOperations):
    parent: 'COMPSPlatform'

    def run_items(self, items: IItemList) -> NoReturn:
        for item in items:
            item.get_platform_object().commission()

    def _create_batch(self, batch: IEntityList, item_type: ItemType) -> List[UUID]:
        if item_type == ItemType.SIMULATION:
            created_simulations = []
            for simulation in batch:
                s = COMPSSimulation(name=simulation.experiment.name, experiment_id=simulation.parent_id,
                                    configuration=Configuration(asset_collection_id=simulation.experiment.assets.uid))
                self.parent.io.send_assets(item=simulation, comps_simulation=s)
                s.set_tags(simulation.tags)
                created_simulations.append(s)
            COMPSSimulation.save_all(None, save_semaphore=COMPSSimulation.get_save_semaphore())
            return [s.id for s in created_simulations]
        elif item_type == ItemType.EXPERIMENT:
            ids = [self._create_experiment(experiment=item) for item in batch]
            return ids
        elif item_type == ItemType.SUITE:
            ids = [self._create_suite(suite=item) for item in batch]
            return ids

    def _create_suite(self, suite: Suite) -> UUID:
        """
        Create a COMPS Suite
        Args:
            suite: local suite to be used to create COMPS Suite
        Returns: None
        """
        self.parent._login()

        # Create suite
        comps_suite = COMPSSuite(name=suite.name, description=suite.description)
        comps_suite.set_tags(suite.tags)
        comps_suite.save()

        # Update suite uid
        suite.uid = comps_suite.id
        return suite.uid

    def _create_experiment(self, experiment: IExperiment) -> UUID:

        if not self.parent.is_supported_experiment(experiment):
            raise ValueError("The specified experiment is not supported on this platform")

        # Cleanup the name
        experiment_name = COMPSPlatformCommissionOperations._clean_experiment_name(experiment.name)

        # Define the subdirectory
        subdirectory = experiment_name[0:self.parent.MAX_SUBDIRECTORY_LENGTH] + '_' + timestamp()

        config = Configuration(
            environment_name=self.parent.environment,
            simulation_input_args=experiment.command.arguments + " " + experiment.command.options,
            working_directory_root=os.path.join(self.parent.simulation_root, subdirectory).replace('\\', '/'),
            executable_path=experiment.command.executable,
            node_group_name=self.parent.node_group,
            maximum_number_of_retries=self.parent.num_retires,
            priority=self.parent.priority,
            min_cores=self.parent.num_cores,
            max_cores=self.parent.num_cores,
            exclusive=self.parent.exclusive
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
        self.parent.io.send_assets(item=experiment)
        return experiment.uid

    @staticmethod
    def _clean_experiment_name(experiment_name: str) -> str:
        """
        Enforce any COMPS-specific demands on experiment names.
        Args:
            experiment_name: name of the experiment
        Returns:the experiment name allowed for use
        """
        for c in ['/', '\\', ':']:
            experiment_name = experiment_name.replace(c, '_')
        return experiment_name
