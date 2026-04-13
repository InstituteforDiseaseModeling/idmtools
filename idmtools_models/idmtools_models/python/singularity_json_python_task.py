"""idmtools Singularity JSON configured Python task.

Copyright 2026, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass
from typing import Union, TYPE_CHECKING

from idmtools.assets import AssetCollection
from idmtools.entities import CommandLine  # noqa F401
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools_models.python.python_task import PythonTask
from idmtools_models.singularity_json_task import SingularityJSONConfiguredTask

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform


@dataclass
class SingularityJSONConfiguredPythonTask(SingularityJSONConfiguredTask, PythonTask):
    """
    SingularityJSONConfiguredPythonTask combines SingularityJSONConfiguredTask and PythonTask.

    This class is specifically for running Python scripts with JSON configuration within
    Singularity containers. It inherits Singularity container support from the generic
    SingularityJSONConfiguredTask and Python-specific functionality from PythonTask.

    Examples:
        >>> task = SingularityJSONConfiguredPythonTask(script_path="model.py")
        >>> task.provided_command = CommandLine("singularity exec ./Assets/my_python.sif python3 ./Assets/model.py")
        >>> task.common_assets.add_assets(AssetCollection.from_id_file("my_python.sif.id"))

    See Also:
        :class:`idmtools_models.singularity_json_task.SingularityJSONConfiguredTask`
        :class:`idmtools_models.python.python_task.PythonTask`
        :class:`idmtools_models.python.json_python_task.JSONConfiguredPythonTask`
    """

    def __post_init__(self):
        """Constructor."""
        SingularityJSONConfiguredTask.__post_init__(self)
        PythonTask.__post_init__(self)

    def gather_common_assets(self) -> AssetCollection:
        """
        Return the common assets for a Singularity JSON Configured Python Task.

        Returns:
            Common AssetCollection
        """
        return PythonTask.gather_common_assets(self)

    def gather_transient_assets(self) -> AssetCollection:
        """
        Get transient assets. This should generally be the config.json.

        Returns:
            Transient assets (simulation-specific)
        """
        return SingularityJSONConfiguredTask.gather_transient_assets(self)

    def reload_from_simulation(self, simulation: Simulation, **kwargs):
        """
        Reload the task from a simulation.

        Args:
            simulation: Simulation to reload from
            **kwargs: Additional keyword arguments

        Returns:
            None

        See Also:
            :meth:`idmtools_models.singularity_json_task.SingularityJSONConfiguredTask.reload_from_simulation`
            :meth:`idmtools_models.python.python_task.PythonTask.reload_from_simulation`
        """
        SingularityJSONConfiguredTask.reload_from_simulation(self, simulation, **kwargs)
        PythonTask.reload_from_simulation(self, simulation, **kwargs)

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Pre-creation hook.

        Args:
            parent: Parent of task (Simulation or IWorkflowItem)
            platform: Platform the task is being executed on

        Returns:
            None

        See Also:
            :meth:`idmtools_models.singularity_json_task.SingularityJSONConfiguredTask.pre_creation`
            :meth:`idmtools_models.python.python_task.PythonTask.pre_creation`
        """
        PythonTask.pre_creation(self, parent, platform)
        SingularityJSONConfiguredTask.pre_creation(self, parent, platform)

    def post_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Post-creation hook.

        For us, we proxy the underlying SingularityJSONConfiguredTask and PythonTask.

        Args:
            parent: Parent entity
            platform: Platform the task is being executed on

        Returns:
            None

        See Also:
            :meth:`idmtools_models.singularity_json_task.SingularityJSONConfiguredTask.post_creation`
            :meth:`idmtools_models.python.python_task.PythonTask.post_creation`
        """
        SingularityJSONConfiguredTask.post_creation(self, parent, platform)
        PythonTask.post_creation(self, parent, platform)
