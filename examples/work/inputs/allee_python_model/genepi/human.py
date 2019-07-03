from collections import Counter
import itertools
import logging

import numpy as np

from genepi import utils

log = logging.getLogger(__name__)


class HumanCohort(object):
    """
    A cohort used to track aggregate properties of uninfected humans
    """

    def __init__(self, population, n_humans, immunity_fractions={}):
        self.population = population
        self.n_humans = n_humans
        self.immunity = Counter()
        if immunity_fractions:
            # TODO: approximate for large populations?
            immunity_values = np.random.choice(immunity_fractions.keys(), p=immunity_fractions.values(), size=n_humans)
            self.immunity = Counter(immunity_values)
        else:
            self.immunity[0] = n_humans

    def merge_individual(self, individual):
        self.n_humans += 1
        self.immunity[individual.immunity] += 1

    def pop_individual(self):
        if self.n_humans < 1:
            raise Exception('Attempting to pop_individual from empty HumanCohort.')
        self.n_humans -= 1
        sampled_immunity = self.sample_immunity()
        self.immunity[sampled_immunity] -= 1
        return HumanIndividual(self.population, immunity=sampled_immunity)

    def sample_immunity(self):
        choices, weights = zip(*self.immunity.items())
        cdf = utils.accumulate_cdf(weights)
        return choices[utils.weighted_choice(cdf)]

    def update(self, dt):
        # TODO: population-level immunity waning through birth/death process
        pass

    def cohort_migration(self):
        # TODO: correct sampling of individual immunity to pass back and forth
        #       passed object can't just be list of destinations,
        #       but perhaps a refactored cohort of 1 (or N?).
        pass


class HumanIndividual(object):
    """
    An individual instance for tracking infected humans
    """

    id = itertools.count()

    def __init__(self, population, infection=None, immunity=0):
        self.id = HumanIndividual.id.next()
        log.debug('HumanIndividual: id=%d', self.id)
        self.population = population
        self.infection = infection
        self.migration = population.migration_info.next_migration() if population else None
        self.immunity = immunity  # TODO: what are the units of this?

    def update(self, dt):
        if self.migration:
            self.migration.update(dt)
        vectorial_capacity = self.population.vectorial_capacity() if self.population else None
        self.infection.update(dt, vectorial_capacity)

    def update_immunity(self, strain):
        # TODO: increment according to decided-upon meaning of immunity counter
        #       for example: index > threshold, time_since_infection, etc.

        # TODO: this might belong in DiseaseModel?
        #self.immunity += strain.antigens[-1].index

        # TODO: address the meaning of the immunity counter,
        #       assure balancing and birth/death are handled efficiently in cohort_migration,
        #       modify weights in model.functions.piecewise_antigen_peaks,
        #       and update clear_infection_test check
        pass