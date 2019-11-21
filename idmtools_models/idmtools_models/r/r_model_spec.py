from typing import Type
from idmtools.registry.model_specification import ModelSpecification, get_model_impl, get_model_type_impl
from idmtools.registry.plugin_specification import get_description_impl


class RModelSpec(ModelSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provide R Based models for idmtools"

    @get_model_impl
    def get(self, configuration: dict) -> 'RModel':  # noqa: F821
        """
        Build our local platform from the passed in configuration object

        We do our import of platform here to avoid any weir
        Args:
            configuration:

        Returns:

        """
        from idmtools_models.r.r_model import RModel
        return RModel(**configuration)

    @get_model_type_impl
    def get_type(self) -> Type['RExperiment']:
        from idmtools_models.r.r_model import RModel
        return RModel
