import os

import numpy as np

from genepi import genome as gn


def parse_snp_id(snp_id):
    """
    Parse SNP ID from dataframe into .map formatted line:
    e.g. Pf.1.2402 --> 1 Pf.1.2402 0.0016013 2402
    """
    _, chrom, pos = snp_id.split('.')
    pos_cM = float(pos) / (gn.bp_per_morgan / 100)
    return "{0} {1} {2:.7f} {3}".format(chrom, snp_id, pos_cM, pos)


def parse_genome(genome_id, genome=[]):
    """
    Parse genome ID and genome from dataframe into .ped formatted line:
    e.g. 0,00nan11... --> 0 g0 0 0 0 -9 1 1 1 1 1 2 2 2 2 2  ...
    """

    def encode(value):
        if np.isnan(value):
            # make heterozygous
            # GERMLINE doesn't accept missing data
            # will be flexible with heterozygous errors
            return '1 2'
        return "{0:d} {0:d}".format(int(value + 1))

    return '0 %s 0 0 0 -9 ' % genome_id + ' '.join([encode(x) for x in genome])


def plink_format(genomes, chrom_name='', output_directory='output'):
    """
    Transform dataframe into temporary PLINK formatted files (.map + .ped)

    By default, each line of the MAP file describes a single marker
    and must contain exactly 4 columns:
       chromosome (1-22, X, Y or 0 if unplaced)
       rs# or snp identifier
       Genetic distance (morgans)
       Base-pair position (bp units)

    """

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    map_file = os.path.join(output_directory, 'plink%s.map' % chrom_name)
    print('Writing file: %s' % map_file)
    with open(map_file, 'w') as f:
        for snp_id in genomes.columns:
            line = parse_snp_id(snp_id)
            f.write(line + '\n')

    """
    The PED file is a white-space (space or tab) delimited file;
    the first six columns are mandatory:
       Family ID
       Individual ID
       Paternal ID
       Maternal ID
       Sex (1=male; 2=female; other=unknown)
       Phenotype

    Genotypes (column 7 onwards) should also be white-space delimited;
    they can be any character (e.g. 1,2,3,4 or A,C,G,T or anything else)
    except 0 which is, by default, the missing genotype character.
    All markers should be biallelic. All SNPs (whether haploid or not)
    must have two alleles specified. Either Both alleles should be
    missing (i.e. 0) or neither.
    """

    ped_file = os.path.join(output_directory, 'plink%s.ped' % chrom_name)
    print('Writing file: %s' % ped_file)
    with open(ped_file, 'w') as f:
        for id_genome in zip(genomes.index, genomes.values):
            line = parse_genome(*id_genome)
            f.write(line+'\n')

    fam_file = os.path.join(output_directory, 'plink%s.fam' % chrom_name)
    print('Writing file: %s' % fam_file)
    with open(fam_file, 'w') as f:
        for genome_id in genomes.index:
            line = parse_genome(genome_id)
            f.write(line + '\n')
