"""
Manages the creation of our platforms.

The Platform allows us to lookup a platform via its plugin name, "COMPS" or via configuration aliases defined in a platform plugins, such as CALCULON.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from contextlib import contextmanager
from dataclasses import fields
from logging import getLogger, DEBUG
from typing import TYPE_CHECKING
from idmtools.config import IdmConfigParser
from idmtools.core import TRUTHY_VALUES
from idmtools.core.context import set_current_platform, remove_current_platform
from idmtools.utils.entities import validate_user_inputs_against_dataclass


if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@contextmanager
def platform(*args, **kwargs):
    """
    Utility function to create platform.

    Args:
        *args: Arguments to pass to platform
        **kwargs: Keyword args to pass to platform

    Returns:
        Platform created.
    """
    logger.debug(f'Acquiring platform context with options: {str(*args)}')
    try:
        # check if we are already in a platform context and if so add to stack
        pl = Platform(*args, **kwargs)
        set_current_platform(pl)
        yield pl
    finally:
        # Code to release resource, e.g.:
        logger.debug('Un-setting current platform context')
        remove_current_platform()


class Platform:
    """
    Platform Factory.
    """
    def __new__(cls, block: str = None, **kwargs):
        """
        Create a platform based on the block and all other inputs.

        Args:
            block(str, optional): The INI configuration file block name.

        COMPSPlatform Keyword Args:
           - endpoint (str, optional): URL of the COMPS endpoint to use. Default is 'https://comps.idmod.org'
           - environment (str, optional):  Name of the COMPS environment to target, Default is Calculon, Options are Calculon, IDMcloud, SlurmStage, Cumulus, etc
           - priority (str, optional): Priority of the job. Default is 'Lowest'. Options are Lowest, BelowNormal, Normal, AboveNormal, Highest
           - node_group (str, optional): node group to target. Default is None. Options are 'idm_abcd', 'idm_ab', idm_cd', 'idm_a', 'idm_b', 'idm_c', 'idm_d', 'idm_48cores'
           - num_retries (int, optional): How retries if the simulation fails, Default is 0, max is 10
           - num_cores (int, optional): How many cores per simulation. Default is 1, max is 32
           - max_workers (int, optional): The number of processes to spawn locally. Defaults to 16, min is 1, max is 32
           - batch_size (int, optional): How many simulations per batch. Default is 10, min is 1 and max is 100
           - exclusive (bool, optional): Enable exclusive mode? (one simulation per node on the cluster). Default is False
           - docker_image (str, optional): Docker image to use for the simulation. Default is None

        SlurmPlatform Keyword Args:
           - nodes (int, optional): How many nodes to be used. Default is None
           - ntasks (int, optional):  Num of tasks. Default is None
           - cpus_per_task (int, optional): CPU # per task. Default is None
           - ntasks_per_core (int, optional): Task # per core. Default is None
           - max_running_jobs (int, optional): Maximum of running jobs(Per experiment). Default is None
           - mem (int, optional): Memory per core: MB of memory. Default is None
           - mem_per_cpu (int, optional): Memory per core: MB of memory. Default is None
           - partition (str, optional): Which partition to use. Default is None
           - constraint (str, optional): Specify compute node. Default is None
           - time (str, optional): Limit time on this job hrs:min:sec. Default is None
           - account (str, optional): if set to something, jobs will run with the specified account in slurm. Default is None
           - exclusive (bool, optional): Allocated nodes can not be shared with other jobs/users. Default is False
           - requeue (bool, optional): Specifies that the batch job should be eligible for re-queuing. Default is True
           - retries (int, optional): Default retries for jobs. Default is 1
           - sbatch_custom (str, optional): Pass custom commands to sbatch generation script. Default is None
           - modules (list, optional): modules to be load, for example load 'mpi' module. Default is []
           - dir_exist_ok (bool, optional): Specifies default setting of whether slurm should fail if item directory already exists. Default is False
           - array_batch_size (int, optional): Set array max size for Slurm job. Default is None
           - run_on_slurm (bool, optional): determine if run script as Slurm job. Default is False

        ContainerPlatform Keyword Args:
           - job_directory (str, optional): Job directory. Default is None
           - docker_image (str, optional): Docker image to use for the simulation. Default is None
           - extra_packages (list, optional): Extra packages to install. Default is None
           - data_mount (str, optional): Data mount point. Default is None
           - user_mounts (dict, optional): User mounts. Default is None
           - container_prefix (str, optional): Prefix for container name. Default is None
           - force_start (bool, optional): Force start container. Default is False
           - new_container (bool, optional): Start a new container. Default is False
           - include_stopped (bool, optional): Include stopped containers. Default is False
           - container_id (str, optional): The ID of the container being used.
           - max_job (int, optional): Max job. Default is 4
           - modules (list, optional): Modules to load. Default is None
           - debug (bool, optional): Debug mode. Default is False
           - retries (int, optional): The number of retries to attempt for a job.

        Returns:
            The requested platform.

        Raises:
            ValueError if the block is None
        """
        global current_platform, current_platform_stack
        from idmtools.registry.platform_specification import PlatformPlugins

        # Load all Platform plugins
        cls._platforms = PlatformPlugins().get_plugin_map()
        cls._aliases = PlatformPlugins().get_aliases()

        platform = cls._create_from_block(block, **kwargs)
        set_current_platform(platform)
        platform._config_block = block
        platform._kwargs = kwargs
        return platform

    @classmethod
    def _validate_platform_type(cls, name):
        """
        Check if the requested platform exists.

        Args:
            name: The platform type.

        Returns:
            None

        Raise:
            ValueError: when the platform is of an unknown type
        """
        if name not in cls._platforms:
            raise ValueError(f"{name} is an unknown Platform Type. "
                             f"Supported platforms are {', '.join(cls._platforms.keys())}")

    @classmethod
    def _create_from_block(cls, block: str, **kwargs) -> 'IPlatform':
        """
        Retrieve section entries from the INI configuration file by giving block.

        Args:
            block: The section name in the configuration file or platform alias.
            overrides: Optional override of parameters from the configuration file.

        Returns:
            A dictionary with entries from the block.
        """
        # Read block details
        platform_type = None
        section = {}

        if block:
            try:
                # If block is a section in the config file
                section = IdmConfigParser.get_section(block)
                if not section:
                    # its possible our logger is not setup
                    from idmtools.core.logging import setup_logging, LOGGING_STARTED, IdmToolsLoggingConfig
                    if not LOGGING_STARTED:
                        setup_logging(IdmToolsLoggingConfig())
            except ValueError:  # If block is not found in the ini config file
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Checking aliases for {block.upper()}")
                # If block is in aliases
                if block.upper() in cls._aliases:
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f"Loading plugin from alias {block.upper()}")
                    props = cls._aliases[block.upper()]
                    platform_type = props[0].get_name()
                    section = props[1]
                else:  # If block is not in aliases, create section from platform constructor
                    section = {'block': block}
                    section.update(kwargs)
        else:  # If block is None, try to get type from kwargs
            platform_type = kwargs.get('type')
            if not platform_type:
                raise Exception("Type must be specified in Platform constructor")

        if platform_type is None:
            try:
                # Make sure block has type entry
                platform_type = section.pop('type')
            except KeyError:
                # try to use the block name as the type
                user_logger.warning(
                    "You are specifying a platform without a configuration file or configuration block. Be sure you have supplied all required parameters for the Platform as this can result in unexpected behaviour. Running this way is only recommended for development mode. Instead, "
                    "it is recommended you create an idmtools.ini to capture the config once you have tested and confirmed your configuration.")
                platform_type = block

        # Make sure we support platform_type
        cls._validate_platform_type(platform_type)

        # Find the correct Platform type
        platform_spec = cls._platforms.get(platform_type)
        platform_cls = platform_spec.get_type()

        # Collect fields types
        fds = fields(platform_cls)
        field_name = [f.name for f in fds]
        field_type = {f.name: f.type for f in fds}

        # Make data to the requested type
        inputs = IdmConfigParser.retrieve_dict_config_block(field_type, section)

        # Make sure the user values have the requested type
        fs_kwargs = validate_user_inputs_against_dataclass(field_type, kwargs)  # noqa: F841

        # Update attr based on priority: #1 Code, #2 INI, #3 Default
        for fn in set(kwargs.keys()).intersection(set(field_name)):
            inputs[fn] = kwargs[fn]

        extra_kwargs = set(kwargs.keys()) - set(field_name)
        if "type" in extra_kwargs and platform_type == kwargs["type"]:
            extra_kwargs.remove("type")  # type is not extra input
        if len(extra_kwargs) > 0:
            field_not_used_display = [" - {} = {}".format(fn, kwargs[fn]) for fn in extra_kwargs]
            logger.warning("\n/!\\ WARNING: The following User Inputs are not used:")
            logger.warning("\n".join(field_not_used_display))

        # Display block info
        try:
            from idmtools.core.logging import VERBOSE
            # is output enabled and is showing of platform config enabled?
            if IdmConfigParser.is_output_enabled() and IdmConfigParser.get_option(None, "SHOW_PLATFORM_CONFIG", 't').lower() in TRUTHY_VALUES:
                if block is not None:
                    if inputs != section:  # Display section based on code first
                        for k, v in section.items():
                            if k in inputs:
                                section[k] = inputs[k]
                        user_logger.log(VERBOSE, f"\n[{block}]")
                        user_logger.log(VERBOSE, json.dumps(section, indent=3))
                    else:
                        IdmConfigParser.display_config_block_details(block)
        except ValueError:
            # This block is triggered by the call to IdmConfigParser.display_config_block_details(block) above when the specified block is not found in the INI config file. Typically, this occurs in cases where the input is an alias for a block. We still want to display the section to inform the user of what is being used."
            if block is not None:
                user_logger.log(VERBOSE, f"\n[{block}]")
                section.pop(block)  # Remove block from section
                user_logger.log(VERBOSE, json.dumps(section, indent=3))

        # Display not used fields of the block
        field_not_used = set(inputs.keys()) - set(field_type.keys())
        if len(field_not_used) > 0:
            field_not_used_display = [" - {} = {}".format(fn, inputs[fn]) for fn in field_not_used]
            logger.warning(f"\n[{block}]: /!\\ WARNING: the following Config Settings are not used when creating "
                           f"Platform:")
            logger.warning("\n".join(field_not_used_display))

        # Remove extra fields
        for f in field_not_used:
            inputs.pop(f)

        # Now create Platform using the data with the correct data types
        return platform_cls(**inputs)
