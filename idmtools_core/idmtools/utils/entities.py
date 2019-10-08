import typing
from idmtools.services.experiments import ExperimentPersistService
from idmtools.core import ExperimentNotFound, UUID
from idmtools.services.platforms import PlatformPersistService

if typing.TYPE_CHECKING:
    from idmtools.entities.iplatform import TPlatform
    from idmtools.entities.iexperiment import TExperiment


def retrieve_experiment(experiment_id: UUID, platform: 'TPlatform' = None,
                        with_simulations: 'bool' = False) -> 'TExperiment':
    experiment = ExperimentPersistService.retrieve(experiment_id)

    if experiment:
        experiment.platform = platform  # Not really the best form, but...
    else:
        # This is an unknown experiment, make sure we have a platform to ask for info
        if not platform:
            raise ExperimentNotFound(experiment_id)

        # Try to retrieve it from the platform
        experiment = platform.get_item(id=experiment_id)
        if not experiment:
            raise ExperimentNotFound(experiment_id, platform)

        # We have the experiment -> persist it for next time
        experiment.platform_id = PlatformPersistService.save(platform)
        ExperimentPersistService.save(experiment)

    # At this point we have our experiment -> check if we need the simulations
    if with_simulations:
        experiment.children(refresh=True)  # children are lazy loaded; go ahead and load them anew
    return experiment
