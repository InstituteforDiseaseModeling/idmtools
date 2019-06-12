from collections import defaultdict
import logging

import numpy as np
import pandas as pd
from sortedcontainers import SortedList

from genepi import utils
from genepi.config import Global

log = logging.getLogger(__name__)

bp_per_morgan = 1.5e6

bp_per_Mbp = 1e6

Pf_chrom_lengths_Mbp = {1: 0.643, 2: 0.947, 3: 1.1, 4: 1.2, 5: 1.35,
                        6: 1.42, 7: 1.45, 8: 1.5, 9: 1.55, 10: 1.7,
                        11: 2.05, 12: 2.3, 13: 2.95, 14: 3.3}

# 'M': 0.005967, 'P': 0.034242  (mitochondria, plastid)


def loc_idx(pm_list):
    """
    A MultiIndex for GenomeModel representations of Polymorphism variables by location
    :param pm_list: list of Polymorphism objects
    :return: pandas.MultiIndex of (chrom, pos) tuples
    """
    return pd.MultiIndex.from_tuples([p.location for p in pm_list], names=['chrom', 'pos'])


class Polymorphism(object):
    """
    The properties of a polymorphic region in the genome,
    for example, single-nucleotide polymorphism (SNP) or microsatellites.
    """

    def __init__(self, chrom, pos, freq, fitness=None, name=None, alleles=None):

        self.chrom = chrom
        self.pos = pos
        self.freq = freq

        self.fitness = fitness
        self.name = name
        self.alleles = alleles

    def __repr__(self):
        return 'genome.%s(%d, %d)' % (self.__class__.__name__, self.chrom, self.pos)

    @property
    def location(self):
        return self.chrom, self.pos

    @staticmethod
    def default_name(chrom, pos):
        return 'Pf.%d.%d' % (chrom, pos)


class GenomeModel(object):

    """
    Base-class for representation of genetic polymorphisms on P.falciparum chromosomes.
    Derived classes include BinaryGenomeModel (binary SNPs) and MultiAlleleModel (microsatellites)
    """

    def __init__(self, polymorphisms):

        self.frequencies = None  # frequency of variable alleles in population
        self.names = None  # user-specified polymorphism names
        self.fitness = None  # user-specified fitness values for non-neutral polymorphisms
        self.locations = defaultdict(SortedList)  # cached polymorphic locations in an efficient format to slice for meiosis
        self.chrom_locations = {}  # cached location of beginning of chromosomes in genome representation

        raise Exception('%s should not be instantiated; only derived classes.' % self.__class__.__name__)

    @staticmethod
    def initialize_from(snp_module, **snp_settings):

        """
        Factory method for constructing GenomeModel instance from specifications
        :param snp_module: Name of module in genepi.snp subpackage
        :param snp_settings: Keyword arguments to init function of snp_module
        :return: Instance of class derived from GenomeModel
        """

        set_global = snp_settings.pop('set_global', True)
        _model = utils.initialize_module('snp', snp_module, **snp_settings)

        log.info('%d SNPs incorporated into GenomeModel', _model.n_polymorphisms())

        if set_global:
            set_model(_model)

        return _model

    @property
    def chrom_pos_index(self):
        """
        The locations of polymorphisms represented in the genome array.
        :return: pandas.MultiIndex representation of (chr, pos) positions
        """
        return self.frequencies.index

    def index_of_chrom_pos(self, chrom, pos):
        return self.chrom_locations[chrom][0] + self.locations[chrom].index(pos)

    def chrom_slice_position(self, chrom, pos):
        chrom_locations = self.locations[chrom]
        chrom_offset = self.chrom_locations[chrom][0]
        return chrom_locations.bisect_left(pos) + chrom_offset

    @property
    def bp_per_morgan(self):
        return bp_per_morgan

    def bp_per_centimorgan(self):
        return self.bp_per_morgan / 1e2

    @property
    def chrom_names(self):
        return Pf_chrom_lengths_Mbp.keys()

    @property
    def chrom_lengths_bp(self):
        return self.Pf_chrom_lengths.values()

    @property
    def chrom_lengths_Mbp(self):
        return Pf_chrom_lengths_Mbp.values()

    @property
    def Pf_chrom_lengths(self):
        return {chrom_name: int(chrom_length_Mbp * bp_per_Mbp)
                for chrom_name, chrom_length_Mbp in Pf_chrom_lengths_Mbp.items()}

    def n_polymorphisms(self):
        return len(self.frequencies)

    def get_SNP_names(self):
        # TODO: append user-specified names to tracked polymorphisms
        return [Polymorphism.default_name(*snp) for snp in self.chrom_pos_index.values]

    @staticmethod
    def distinct(genomes, id_fn=lambda g: g.id):
        # N.B. this operation doesn't necessarily keep the "oldest" strain with the same id
        return {id_fn(g): g for g in genomes}.values()

    def reference_genome(self):
        return np.zeros(self.n_polymorphisms(), dtype=np.uint8)

    def sort_all_indices(self):
        self.frequencies.sort_index(inplace=True)
        self.names.sort_index(inplace=True)
        self.fitness.sort_index(inplace=True)

        chrom_pos_tuples = self.chrom_pos_index.values
        self.locations = defaultdict(SortedList)
        for chrom, pos in chrom_pos_tuples:
            self.locations[chrom].add(pos)

        chrom_indices = list(map(lambda x: x[0], chrom_pos_tuples))
        #print(len(chrom_indices),chrom_indices)

        def first_and_last(A, x):
            return A.index(x), len(A) - 1 - A[::-1].index(x)

        self.chrom_locations = {chrom: first_and_last(chrom_indices, chrom) for chrom in self.locations.keys()}


