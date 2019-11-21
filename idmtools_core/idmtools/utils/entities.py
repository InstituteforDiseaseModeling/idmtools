import dataclasses
import typing
from idmtools.services.experiments import ExperimentPersistService
from idmtools.core import ExperimentNotFound, UUID, ItemType

if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import TPlatform
    from idmtools.entities.experiment import TExperiment


def retrieve_experiment(experiment_id: UUID, platform: 'TPlatform' = None, with_simulations=False) -> 'TExperiment':
    experiment = ExperimentPersistService.retrieve(experiment_id)

    if not experiment:
        # This is an unknown experiment, make sure we have a platform to ask for info
        if not platform:
            raise ExperimentNotFound(experiment_id)

        # Try to retrieve it from the platform
        experiment = platform.get_item(item_id=experiment_id, item_type=ItemType.EXPERIMENT)
        if not experiment:
            raise ExperimentNotFound(experiment_id, platform)

        # We have the experiment -> persist it for next time
        ExperimentPersistService.save(experiment)

    if with_simulations:
        experiment.refresh_simulations()

    return experiment


def get_dataclass_common_fields(src, dest, exclude_none: bool = True) -> typing.Dict:
    """
    Extracts fields from a dataclass source object who are also defined on destination object. Useful for situations
    like nested configurations of data class options

    Args:
        src: Source dataclass object
        dest: Dest dataclass object
        exclude_none: When true, values of None will be excluded

    Returns:

    """
    dest_fields = [f.name for f in dataclasses.fields(dest)]
    src_fields = dataclasses.fields(src)
    result = dict()
    for field in src_fields:
        if field.name in dest_fields and (not exclude_none or (exclude_none and getattr(src, field.name, None) is not None)):
            result[field.name] = getattr(src, field.name)
    return result
