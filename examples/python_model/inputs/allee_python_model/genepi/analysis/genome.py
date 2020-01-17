import os
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.patches import FancyBboxPatch as fpatch
import networkx as nx
import scipy.io
import seaborn as sns

from genepi import genome as gn
from genepi.analysis.germline import GermlineBuilder
from genepi.analysis.beagle import BeagleBuilder

log = logging.getLogger(__name__)

sns.set_style("white", {'grid.color': '.93'})
sns.set_context("notebook")


class HaplotypeAnalyzer(object):

    df = None

    def __init__(self, gid_pairs=[],
                 min_ibd_segment=0,
                 input_file='output/germline_ibd.csv'):

        self.df = pd.read_csv(input_file)

        # For specific pairs of interest (e.g. within same infection)
        if gid_pairs:
            print('Slicing on links between %d specified pairs of genome IDs...' % len(gid_pairs))
            self.df['valid'] = 0
            self.df.set_index(['indId1', 'indId2']).sort_index(inplace=True)
            for gid1, gid2 in gid_pairs:
                print(gid1, gid2)
                if gid1 not in self.df.index:
                    continue
                if gid2 not in self.df.loc[gid1].index:
                    continue
                self.df.loc[(gid1, gid2), 'valid'] = 1
            self.df = self.df[self.df.valid > 0].reset_index()  # Total pairwise shared IBD lengths

        print('Calculating total pairwise shared IBD lengths...')
        self.shared = self.df[self.df.dist > min_ibd_segment].groupby(['indId1', 'indId2'])['dist'].sum()
        self.shared.sort_values(inplace=True, ascending=False)
        self.shared.name = 'sum_IBD'

    def plot_ibd_lengths(self):
        """ Plot IBD segment lengths """
        f = plt.figure('SegmentLengthIBD')
        self.df.dist.apply(np.log10).plot(kind='hist', bins=50, color='navy', alpha=0.2, fig=f)
        plt.xlabel('log10 IBD segment length (cM)')

    def plot_ibd_map(self):
        """ IBD segment locations + frequency """
        counts = self.df.groupby(['chrom', 'start', 'end'])['dist'].count()
        nchrom = len(counts.index.levels[0])
        ncol = 1 + nchrom/4
        nrow = int(np.ceil(float(nchrom) / ncol))
        f, axs = plt.subplots(nrow, ncol, num='SegmentMapIBD', figsize=(15, 10))
        for ichrom, (chrom, ibd_counts) in enumerate(counts.groupby(level=0)):
            ax = axs[ichrom//ncol, ichrom%ncol] if nrow*ncol > 1 else axs
            for idx, (rng, cnt) in enumerate(ibd_counts[chrom].iteritems()):
                ax.plot([x/1e6 for x in rng], [idx]*2, linewidth=0.1+0.6*np.log10(cnt), c='navy', alpha=0.5)
                ax.set_title('Chromosome %s' % chrom, y=0.85, x=0.25, fontsize=10)
                ax.get_yaxis().set_visible(False)
        f.set_tight_layout(True)

    def sorted_shared_idx(self, q=0.5):
        """ Get index of genome pair by IBD-sharing quantile """
        l = len(self.shared)
        return min(l-1, int(l*(1-q)))

    def plot_ibd_fractions(self):
        """ IBD shared fractions """
        f = plt.figure('SharedLengthIBD')
        self.shared.apply(np.log10).plot(kind='hist', bins=50, color='navy', alpha=0.2, fig=f)
        plt.xlabel('log10 Total IBD length (cM)')

    def plot_shared_regions(self, q, ax=None, fs=12):
        """
        Pairwise IBD chromosome painter
        """

        idx = self.sorted_shared_idx(q)
        pair_sharing = self.shared.reset_index().iloc[idx]
        g1, g2, v = pair_sharing.indId1, pair_sharing.indId2, pair_sharing.sum_IBD
        print('q%02d genome similarity: %s and %s (IBD=%0.1f cM)' % (int(q*100), g1, g2, v))

        pair = self.df.groupby(['indId1', 'indId2']).get_group((g1, g2))
        if not ax:
            plt.figure('ChromosomePainterIBD_%s_%s' % (g1, g2))
            ax = plt.subplot(111)
        ax.set(ylim=[0, 15], xlim=[-0.1, 3.5],
               yticks=range(1, 15),
               ylabel='chromosome', xlabel='position (MB)')
        ax.text(1.7, 0.9, '\n(%s, %s)\nIBD=%0.1fcM' % (g1, g2, v), fontsize=fs)

        h = 0.4
        for c, l in gn.Pf_chrom_lengths_Mbp.items():
            ax.add_patch(fpatch((0, c-h/2), l, h,
                                boxstyle="square,pad=0",  # "round,pad=0.03"
                                fc=(1,1,1,0), ec=(0, 0, 0, 0.5)))
        for (c, s, e) in pair[['chrom', 'start', 'end']].values:
            ax.add_patch(fpatch((s/1e6, c-h/2), (e-s)/1e6, h,
                                boxstyle="square,pad=0",
                                fc=(0, 0, 0.5, 0.2),ec=(0, 0, 0, 0.0)))

    def sample_shared_pairs(self, quantiles):
        """
        Make pairwise shared-block comparisons
        for a list of IBD-total-sharing quantiles.
        """
        n_quantiles = len(quantiles)
        f, axs = plt.subplots(1, n_quantiles, num='ChromosomePainterIBD',
                              figsize=(min(18, 4.5*n_quantiles), 4),
                              sharex=True, sharey=True)
        for i, q in enumerate(quantiles):
            ax = axs[i] if n_quantiles > 1 else axs
            self.plot_shared_regions(q, ax, fs=10)
        f.set_tight_layout(True)

    def plot_relation_network(self, total_ibd_sharing_filter=0,
                              max_total_ibd=1500,
                              ibd_spring_scale=5e-4,
                              log_spring_weights=False,
                              draw_labels=False,
                              gexf_output=False):

        """ IBD fraction network """

        f = plt.figure('RelationNetworkIBD', facecolor='w', figsize=(9, 9))
        ax = f.add_axes([0, 0, 1, 1], aspect='equal', frameon=False, xticks=[], yticks=[])
        ax.set_title('IBD network', y=0.95, color=(0.1, 0.1, 0.1))

        # Add edges between samples weighted by total IBD
        ibd_graph = nx.Graph()
        for pair, ibd in self.shared.iteritems():
            if ibd <= total_ibd_sharing_filter:
                continue
            if log_spring_weights:
                w = float((6 + np.log2(ibd/max_total_ibd)) * ibd_spring_scale)
            else:
                w = float(ibd_spring_scale * ibd/max_total_ibd)
            ibd_graph.add_edge(*pair, ibd=float(ibd), weight=w)

        # Assign size property and corresponding size to nodes
        gene_count_file = 'output/genome_counts.csv'
        ns = []

        if os.path.exists(gene_count_file):
            gene_count_map = pd.Series.from_csv(gene_count_file)
            for n in ibd_graph.nodes_iter():
                count = gene_count_map.loc[n]
                ibd_graph.node[n]['size'] = float(count)
                ns.append(count)
            for (n, count) in gene_count_map.iteritems():
                if n in ibd_graph.nodes():
                    continue
                # Add clones with no relatives
                ibd_graph.add_node(n, size=float(count))
                ns.append(count)

        # Assign a site property and corresponding color to nodes
        cmap = matplotlib.colors.ListedColormap(sns.color_palette("husl", 10))
        gene_pop_file = 'output/genome_population_map.csv'
        nc = []
        pop_ids = []

        if os.path.exists(gene_pop_file):
            gene_pop_map = pd.read_csv(gene_pop_file, header=None, index_col=0, names=['gid', 'pid'])
            for n in ibd_graph.nodes_iter():
                if n in gene_pop_map.index:
                    pid = gene_pop_map.loc[n]['pid']
                    ibd_graph.node[n]['site'] = str(pid)
                    try:
                        pid_idx = pop_ids.index(pid)
                    except ValueError:
                        pid_idx = len(pop_ids)
                        pop_ids.append(pid)
                    nc.append(pid_idx)
                else:
                    print('WARNING: no transmissions of genome id=%s'%n)
                    nc.append(0)

            cmap = matplotlib.colors.ListedColormap(sns.color_palette("husl", len(pop_ids)))

        # Position nodes according to spring layout
        pos = nx.spring_layout(ibd_graph, weight='weight')
        nx.draw_networkx_edges(ibd_graph, pos, edge_width=1e-4, edge_color='gray', alpha=0.3)
        nc = nc if nc else 'black'
        nx.draw_networkx_nodes(ibd_graph, pos, node_color=nc, node_size=ns if ns else 60, alpha=0.4, cmap=cmap)

        if draw_labels:
            label_pos = {k: (x, y-0.012) for (k, (x, y)) in pos.items()}
            nx.draw_networkx_labels(ibd_graph, label_pos, font_size=5, font_color='darkgray')

        # Draw legend based on points outside view
        for i, pid in enumerate(pop_ids):
            ax.scatter([-10], [-10], s=60, c=cmap.colors[i], alpha=0.4, label=pid)
        ax.set(xlim=(-0.1, 1.1), ylim=(-0.1, 1.1))
        plt.legend()

        if gexf_output:
           write_gexf(ibd_graph)

        return ibd_graph

    def ibd_analysis(self, **kwargs):
        if self.df is None:
            print('No IBD info to plot...')
            return

        print('Plotting...')
        self.plot_ibd_lengths()
        # self.plot_ibd_map()
        self.plot_ibd_fractions()
        # self.plot_shared_regions(q=0.8)
        self.sample_shared_pairs(quantiles=[0.03, 0.2, 0.5, 0.8, 0.97])
        self.plot_relation_network(**kwargs)


def matlatb_export(npz_file='simulations/GenomeReport.npz'):
    scipy.io.savemat('GenomeReport.mat', np.load(npz_file))


def write_gexf(ibd_graph):
    nx.write_gexf(ibd_graph, "output/ibd_network.gexf")


def load_npz(npz_file):
    with np.load(npz_file) as data:
        genomes = pd.DataFrame(data['genomes'], columns=data['header'])
    return genomes


def genome_analysis(file='simulations/GenomeReport.npz',
                    reformat=True, sample=100,
                    ibd_builder='GERMLINE',
                    sample_genomes=[], **kwargs):
    """
    Analysis of the GenomeReport output
    """

    genomes_df = load_npz(file)

    if ibd_builder == 'GERMLINE':
        builder_class = GermlineBuilder
        input_file = 'output/germline_ibd.csv'
    elif ibd_builder == 'BEAGLE':
        builder_class = BeagleBuilder
        input_file = 'output/beagle_ibd.csv'
    else:
        raise Exception("Don't recognize ibd_builder argument: %s. Known values = [GERMLINE, BEAGLE]." % ibd_builder)

    ibd_builder = builder_class(genomes_df,
                                reformat=reformat,
                                sample=sample,
                                sample_genomes=sample_genomes)

    ibd_builder.process()

    haplotype_analyzer = HaplotypeAnalyzer(
        input_file=input_file,
        gid_pairs=kwargs.pop('gid_pairs', []),
        min_ibd_segment=kwargs.pop('min_ibd_segment', 0))

    haplotype_analyzer.ibd_analysis(**kwargs)


if __name__ == '__main__':

    # matlab_export('../../examples/simulations/GenomeReport.npz')

    genome_analysis('../../examples/simulations/GenomeReport.npz',
                    reformat=True, sample=10)
    plt.show()
