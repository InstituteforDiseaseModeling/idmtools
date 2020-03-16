from collections import defaultdict
import itertools
import logging
import math  # switch all to np?
import random  # use np.random?

import numpy as np
import pandas as pd

from genepi import utils
from genepi import genome as gn
from genepi.strain import Strain
from genepi.transmission import Transmission


log = logging.getLogger(__name__)


chromatids = 'AaBb'
chromatid_pairings = ('AB', 'Ab', 'aB', 'ab')  # excludes sister couplings (Aa or Bb)


def get_crossover_positions():
    """
    Draw independent crossover positions by chromosome with exponentially drawn inter-arrival distances.
    :return: dict (chromosome name) --> list of crossover positions in base pairs
    """

    xpoints = {}
    gn_model = gn.model()

    for chrom_name in gn_model.chrom_names:
        next_point = 0
        xpoints[chrom_name] = []
        chrom_length_bp = gn_model.Pf_chrom_lengths[chrom_name]
        while next_point < chrom_length_bp:
            if next_point:
                xpoints[chrom_name].append(next_point)
            d = int(math.ceil(random.expovariate(2.0 / gn_model.bp_per_morgan)))  # two sister chromatids
            next_point += d

    return xpoints


def meiosis_genomes(input_genomes, N=4):
    """
    Apply independent crossover events between non-sister chromatids and construct the resulting child genomes.
    :param input_genomes: genome arrays of each parent stacked
    :param N: number of child genome array objects to return from meiosis
    :return: a list of genome array objects, the genomes of which are the products of meiotic recombination
    """

    if N > 4:
        raise IndexError('Maximum of four distinct meiotic products to sample.')

    '''
    Initialization of a frame to hold the input genomes and the resulting outcrossed meiotic products.
    The MultiIndex from the GenomeModel allows (chrom, pos) slicing in absolute genome position
    to be tranlated to the discrete array representation of polymorphic positions.
    '''

    gn_model = gn.model()

    output_genomes = np.zeros((gn_model.n_polymorphisms(), N), dtype=np.uint8)

    xpoints = get_crossover_positions()
    # log.debug('crossover positions:\n%s', xpoints)

    '''
    Meiosis proceeds independently on each chromosomes with polymorphic positions represented.
    '''

    for chrom_name in gn_model.locations.keys():

        '''
        Crossover events are randomly assigned between pairs of non-sister chromatids.
        '''

        # log.debug('Chromosome %s', chrom_name)
        crossover_positions = [gn_model.chrom_slice_position(chrom_name, xp) for xp in xpoints[chrom_name]]
        chromatid_crosses = [(pos, random.choice(chromatid_pairings)) for pos in crossover_positions]
        # log.debug(chromatid_crosses)

        chromatid_order = sorted(chromatids, key=lambda k: random.random())  # initial shuffle
        initial_order = tuple(chromatid_order)
        # log.debug(initial_order)

        crosses_by_chromatid = defaultdict(list)
        for position, crossed_chromatids in chromatid_crosses:
            c1, c2 = [chromatid_order.index(c) for c in crossed_chromatids]
            for c in (c1, c2):
                crosses_by_chromatid[c].append(position)
            chromatid_order[c1], chromatid_order[c2] = chromatid_order[c2], chromatid_order[c1]

        '''
        Genetic blocks are copied from either the first or second parent genome into
        each of N meiotic products to be returned according to the assigned crossover events.
        '''

        for i, c in enumerate(initial_order[:N]):
            # log.debug('Cross positions involving chromatid %s (ix=%d): %s', c, i, crosses_by_chromatid[i])

            current_input_genome = itertools.cycle([0, 1] if c in 'Aa' else [1, 0])

            first, last = gn_model.chrom_locations[chrom_name]
            crossover_boundaries = [first] + crosses_by_chromatid[i] + [last + 1]

            for (l1, l2), input_genome in zip(utils.pairwise(crossover_boundaries), current_input_genome):
                # log.debug('(chr, pos) = (%s, %d: %d) ==> in%d', chrom_name, l1, l2, input_genome)

                chrom_slice = slice(l1, l2)
                output_genomes[chrom_slice, i] = input_genomes[input_genome, chrom_slice]

    return [output_genomes[:, i].copy(order='C') for i in range(N)]


def meiosis(in1, in2, N=4):
    """
    Apply independent crossover events between non-sister chromatids and construct the resulting child genomes.
    :param in1: first parent Strain object
    :param in2: second parent Strain object
    :param N: number of child Strain objects to return from meiosis
    :return: a list of Strain objects, the genomes of which are the products of meiotic recombination
    """

    return [Strain(g) for g in meiosis_genomes(np.stack([in1.genome, in2.genome]), N)]


def distinct_sporozoites_from(gametocyte_pairs, n_products):
    """
    Returns genetically distinct Transmission objects representing sporozoites from the meiotic products
    of multiple oocysts from mated parent gametocytes.

    :param gametocyte_pairs: a list of tuples of parent Strain objects representing mated oocysts from mated gametocytes
    :param n_products: the number of meiotic products to return from each of the parental genomes.
    :return: a list of Transmission objects storing the parent and child genome information
    """

    transmitted_sporozoites = []

    for (g1, g2), N in zip(gametocyte_pairs, n_products):

        if g1.id == g2.id:
            # log.debug('Selfing of gametocytes (id=%d)\n%s', g1.id, g1)
            t = Transmission((g1.id, g2.id), Strain(g1.genome))
            transmitted_sporozoites.append(t)
            continue

        meiotic_products = meiosis(g1, g2, N)
        # log.debug('Meiosis: %s', [str(mp) for mp in meiotic_products])
        tt = [Transmission((g1.id, g2.id), child_strain) for child_strain in meiotic_products]
        transmitted_sporozoites.extend(tt)

    return gn.GenomeModel.distinct(transmitted_sporozoites, id_fn=lambda t: t.genome.id)
