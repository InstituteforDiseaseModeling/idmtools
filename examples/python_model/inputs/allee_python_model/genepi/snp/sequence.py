import logging
import os

import pandas as pd

from genepi import genome as gn

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def positions_from_csv(filename, min_allele_freq):
    """
    Read SNP positions from a CSV file in following format:

    chrom,pos,freq
    1,1110,0.02631
    1,2271,0.03125
    1,2402,0.03125
    """

    log.info('Reading SNPs from file: %s', filename)

    df = pd.read_csv(os.path.join(os.path.dirname(__file__), filename))
    df = df[(df.freq > min_allele_freq) & (df.freq < (1-min_allele_freq))]  # remove SNPs fixated in either direction

    df_list = df.to_dict('list')  # orient='records' changes dtype?
    df_records = [dict(zip(df_list.keys(), s)) for s in zip(*df_list.values())]

    return [gn.Polymorphism(**s) for s in df_records]


def init(min_allele_freq=0.0, loci=[]):

    polymorphisms = positions_from_csv('sequence_loci.csv', min_allele_freq)
    polymorphisms.extend([gn.Polymorphism(**l) for l in loci])

    return gn.BinaryGenomeModel(polymorphisms)

