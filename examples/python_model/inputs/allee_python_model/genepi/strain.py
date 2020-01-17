from collections import deque
import hashlib
import itertools
import logging
import string

import numpy as np
import pandas as pd

from genepi import genome as gn
from genepi import disease
from genepi.config import Global

log = logging.getLogger(__name__)


def display_bit(b):
    """
    Display binary SNPs as follows:
      ---a----a---, where '-' is the major allele and 'a' is the minor allele.

    For more variable sites, e.g. microsatellites, display up to 53 sites for example like:
      bja-adci-d, where '-' is the most common allele and 'a-zA-Z' are the next (up to) 52 most common in order.

    N.B. The np.uint8 representation can hold values 0-255, so these could cycle back through the alphabet.
    But this is just a convenience function for visual inspection and not intended to be rigorously unique.
    """
    return '-' if not b else string.ascii_letters[(b-1) % 52]


class Antigen(object):
    """ Stores the properties of a distinct antigenic wave of parasitemia """

    def __init__(self, index, time, peak_asexual, gametocyte_rate):
        self.index = index
        self.time = time
        self.peak_asexual = peak_asexual
        self.gametocyte_rate = gametocyte_rate

    def __repr__(self):
        return '%s(%s, %s, %s, %s)' % (self.__class__.__name__, self.index, self.time, self.peak_asexual, self.gametocyte_rate)

    def asexual_density(self, time):
        """ Density estimated with respect to peak of antigenic wave """
        days_past_peak = time - self.time
        if abs(days_past_peak) > 15:
            density = 0
        else:
            density = self.peak_asexual * disease.model().asexual_density_template(days_past_peak)
        log.debug('Density = %0.2f parasites/uL for peak_asexual=%0.2f and days_past_peak=%d',
                  density, self.peak_asexual, days_past_peak)
        return density

    def gametocyte_density(self, time):
        """ Asexual density lagged by gametocyte latency and weighted by production rate """
        days_past_peak = time - self.time - disease.model().gametocyte_latency
        if abs(days_past_peak) > 30:
            density = 0
        else:
            density = self.gametocyte_rate * self.peak_asexual * disease.model().gametocyte_density_template(days_past_peak)
        # log.debug('Density = %0.2f gametocytes/uL for gametocyte_rate=%0.2f,'
        #           'peak_asexual=%0.2f and days_past_peak=%d',
        #           density, self.gametocyte_rate, self.peak_asexual, days_past_peak)
        return density


class Strain(object):
    """
    An object holding a reference to a genome
    represented as a numpy array.
    """

    id = itertools.count()
    hash_to_id = {}

    max_tracked_antigens = 4

    def __init__(self, genome, mod_fns=[]):

        self.genome = genome

        for fn in mod_fns:
            fn(self.genome)

        h = hash(self)
        existing_id = Strain.hash_to_id.get(h, None)

        if existing_id is not None:
            self.id = existing_id
        else:
            self.id = Strain.id.next()
            Strain.hash_to_id[h] = self.id
            sim = Global.simulation
            if sim:
                sim.notify('strain.init', self)

        log.debug('%s: id=%d\n%s', self.__class__.__name__, self.id, self)

        self.time_since_infection = 0

        # Adjustments in Infection.set_strain_properties incorporate individual-specific effects

        self.duration = disease.model().sample_infection_duration()  # complexity of infection reduces duration
        self.antigens = deque()  # Infection calls back to init_antigen where peak density depends on host immunity

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.genome)

    def __str__(self):
        return self.display_barcode()
        #return self.display_genome()

    def __hash__(self):
        hash_fn = hashlib.sha1  # a bit faster than md5
        return int(hash_fn(self.genome.view(np.uint8)).hexdigest(), 16)

    @classmethod
    def from_reference(cls):
        return cls(gn.model().reference_genome())

    @classmethod
    def from_allele_freq(cls, mod_fns=[]):
        barcode = gn.model().random_barcode()
        return cls.from_barcode(barcode, mod_fns)

    @classmethod
    def from_barcode(cls, barcode, mod_fns=[]):
        return cls(np.array(barcode, dtype=np.uint8), mod_fns)

    def fitness(self):
        return gn.model().strain_fitness(self.genome)

    def barcode(self, sites=None):
        return self.genome[sites] if sites else self.genome

    def display_barcode(self):
        return ''.join([display_bit(b) for b in self.barcode()])

    def display_genome(self):
        return pd.Series(self.genome, index=gn.model().index)

    def asexual_density(self):
        """ Total asexual density combining last and current antigenic waves """
        if self.time_since_infection < disease.model().incubation:
            density = 0
        else:
            density = sum([a.asexual_density(self.time_since_infection) for a in self.antigens])
        return density

    def gametocyte_density(self):
        """ Total gametocyte density combining last and current antigenic waves """
        disease_model = disease.model()
        if self.time_since_infection < (disease_model.incubation + disease_model.gametocyte_latency):
            density = 0
        else:
            density = sum([a.gametocyte_density(self.time_since_infection) for a in self.antigens])
        return density

    def init_antigen(self, immunity):
        self.switch_antigen(time_to_next=disease.model().time_to_first_peak_parasitemia, immunity=immunity)

    def switch_antigen(self, time_to_next=None, immunity=0):
        """ Sample properties of next antigenic wave. """

        index = self.antigens[-1].index + 1 if self.antigens else 0

        if not time_to_next:
            time_to_next = disease.model().sample_time_to_next_peak()
        time = time_to_next + self.time_since_infection

        if time > self.duration:
            asexual_peak = 0
        else:
            asexual_peak = disease.model().sample_peak_asexual(index, immunity)

        antigen = Antigen(index, time, asexual_peak, 0)
        antigen.gametocyte_rate = disease.model().sample_gametocyte_rate(antigen)

        self.antigens.append(antigen)

        if len(self.antigens) > self.max_tracked_antigens:
            self.antigens.popleft()

    def update(self, dt, immunity=0):
        """ Update infection time and check next antigenic wave """
        self.time_since_infection += dt
        last_antigen = self.antigens[-1]
        if self.time_since_infection >= last_antigen.time:
            if last_antigen.peak_asexual:
                self.switch_antigen(immunity=immunity)

    @property
    def expired(self):
        return self.antigens[-1].peak_asexual == 0