class BinaryGenomeModel(GenomeModel):

    def __init__(self, polymorphisms):

        self.frequencies = pd.Series(
            data=[p.freq for p in polymorphisms], index=loc_idx(polymorphisms), name='MAF'  # minor-allele frequency
        )

        empty_ = [[] for _ in self.frequencies.index.names]
        empty_index = pd.MultiIndex(levels=empty_, labels=empty_, names=self.frequencies.index.names)

        named_polymorphisms = [p for p in polymorphisms if p.name]
        self.names = pd.Series(
            data=[p.name for p in named_polymorphisms],
            index=empty_index if not named_polymorphisms else loc_idx(named_polymorphisms),
            name='names'
        )

        non_neutral_polymorphisms = [p for p in polymorphisms if p.fitness]
        self.fitness = pd.Series(
            data=[p.fitness for p in non_neutral_polymorphisms],
            index=empty_index if not non_neutral_polymorphisms else loc_idx(non_neutral_polymorphisms),
            name='fitness'
        )

        self.sort_all_indices()

    def random_barcode(self):
        rands = np.random.random_sample((self.n_polymorphisms(),))
        return rands < self.frequencies.values

    def add_locus(self, polymorphism):

        chrom_pos = polymorphism.location

        self.frequencies.ix[chrom_pos] = polymorphism.freq
        self.frequencies.sort_index(inplace=True)

        if polymorphism.name:
            self.names.ix[chrom_pos] = polymorphism.name
            self.names.sort_index(inplace=True)

        if polymorphism.fitness:
            self.fitness.ix[chrom_pos] = polymorphism.fitness
            self.fitness.sort_index(inplace=True)

    def strain_fitness(self, genome):

        if self.fitness.empty:
            return 1.0

        genome_ixs = [self.index_of_chrom_pos(*chrom_pos) for chrom_pos in self.fitness.index.values]
        df = pd.DataFrame({'genome': genome[genome_ixs], 'fitness': self.fitness})

        return np.product(df.fitness[df.genome != 0].values)  # returns 1.0 if all reference alleles


class MultiAlleleModel(GenomeModel):

    def __init__(self, polymorphisms):

        self.frequencies = pd.DataFrame(data=[p.freq for p in polymorphisms],
                                        index=loc_idx(polymorphisms))

        self.alleles = pd.DataFrame(data=[p.alleles for p in polymorphisms],
                                    index=loc_idx(polymorphisms))

        empty_ = [[] for _ in self.frequencies.index.names]
        empty_index = pd.MultiIndex(levels=empty_, labels=empty_, names=self.frequencies.index.names)

        named_polymorphisms = [p for p in polymorphisms if p.name]
        self.names = pd.Series(
            data=[p.name for p in named_polymorphisms],
            index=empty_index if not named_polymorphisms else loc_idx(named_polymorphisms),
            name='names'
        )

        non_neutral_polymorphisms = [p for p in polymorphisms if p.fitness]
        self.fitness = pd.DataFrame(
            data=[p.fitness for p in non_neutral_polymorphisms],
            index=empty_index if not non_neutral_polymorphisms else loc_idx(non_neutral_polymorphisms)
        )

        self.sort_all_indices()

    def random_barcode(self):
        barcode = []
        for f in self.frequencies.values:
            f = f[f > 0].tolist()  # drop None values from allele frequencies
            barcode += [np.random.choice(range(len(f)), p=f)]
        return barcode

    def add_locus(self, polymorphism):

        chrom_pos = polymorphism.location

        self.frequencies.ix[chrom_pos, :] = polymorphism.freq
        self.frequencies.sort_index(inplace=True)

        self.alleles.ix[chrom_pos, :] = polymorphism.alleles
        self.alleles.sort_index(inplace=True)

        if polymorphism.name:
            self.names.ix[chrom_pos] = polymorphism.name
            self.names.sort_index(inplace=True)

        if polymorphism.fitness:
            self.fitness.ix[chrom_pos, :] = polymorphism.fitness
            self.fitness.sort_index(inplace=True)

    def strain_fitness(self, genome):
        # TODO: function to take product of fitness of non-neutral alleles in genome
        return 1.0

    def sort_all_indices(self):
        self.alleles.sort_index(inplace=True)
        super(MultiAlleleModel, self).sort_all_indices()


"""
Access single globally accessible object of
GenomeModel parameter values and functions.
"""


def model():
    _model = Global.genome_model
    if _model is None:
        raise Exception('No genome_model set in Global.')
    return _model


def set_model(_model):
    Global.genome_model = _model
