import os
import subprocess

import pandas as pd

from genepi import genome as gn
from .ibd import IBDBuilder
from .plink import parse_snp_id


def parse_snp(snp_id, snp_values):
    """
    Parse SNP info from Series into .vcf formatted line:
    e.g. Pf.1.2402 --> 1 2402 Pf.1.2402 A T . PASS . GT 0/. 1/.
    """
    _, chrom, pos = snp_id.split('.')
    pos_cM = float(pos) / (gn.bp_per_morgan / 100)
    line = "{0}\t{1}\t{2}\tA\tT\t.\tPASS\t.\tGT".format(chrom, pos, snp_id)  # dummy REF/ALT values
    return '\t'.join([line] + ['%d/%d' % (s, s) for s in snp_values])


class BeagleBuilder(IBDBuilder):

    @property
    def vcf_file(self):
        return os.path.join(self.output_directory, 'beagle.vcf')

    @property
    def map_file(self):
        return os.path.join(self.output_directory, 'plink.map')

    def process(self):

        if self.reformat:

            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)

            print('Writing file: %s' % self.map_file)
            with open(self.map_file, 'w') as f:
                for snp_id in self.genomes_df.columns:
                    line = parse_snp_id(snp_id)
                    f.write(line + '\n')

            self.vcf_format()
            self.run_beagle()

        self.parse_beagle_output()

    def run_beagle(self):
        """
        Call out to BEAGLE
        http://faculty.washington.edu/browning/beagle/beagle.html
        to find pairwise IBD segments
        """

        jar = os.path.join(self.cwd, 'bin', 'beagle.03May16.862.jar')  # version 4.1

        try:
            with open(os.path.join(self.cwd, 'beagle.stdout'), 'w') as f:
                print('Running BEAGLE...')
                subprocess.call(['java',
                                 '-jar', jar,
                                 'gt=%s' % self.vcf_file,
                                 'ibd=true',
                                 'map=%s' % self.map_file,
                                 'niterations=0',  # already phased (haploid)
                                 'overlap=500',
                                 'window=5000',  # at least 2x overlap
                                 'out=%s' % os.path.join(self.output_directory, 'beagle')],
                                stdout=f)

        except subprocess.CalledProcessError as e:
            codes = {1: 'BEAGLE: complete'}
            print(codes.get(e.returncode, '\nERROR CODE=%d' % e.returncode))

        except OSError:
            print('BEAGLE executable not found at %s' % jar)

    def vcf_format(self):
        """
        Transform dataframe into temporary VCF formatted file

        For example:

        ##fileformat=VCFv4.2
        ##FORMAT=<ID=GT,Number=1,Type=Integer,Description="Genotype">
        ##FORMAT=<ID=GP,Number=G,Type=Float,Description="Genotype Probabilities">
        ##FORMAT=<ID=PL,Number=G,Type=Float,Description="Phred-scaled Genotype Likelihoods">
        #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMP001	SAMP002
        20	1291018	rs11449	G	A	.	PASS	.	GT	0/0	0/1

        """

        column_names = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']
        column_names += [str(x) for x in self.genomes_df.index]  # sample IDs

        header = ['##fileformat=VCFv4.2',
                  '##FORMAT=<ID=GT,Number=1,Type=Integer,Description="Genotype">',
                  '#' + '\t'.join(column_names)]

        with open(self.vcf_file, 'w') as f:
            f.write('\n'.join(header) + '\n')
            for snp_id, snp_s in self.genomes_df.iteritems():
                line = parse_snp(snp_id, snp_s.values)
                f.write(line + '\n')

    def parse_beagle_output(self):

        df = pd.read_csv(os.path.join(self.output_directory, 'beagle.ibd'),
                         delim_whitespace=True,
                         names=['indId1', 'allele1', 'indId2', 'allele2',
                                'chrom', 'start', 'end', 'dist'])

        df = df[(df.allele1 == 1) & (df.allele2 == 1)]  # remove duplicates (haploid)

        df.to_csv(os.path.join(self.output_directory, 'beagle_ibd.csv'))
