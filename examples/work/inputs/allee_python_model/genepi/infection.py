from collections import defaultdict
import itertools
import logging
import random  # use np.random everywhere?

from genepi import utils
from genepi import meiosis
from genepi import disease
from genepi.strain import Strain
from genepi.transmission import Transmission
from genepi.config import Global

log = logging.getLogger(__name__)


class Infection(object):
    """
    An infection in a human containing one or more parasite strains,
    including the dynamics of parasite propagation through
    the mosquito vector into a new human host.
    """

    id = itertools.count()

    def __init__(self, host, genomes=[]):
        self.id = Infection.id.next()
        self.host = host
        self.genomes = []
        self.add_strains(genomes)
        self.transmissions = []
        log.debug('Infection: id=%d\n%s', self.id, self)

    def __str__(self):
        return '\n'.join([str(g) for g in self.genomes])

    def update(self, dt, vectorial_capacity):

        self.transmissions = []

        for idx, strain in enumerate(self.genomes):

            immunity = self.host.immunity if self.host else 0
            strain.update(dt, immunity=immunity)
            if strain.expired:

                sim = Global.simulation
                if sim:
                    sim.notify('strain.expired', strain, self)

                if self.host:
                    self.host.update_immunity(strain)

        self.genomes = [strain for strain in self.genomes if not strain.expired]

        if self.expired:
            return

        if vectorial_capacity:
            transmit_rate = vectorial_capacity * dt * self.infectiousness()
            n_transmit = utils.poissonRandom(transmit_rate)
            log.debug('  id=%d: transmit_rate=%0.2f  n_transmit=%d', self.id, transmit_rate, n_transmit)
            self.transmissions = [self.transmit() for _ in range(n_transmit)]

    def get_transmissions(self):
        return self.transmissions

    def transmit(self):

        if self.n_strains() == 1:
            clone = self.genomes[0]
            log.debug('Clonal transmission of genome id=%d', clone.id)
            return [Transmission((clone.id, clone.id), Strain(clone.genome), self)]

        n_hep = disease.model().sample_n_hepatocytes()
        n_ooc = disease.model().sample_n_oocysts()
        log.debug('Sample %d hepatocyte(s) from %d oocyst(s):', n_hep, n_ooc)

        if n_hep > disease.model().max_transmit_strains:
            log.debug('Truncating to %d hepatocytes:', disease.model().max_transmit_strains)
            n_hep = disease.model().max_transmit_strains

        n_products = self.sample_oocyst_products(n_hep, n_ooc)
        gametocyte_pairs = self.sample_gametocyte_pairs(len(n_products))
        sporozoites = meiosis.distinct_sporozoites_from(gametocyte_pairs, n_products)
        for s in sporozoites:
            s.parentInfection = self

        return sporozoites

    def infectiousness(self):
        return disease.model().infectiousness(self.gametocyte_density())

    def sample_gametocyte_pairs(self, N):
        pairs = []
        w = self.gametocyte_strain_cdf()
        for _ in range(N):
            pairs.append([self.select_strain(w), self.select_strain(w)])
        return pairs

    def gametocyte_strain_cdf(self):
        # TODO: do we want fitness to have an abolute cost to infectiousness
        #       or only a relative competitive disadvantage (as done here) to onward transmission
        cdf = utils.accumulate_cdf([g.fitness() * g.gametocyte_density() for g in self.genomes])
        log.debug('Gametocyte strain CDF: %s', cdf)
        return cdf

    def select_strain(self, cumwts):
        return self.genomes[utils.weighted_choice(cumwts)]

    @property
    def expired(self):
        return self.n_strains() == 0

    def merge_infection(self, genomes):

        # Limit addition of new strains
        limit = disease.model().max_transmit_strains
        n_current = self.n_strains()
        current_genome_ids = [g.id for g in self.genomes]

        N = len(genomes)
        M = int(round((1 - n_current/float(limit)) * N))

        new_strains = [genomes[i] for i in utils.choose_without_replacement(M, N)]

        log.debug('Choosing %d from %d genomes: %s', M, N, [g.id for g in genomes])
        log.debug('Adding IDs %s to IDs %s', [g.id for g in new_strains], current_genome_ids)

        # Don't reinfect with a currently present strain
        unique_strains = [g for g in new_strains if g.id not in current_genome_ids]
        self.add_strains(unique_strains)

        log.debug('Results in IDs: %s', [g.id for g in self.genomes])

        # TODO: Also truncate lowest density infections to force total below limit?

    def add_strains(self, strains):
        self.set_strain_properties(strains)
        self.genomes.extend(strains)

    def set_strain_properties(self, strains):
        """
        Modify strain properties
           * Shift in infection duration distribution in presence of high complexity of infection
           * Reduced asexual parasite density with higher individual immunity
        """

        n_strains = self.n_strains() + len(strains)
        host_immunity = self.host.immunity if self.host else 0

        for s in strains:
            s.duration = disease.model().sample_infection_duration(n_strains)
            s.init_antigen(immunity=host_immunity)

    def n_strains(self):
        return len(self.genomes)

    def asexual_density(self):
        return sum([g.asexual_density() for g in self.genomes])

    def gametocyte_density(self):
        return sum([g.gametocyte_density() for g in self.genomes])

    @staticmethod
    def sample_oocyst_products(n_hep, n_ooc):

        oocyst_product_idxs = list(itertools.product(range(n_ooc), range(4)))
        hep_idxs = [random.choice(oocyst_product_idxs) for _ in range(n_hep)]

        product_idxs = defaultdict(set)
        for o_idx, m_idx in hep_idxs:
            product_idxs[o_idx].add(m_idx)

        n_products_by_oocyst = [len(v) for k, v in product_idxs.items()]
        log.debug('meiotic products to be sampled per oocyst: %s', n_products_by_oocyst)

        return n_products_by_oocyst
