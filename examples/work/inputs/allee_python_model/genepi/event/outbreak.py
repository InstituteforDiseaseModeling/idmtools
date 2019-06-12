import logging

import numpy as np

from genepi.strain import Strain

log = logging.getLogger(__name__)


def add_infected_individuals(sim, pop_ids, n_infections=1, mean_strains=1):

    populations = [sim.populations.get(pop_id) for pop_id in pop_ids]
    populations = filter(None, populations)

    if not populations:
        raise Exception('No specified values (%s) in sim.populations (%s).',
                        pop_ids, [p.id for p in sim.populations])

    for population in populations:
        n_strains_by_infection = np.random.poisson(lam=mean_strains, size=n_infections)
        n_strains_by_infection[n_strains_by_infection < 1] = 1  # At least one strain per infection

        log.info('Adding %d infections with <strains>=%0.1f to %s', n_infections, mean_strains, population.id)

        for i in range(n_infections):
            n_strains = n_strains_by_infection[i]
            population.add_infection_from_genomes([Strain.from_allele_freq() for _ in range(n_strains)])


if __name__ == '__main__':
    from functools import partial
    from genepi.settings import Params

    outbreak_fn = partial(add_infected_individuals, n_infections=10, mean_strains=1.8)
    params = Params()
    params.add_event(day=100, event=outbreak_fn)