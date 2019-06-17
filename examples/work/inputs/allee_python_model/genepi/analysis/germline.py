import glob
import logging
import os
import subprocess

import pandas as pd

from genepi import genome as gn
from .ibd import IBDBuilder
from .plink import plink_format

log = logging.getLogger(__name__)


class GermlineBuilder(IBDBuilder):

    def __init__(self, genomes_df,
                 chrom_names=gn.Pf_chrom_lengths_Mbp.keys(),
                 reformat=True,
                 sample=100,  # default: 100x down-sampling
                 sample_genomes=[],
                 germline_options={},
                 output_directory='output'):

        self.chrom_names = chrom_names
        self.germline_options = germline_options
        super(GermlineBuilder, self).__init__(genomes_df, reformat, sample, sample_genomes, output_directory)

    def get_chromosome(self, chrom_name):
        return self.genomes_df.filter(regex='\w\.%s\.\w' % chrom_name)

    def process(self):

        if self.reformat:

            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)

            for chrom_name in self.chrom_names:
                print('Chromosome %s:' % chrom_name)
                chrom_df = self.get_chromosome(chrom_name)
                plink_format(chrom_df, chrom_name, self.output_directory)
                self.run_germline(chrom_name)

        self.concatenate_germline_output()

    def run_germline(self, chrom_name=''):
        """
        Call out to GERMLINE
        http://www.cs.columbia.edu/~gusev/germline/
        to find pairwise IBD segments
        """

        args = tuple([self.output_directory, chrom_name] * 3)
        with open(os.path.join(self.cwd, 'germline.stdin'), 'w') as f:
            f.write('1\n%s/plink%s.map\n%s/plink%s.ped\n%s/germline%s' % args)

        with open(os.path.join(self.cwd, 'germline.stdin'), 'r') as f:

            exe = os.path.join(self.cwd, 'bin', 'germline')

            process_options = ['-min_m', str(self.germline_options.get('min_m', 10)),
                               '-bits', str(self.germline_options.get('bits', 128)),
                               '-w_extend',
                               # '-h_extend',
                               # '-bin_out',
                               # '-haploid',
                               '-err_hom', '0',
                               '-err_het', '0'
                               ]

            try:
                subprocess.check_call([exe] + process_options, stdin=f)

            except subprocess.CalledProcessError as e:
                codes={1:'GERMLINE: complete'}
                print(codes.get(e.returncode, '\nERROR CODE=%d' % e.returncode))

            except OSError:
                print('GERMLINE executable not found at %s' % exe)

    def concatenate_germline_output(self):

        all_files = glob.glob(os.path.join(self.output_directory, 'germline**.match'))
        if not all_files:
            log.warning('No GERMLINE match files to concatenate.')
            return

        df_list = []
        for df_file in all_files:
            print(df_file)
            if os.stat(df_file).st_size == 0:  # no IBD matches on this chromosome
                continue
            tmp = pd.read_csv(df_file, delim_whitespace=True, index_col=None, header=None)
            df_list.append(tmp)

        if not df_list:
            log.warning('No IBD matches on any chromosome...')
            return

        print('Concatenating %d GERMLINE outputs...' % len(df_list))
        df = pd.concat(df_list)
        df.columns = ['famId1', 'indId1', 'famId2', 'indId2',
                      'chrom', 'start', 'end', 'startSNP', 'endSNP',
                      'bits', 'dist', 'unit', 'mismatches', 'homo1', 'homo2']

        df.to_csv(os.path.join(self.output_directory, 'germline_ibd.csv'))