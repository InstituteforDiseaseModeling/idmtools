import os
from dataclasses import dataclass, field
from itertools import tee
from logging import getLogger, DEBUG
from typing import List, Type, Generator, NoReturn, Optional, TYPE_CHECKING
from uuid import UUID
from COMPS.Data import Experiment as COMPSExperiment, QueryCriteria, Configuration, Suite as COMPSSuite, \
    Simulation as COMPSSimulation
from idmtools.assets import AssetCollection
from idmtools.core import ItemType
from idmtools.core.experiment_factory import experiment_factory
from idmtools.core.logging import SUCCESS
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_experiment_operations import IPlatformExperimentOperations
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.collections import ParentIterator
from idmtools.utils.time import timestamp
from idmtools_platform_comps.utils.general import clean_experiment_name, convert_comps_status

if TYPE_CHECKING:
    from idmtools_platform_comps.comps_platform import COMPSPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class CompsPlatformExperimentOperations(IPlatformExperimentOperations):
    platform: 'COMPSPlatform'  # noqa F821
    platform_type: Type = field(default=COMPSExperiment)

    def get(self, experiment_id: UUID, columns: Optional[List[str]] = None, children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> COMPSExperiment:
        """
        Fetch experiments from COMPS

        Args:
            experiment_id: Experiment ID
            columns: Optional Columns. If not provided, id, name, and suite_id are fetched
            children: Optional Children. If not provided, tags and configuration are specified
            query_criteria Optional QueryCriteria
            **kwargs:

        Returns:
            COMPSExperiment with items
        """
        columns = columns or ["id", "name", "suite_id"]
        children = children if children is not None else ["tags", "configuration"]
        query_criteria = query_criteria or QueryCriteria().select(columns).select_children(children)
        return COMPSExperiment.get(
            id=experiment_id,
            query_criteria=query_criteria
        )

    def pre_create(self, experiment: Experiment, **kwargs) -> NoReturn:
        """
        Pre-create for Experiment. At moment, validation related to COMPS is all that is done

        Args:
            experiment: Experiment to run pre-create for
            **kwargs:

        Returns:

        """
        if experiment.name is None:
            raise ValueError("Experiment name is required on COMPS")
        super().pre_create(experiment, **kwargs)

    def platform_create(self, experiment: Experiment, num_cores: Optional[int] = None,
                        executable_path: Optional[str] = None,
                        command_arg: Optional[str] = None, priority: Optional[str] = None,
                        check_command: bool = True) -> COMPSExperiment:
        """
        Create Experiment on the COMPS Platform

        Args:
            experiment: IDMTools Experiment to create
            num_cores: Optional num of cores to allocate using MPI
            executable_path: Executable path
            command_arg: Command Argument
            priority: Priority of command
            check_command: Run task hooks on item

        Returns:
            COMPSExperiment that was created
        """
        # TODO check experiment task supported

        # Cleanup the name
        experiment_name = clean_experiment_name(experiment.name)

        # Define the subdirectory
        subdirectory = experiment_name[0:self.platform.MAX_SUBDIRECTORY_LENGTH] + '_' + timestamp()
        # Get the experiment command line

        exp_command: CommandLine = self._get_experiment_command_line(check_command, experiment)

        if command_arg is None:
            command_arg = exp_command.arguments + " " + exp_command.options

        if executable_path is None:
            executable_path = exp_command.executable

        # create initial configuration object
        comps_config = dict(
            environment_name=self.platform.environment,
            simulation_input_args=command_arg,
            working_directory_root=os.path.join(self.platform.simulation_root, subdirectory).replace(
                '\\', '/'),
            executable_path=executable_path,
            node_group_name=self.platform.node_group,
            maximum_number_of_retries=self.platform.num_retries,
            priority=self.platform.priority if priority is None else priority,
            min_cores=self.platform.num_cores if num_cores is None else num_cores,
            max_cores=self.platform.num_cores if num_cores is None else num_cores,
            exclusive=self.platform.exclusive
        )

        if logger.isEnabledFor(DEBUG):
            logger.debug(f'COMPS Experiment Configs: {str(comps_config)}')
        config = Configuration(**comps_config)

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
        return e

    def _get_experiment_command_line(self, check_command: bool, experiment: Experiment) -> CommandLine:
        """
        Get the command line for COMPS

        Args:
            check_command: Should we run the platform task hooks on comps?
            experiment: Experiment to get command line for

        Returns:
            Command line for Experiment
        """
        from idmtools_platform_comps.utils.python_version import platform_task_hooks
        if isinstance(experiment.simulations, Generator):
            if logger.isEnabledFor(DEBUG):
                logger.debug("Simulations generator detected. Copying generator and using first task as command")
            sim_gen1, sim_gen2 = tee(experiment.simulations)
            experiment.simulations = sim_gen2
            sim = next(sim_gen1)
            if check_command:
                task = platform_task_hooks(sim.task, self.platform)
            # run pre-creation in case task use it to produce the command line dynamically
            task.pre_creation(sim)
            exp_command = task.command
        elif isinstance(experiment.simulations, ParentIterator) and isinstance(experiment.simulations.items,
                                                                               TemplatedSimulations):
            if logger.isEnabledFor(DEBUG):
                logger.debug("ParentIterator/TemplatedSimulations detected. Using base_task for command")
            from idmtools.entities.simulation import Simulation
            task = experiment.simulations.items.base_task
            if check_command:
                task = platform_task_hooks(task, self.platform)
            # run pre-creation in case task use it to produce the command line dynamically
            task.pre_creation(Simulation(task=task))
            exp_command = task.command
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug("List of simulations detected. Using base_task for command")
            task = experiment.simulations[0].task
            if check_command:
                task = platform_task_hooks(task, self.platform)
            # run pre-creation in case task use it to produce the command line dynamically
            task.pre_creation(experiment.simulations[0])
            exp_command = task.command
        return exp_command

    def post_run_item(self, experiment: Experiment, **kwargs):
        """
        Ran after experiment. Nothing is done on comps other that alerting the user to the item

        Args:
            experiment: Experiment to run post run item
            **kwargs:

        Returns:
            None
        """
        super().post_run_item(experiment, **kwargs)
        user_logger.log(SUCCESS, f"\nThe running experiment can be viewed at {self.platform.endpoint}/#explore/"
                                 f"Simulations?filters=ExperimentId={experiment.uid}\n"
                        )

    def get_children(self, experiment: COMPSExperiment, columns: Optional[List[str]] = None,
                     children: Optional[List[str]] = None, **kwargs) -> List[COMPSSimulation]:
        """
        Get children for a COMPSExperiment

        Args:
            experiment: Experiment to get children of Comps Experiment
            columns: Columns to fetch. If not provided, id, name, experiment_id, and state will be loaded
            children: Children to load. If not provided, Tags will be loaded
            **kwargs:

        Returns:
            Simulations belonging to the Experiment
        """
        columns = columns or ["id", "name", "experiment_id", "state"]
        children = children if children is not None else ["tags"]

        children = experiment.get_simulations(query_criteria=QueryCriteria().select(columns).select_children(children))
        return children

    def get_parent(self, experiment: COMPSExperiment, **kwargs) -> COMPSSuite:
        """
        Get Parent of experiment

        Args:
            experiment: Experiment to get parent of
            **kwargs:

        Returns:
            Suite of the experiment
        """
        if experiment.suite_id is None:
            return None
        return self.platform._suites.get(experiment.suite_id, **kwargs)

    def platform_run_item(self, experiment: Experiment, **kwargs):
        """
        Run experiment on COMPS. Here we commission the experiment

        Args:
            experiment: Experiment to run
            **kwargs:

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Commissioning experiment: {experiment.uid}')
        experiment.get_platform_object().commission()

    def send_assets(self, experiment: Experiment, **kwargs):
        """
        Send assets related to the experiment

        Args:
            experiment: Experiment to send assets for

            **kwargs:

        Returns:
            None
        """
        if experiment.assets.count == 0:
            logger.warning('Experiment has not assets')
            return

        ac = self.platform._assets.create(experiment.assets)
        print("Asset collection for experiment: {}".format(ac.id))

        # associate the assets with the experiment in COMPS
        e = COMPSExperiment.get(id=experiment.uid)
        e.configuration = Configuration(asset_collection_id=ac.id)
        e.save()

    def refresh_status(self, experiment: Experiment, **kwargs):
        """
        Reload status for experiment(load simulations)

        Args:
            experiment: Experiment to load status for
            **kwargs:

        Returns:
            None
        """
        simulations = self.get_children(experiment.get_platform_object(), force=True, columns=["id", "state"], children=[])
        for s in simulations:
            experiment.simulations.set_status_for_item(s.id, convert_comps_status(s.state))

    def to_entity(self, experiment: COMPSExperiment, parent: Optional[COMPSSuite] = None, children: bool = True,
                  **kwargs) -> Experiment:
        """
        Converts a COMPSExperiment to an idmtools Experiment

        Args:
            experiment: COMPS Experiment objet to convert
            parent: Optional suite parent
            children: Should we load children objects?
            **kwargs:

        Returns:
            Experiment
        """
        # Recreate the suite if needed
        if experiment.suite_id is None:
            suite = kwargs.get('suite')
        else:
            # did we have the parent?
            if parent:
                suite = parent
            else:
                suite = kwargs.get('suite') or self.platform.get_item(experiment.suite_id, item_type=ItemType.SUITE)

        # Create an experiment
        experiment_type = experiment.tags.get("type") if experiment.tags is not None else ""
        obj = experiment_factory.create(experiment_type, tags=experiment.tags, name=experiment.name,
                                        fallback=Experiment)
        obj.platform = self.platform
        obj._platform_object = experiment

        if children:
            # Convert all simulations
            comps_sims = experiment.get_simulations()
            obj.simulations = [self.platform._simulations.to_entity(s, parent=obj, **kwargs) for s in comps_sims]    # Cause recursive call...

        # Set parent
        obj.parent = suite

        # Set the correct attributes
        obj.uid = experiment.id
        obj.comps_experiment = experiment
        obj.assets = self.get_assets_from_comps_experiment(experiment)
        if obj.assets is None:
            obj.assets = AssetCollection()
        return obj

    def get_assets_from_comps_experiment(self, experiment: COMPSExperiment) -> Optional[AssetCollection]:
        if experiment.configuration and experiment.configuration.asset_collection_id:
            return self.platform.get_item(experiment.configuration.asset_collection_id, ItemType.ASSETCOLLECTION)
        return None
