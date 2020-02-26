import logging
import random  # replace with np.random everywhere?

from genepi import utils
from genepi import genome as gn
from genepi.strain import Strain
from genepi.transmission import Transmission
from genepi.infection import Infection
from genepi.human import HumanCohort, HumanIndividual
from genepi.migration import MigrationInfo

log = logging.getLogger(__name__)


class Population(object):
    """
    An object containing a list of infections and their dynamics
    """

    def __init__(self, id, sim, n_humans,
                 n_infections=0,
                 n_strains=0,
                 initial_immunity={0: 1.0},
                 vectorial_capacity_fn=lambda t: 0.05,
                 migration_rates={}):

        self.id = id
        self.sim = sim
        self.vectorial_capacity_fn = vectorial_capacity_fn
        self.migration_info = MigrationInfo(migration_rates)
        self.susceptibles = HumanCohort(self, n_humans, initial_immunity)
        self.infecteds = {}

        genomes = [gn.model().random_barcode() for _ in range(n_strains)]
        for _ in range(n_infections):
            genome = random.choice(genomes) if genomes else gn.model().random_barcode()
            self.add_infection_from_genomes([Strain(genome)])

        log.debug(self)

    def __str__(self):
        s = '%s:' % self.id
        s += '  humans=%d' % self.n_humans()
        s += '  infections=%d' % self.n_infecteds()
        s += '  <COI>=%0.1f' % self.mean_COI()
        return s

    def add_infection_from_genomes(self, genomes):

        idx = random.randrange(self.n_humans())
        individual = self.sample_human_by_index(idx)

        if individual:
            individual.infection.merge_infection(genomes)
            infection = individual.infection
        else:
            infection = self.add_new_infection(genomes)

        if not infection:
            return  # callback from add_new_infection could clear infection (e.g. drugs)?

        for strain in infection.genomes:
            tx = Transmission(infection=infection, genome=strain)
            self.notify_transmission([tx])

    def add_new_infection(self, genomes, individual=None):

        if not individual:
            individual = self.susceptibles.pop_individual()

        individual.infection = Infection(individual, genomes)
        self.infecteds[individual.id] = individual

        return individual.infection

    def sample_human_by_index(self, idx):
        if idx < self.n_infecteds():
            return self.infecteds.values()[idx]
        else:
            return None

    def transmit_infections(self, transmissions):

        n_infections = len(transmissions)
        log.debug('Add %d infections:', n_infections)

        idxs = utils.choose_with_replacement(n_infections, self.n_humans())
        log.debug('Selected individual indices: %s', idxs)

        for idx, transmission in zip(idxs, transmissions):

            genomes = [t.genome for t in transmission]

            i = self.sample_human_by_index(idx)
            if i is not None:
                i.infection.merge_infection(genomes)
                log.debug('Merged strains (idx=%d, id=%d):\n%s',
                          idx, i.id, i.infection)
                self.notify_transmission(transmission, i.infection)
            else:
                log.debug('New infected individual:\n%s', genomes)
                infection = self.add_new_infection(genomes)
                if infection:
                    self.notify_transmission(transmission, infection)

    def notify_transmission(self, transmission, infection=None):

        for t in transmission:
            t.populationId = self.id
            t.day = self.sim.day
            if infection:
                t.infection = infection

        self.sim.notify('infection.transmit', transmission)

    def update(self, dt):

        transmissions = []

        V = self.vectorial_capacity()
        log.info('%s  vectorial capacity=%0.2f', self, V)

        for iid, i in self.infecteds.items():

            i.update(dt)

            transmissions.extend(i.infection.get_transmissions())

            if i.infection.expired:
                recovered = self.infecteds.pop(iid)
                self.susceptibles.merge_individual(recovered)

            elif i.migration.migrating():
                emigrant = self.infecteds.pop(iid)
                self.transmit_emigrant(emigrant)

        if transmissions:
            self.transmit_infections(transmissions)

        self.cohort_migration(dt)

    def vectorial_capacity(self):
        return self.vectorial_capacity_fn(self.sim.day)

    def n_humans(self):
        return self.susceptibles.n_humans + self.n_infecteds()

    def n_infecteds(self):
        return len(self.infecteds)

    def n_polygenomic(self):
        return sum([i.infection.n_strains() > 1 for i in self.infecteds.values()])

    def mean_COI(self):
        """ Mean complexity of infection """
        n_infecteds = self.n_infecteds()
        if n_infecteds == 0:
            return 0
        return sum([i.infection.n_strains() for i in self.infecteds.values()]) / float(n_infecteds)

    def transmit_emigrant(self, emigrant):
        src_pop, dest_pop = self.id, emigrant.migration.destination
        self.sim.migrants[dest_pop].append((emigrant, src_pop))

    def cohort_migration(self, dt):

        mig_dest = self.migration_info.destinations_in_timestep
        destinations = mig_dest(self.susceptibles.n_humans, dt)

        if self.susceptibles.n_humans < len(destinations):
            log.warning('Migration rate would move more individuals than present in Population')
            destinations = destinations[:self.susceptibles.n_humans]

        self.susceptibles.n_humans -= len(destinations)

        for dest in destinations:
            self.sim.cohort_migrants[dest] += 1

        log.debug('Cohort migration from %s: %s', self.id, destinations)

    def receive_immigrant(self, immigrant, src_pop):

        immigrant.migration = self.migration_info.next_migration()

        # TODO: extend random migration to round-trip concepts using src_pop

        immigrant.population = self
        self.infecteds[immigrant.id] = immigrant
