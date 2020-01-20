import os


class IBDBuilder(object):

    cwd = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, genomes_df,
                 reformat=True,
                 sample=100,  # default: 100x down-sampling
                 sample_genomes=[],
                 output_directory='output'):

        self.reformat = reformat
        self.output_directory = output_directory

        if sample_genomes:
            self.genomes_df = genomes_df.loc[sample_genomes]
        elif sample > 0:
            self.genomes_df = genomes_df.iloc[::sample, :]
        else:
            raise Exception('No samples passed to IBD builder')

    def process(self):
        # API for derived classes
        return