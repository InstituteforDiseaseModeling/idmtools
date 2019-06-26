import typing

from idmtools.services.experiments import ExperimentPersistService
from idmtools.core import ExperimentNotFound
from idmtools.services.platforms import PlatformPersistService

if typing.TYPE_CHECKING:
    from idmtools.core import TPlatform, TExperiment
    import uuid


def retrieve_experiment(experiment_id:'uuid', platform: 'TPlatform' = None, with_simulations:'bool'=False) -> 'TExperiment':
    experiment = ExperimentPersistService.retrieve(experiment_id)
    if experiment:
        return experiment

    if not platform:
        raise ExperimentNotFound(experiment_id)

    # No experiment was found in the persist service, try to retrieve from the platform
    experiment = platform.retrieve_experiment(experiment_id)
    if not experiment:
        raise ExperimentNotFound(experiment_id, platform)

    # Restore the simulations as well?
    if with_simulations:
        platform.restore_simulations(experiment)

    # We have the experiment -> persist and return
    experiment.platform_id = PlatformPersistService.save(platform)
    ExperimentPersistService.save(experiment)

    return experiment
