from typing import Type
from idmtools.registry.ModelSpecification import ModelSpecification, get_model_impl, get_model_type_impl
from idmtools.registry.PluginSpecification import get_description_impl


class PythonExperimentSpec(ModelSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @get_model_impl
    def get(self, configuration: dict) -> 'PythonExperiment':
        """
        Build our local platform from the passed in configuration object

        We do our import of platform here to avoid any weir
        Args:
            configuration:

        Returns:

        """
        from idmtools_models.python.PythonExperiment import PythonExperiment
        return PythonExperiment(**configuration)

    @get_model_type_impl
    def get_type(self) -> Type['PythonExperiment']:
        from idmtools_models.python.PythonExperiment import PythonExperiment
        return PythonExperiment