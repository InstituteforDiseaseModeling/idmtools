import random
import logging
log = logging.getLogger(__name__)

from genepi import genome as gn
from genepi.report.listener import Listener
from genepi import simulation

resistant_sites = {'AM': (13, 1725259)}

def is_resistant(g, drug):
    resistant_idx = gn.model().snp_bin_from_chrom_pos(*resistant_sites[drug])
    return g[resistant_idx]

def set_resistance(g, drug, allele=1):
    resistant_idx = gn.model().snp_bin_from_chrom_pos(*resistant_sites[drug])
    log.debug('Setting %s resistance at index %d', drug, resistant_idx)
    g[resistant_idx] = allele

class DrugTreatment(Listener):
    """
    Treatment with a drug on a new-infection transmission event

    e.g. treatment_by_population = lambda t: {'Population #1': {
                                                  'fraction': min(0.8, 0.3+0.1*t/365),
                                                  'clearance': lambda g: 0.5 if is_resistant(g, 'AM') else 0.95}}
    """

    def __init__(self, treatment_by_population):
        self.treatment_by_population = treatment_by_population
        self.event = 'infection.transmit'

    def notify(self, *args):
        try:
            transmission = args[0]
            assert isinstance(transmission, list)
        except:
            raise Exception('Expected list of Transmission objects as first argument.')

        popId = transmission[0].populationId

        sim = simulation.get()
        if sim == None:  # callback from populating initial infections
            return

        treatment = self.treatment_by_population(sim.day).get(popId, None)

        if not treatment or random.random() > treatment['fraction']:
            return

        infection = transmission[0].infection

        for i, g in enumerate(infection.genomes):
            infection.genomes = [g for g in infection.genomes if random.random() > treatment['clearance'](g.genome)]
            if not infection.genomes:
                log.debug('New infection cleared with prompt treatment.')
                infection.infection_timer = 0
