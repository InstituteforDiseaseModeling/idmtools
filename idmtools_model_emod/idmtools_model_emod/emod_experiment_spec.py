from typing import Type
from idmtools.registry.model_specification import ModelSpecification, get_model_impl, get_model_type_impl
from idmtools.registry.plugin_specification import get_description_impl


class EMODExperimentSpec(ModelSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @get_model_impl
    def get(self, configuration: dict) -> 'EMODExperiment':
        """
        Build a local platform from the passed in configuration object. The
        import of platform is here to avoid problems.
        
        Args:
            configuration:

        Returns:

        """
        from idmtools_model_emod.emod_experiment import EMODExperiment
        return EMODExperiment(**configuration)

    @get_model_type_impl
    def get_type(self) -> Type['LocalPlatform']:
        from idmtools_model_emod.emod_experiment import EMODExperiment
        return EMODExperiment