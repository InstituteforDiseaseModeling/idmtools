import logging
import os

import pandas as pd

from genepi import genome as gn

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def positions_from_csv(regions_file, frequencies_file, min_allele_freq, home_MS):
    """
    Read micro-satellite positions from a regions CSV file in following format:

    region_name,chromosome,begin
    Ara2,11,416189
    AS1,11,416138
    AS11,6,377349

    And an allele frequency CSV file in the following format:

    region_name,allele,frequency
    AS1,185,0.003512293
    AS1,179,0.057200201
    AS1,167,0.003010537
    """

    log.info('Reading microsatellites from files: %s and %s', regions_file, frequencies_file)

    regions_df = pd.read_csv(os.path.join(os.path.dirname(__file__), regions_file), index_col=0)

    frequency_df = pd.read_csv(os.path.join(os.path.dirname(__file__), frequencies_file))
    frequency_df.sort_values(by=['region_name', 'frequency'], ascending=[True, False], inplace=True)
    frequency_s = frequency_df.set_index(['region_name', 'allele']).frequency

    if home_MS and 'home_MS' in regions_df.columns:
        MS_regions = regions_df.home_MS.dropna().unique()
    else:
        MS_regions = regions_df.index.values

    SNPs = []

    for region_name in MS_regions:
        region = regions_df.ix[region_name]
        frequencies = frequency_s.ix[region_name]
        frequencies = frequencies[frequencies > min_allele_freq]
        if frequencies.empty:
            continue
        frequencies /= frequencies.sum()  # for sampling with numpy.random.choice(p=frequencies)
        s = gn.Polymorphism(region.chromosome, region.begin, freq=frequencies.tolist(),
                            name=region_name, alleles=frequencies.index.tolist())
        SNPs.append(s)

    return SNPs


def init(min_allele_freq=0, home_MS=True, loci=[]):

    polymorphisms = positions_from_csv('MS_regions.csv', 'MS_allele_freqs.csv', min_allele_freq, home_MS)
    polymorphisms.extend([gn.Polymorphism(**l) for l in loci])

    return gn.MultiAlleleModel(polymorphisms)

