import logging
import os

import pandas as pd

from genepi import genome as gn

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

allele_freqs = [0.7567, 0.5334, 0.9282, 0.4096,
                0.2809, 0.1045, 0.4659, 0.6340,
                0.7400, 0.1839, 0.0155, 0.1021,
                0.9507, 0.9131, 0.3911, 0.8800,
                0.8641, 0.8476, 0.1940, 0.5053,
                0.6744, 0.8951, 0.5995, 0.9217]


def positions_from_txt_table(filename):
    """
    Read SNP positions from file in following format:
    CHR    POS
    Pf3D7_01_v3    130339
    """

    log.info('Reading SNPs from file: %s', filename)

    df = pd.read_csv(os.path.join(os.path.dirname(__file__), filename), delim_whitespace=True)
    df.columns = ['chrom', 'pos']
    df['chrom'] = df.chrom.map(lambda c: int(c.split('_')[1]))  # 'Pf3D7_01_v3' --> 1

    if len(allele_freqs) != len(df):
        raise Exception('Incompatible lengths of SNP positions and allele frequencies')

    df['freq'] = allele_freqs

    log.debug(df)

    df_list = df.to_dict('list')  # orient='records' changes dtype?
    df_records = [dict(zip(df_list.keys(), s)) for s in zip(*df_list.values())]

    return [gn.Polymorphism(**s) for s in df_records]


def init(min_allele_freq=0, loci=[]):

    if min_allele_freq > 0:
        raise Exception('Filtering on rare SNPs not supported for barcode.')

    polymorphisms = positions_from_txt_table('barcode_loci.txt')
    polymorphisms.extend([gn.Polymorphism(**l) for l in loci])

    return gn.BinaryGenomeModel(polymorphisms)

