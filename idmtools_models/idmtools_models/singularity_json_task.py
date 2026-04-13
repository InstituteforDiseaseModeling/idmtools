"""idmtools generic Singularity JSON configured task.

Copyright 2026, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import field, dataclass
from functools import partial
from typing import Optional, Any, Dict

from idmtools.assets import AssetCollection  # noqa F401
from idmtools.entities import CommandLine
from idmtools.entities.simulation import Simulation
from idmtools_models.json_configured_task import JSONConfiguredTask


@dataclass
class SingularityJSONConfiguredTask(JSONConfiguredTask):
    """
    SingularityJSONConfiguredTask provides a generic base for running JSON-configured tasks within Singularity containers.

    This class can be used with any task type (Python, R, shell commands, etc.) that needs
    to run within a Singularity container and use JSON configuration.

    Attributes:
        provided_command: Optional CommandLine to override the default command when running
                         in a Singularity container.

    Examples:
        >>> task = SingularityJSONConfiguredTask()
        >>> task.provided_command = CommandLine("singularity exec ./Assets/container.sif python3 ./Assets/script.py")
        >>> task.common_assets.add_assets(AssetCollection.from_id_file("container.sif.id"))
        >>> task.common_assets.add_asset("script.py")

    See Also:
        :class:`idmtools_models.json_configured_task.JSONConfiguredTask`
        :class:`idmtools_models.python.singularity_json_python_task.SingularityJSONConfiguredPythonTask`
    """
    provided_command: Optional[CommandLine] = field(default_factory=lambda: CommandLine(), metadata={"md": True})

    def pre_creation(self, parent, platform):
        """
        Pre-creation hook that sets the command to the provided_command.

        This allows the task to override its default command with a Singularity-specific
        command (e.g., wrapping with 'singularity exec').

        Args:
            parent: Parent entity (Simulation or IWorkflowItem)
            platform: Platform the task is being executed on

        Returns:
            None
        """
        super().pre_creation(parent=parent, platform=platform)
        self.command = self.provided_command

    @staticmethod
    def set_parameter_sweep_callback(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        """
        Convenience callback for parameter sweeps.

        This static method can be used with SimulationBuilder to easily sweep over
        parameters in the JSON configuration.

        Args:
            simulation: Simulation we are updating
            param: Parameter name to set
            value: Value to assign to the parameter

        Returns:
            Dict of tags to set on the simulation

        Raises:
            ValueError: If the task doesn't have a set_parameter method

        Examples:
            >>> builder = SimulationBuilder()
            >>> builder.add_sweep_definition(
            ...     SingularityJSONConfiguredTask.set_parameter_sweep_callback,
            ...     {"param": "beta", "value": 0.5}
            ... )
        """
        if not hasattr(simulation.task, 'set_parameter'):
            raise ValueError("set_parameter_sweep_callback can only be used on tasks with a set_parameter method")
        return simulation.task.set_parameter(param, value)

    @classmethod
    def set_param_partial(cls, parameter: str):
        """
        Create a partial function for parameter sweeps.

        This is a convenience method to create a partial function that can be used
        directly with SimulationBuilder.add_sweep_definition.

        Args:
            parameter: Name of the parameter to sweep

        Returns:
            Partial function bound to the specified parameter

        Examples:
            >>> builder = SimulationBuilder()
            >>> beta_sweep = SingularityJSONConfiguredTask.set_param_partial("beta")
            >>> builder.add_sweep_definition(beta_sweep, [0.1, 0.2, 0.3])
        """
        return partial(cls.set_parameter_sweep_callback, param=parameter)
