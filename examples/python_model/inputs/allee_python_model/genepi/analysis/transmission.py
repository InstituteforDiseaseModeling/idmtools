import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
import networkx as nx
import seaborn as sns

sns.set_style("white", {'grid.color': '.93'})
sns.set_context("notebook")
cmap = matplotlib.colors.ListedColormap(sns.color_palette("husl", 10))


def n_unique(x):
    return len(x.unique())


def onward_transmissions(tx, ax1):
    n_transmit = tx.groupby('iidParent')['iid'].apply(n_unique).values
    infections = set(tx.iid.values)
    parents = set(tx.iidParent.values)
    zero_bin = len(infections^parents)
    n_transmit = np.append(n_transmit, [0]*zero_bin)
    ax1.hist(n_transmit,
             bins=np.arange(-0.5, 10.5), normed=True,
             color='navy', alpha=0.2)
    ax1.set_xlabel('# onward transmissions')
    ax1.set_xlim([-1, 11])


def genomes_per_infection(tx, ax2):
    n_genomes = tx.groupby('iid')['gid'].apply(n_unique).values
    ax2.hist(n_genomes,
             bins=np.arange(0.5, 7.5), normed=True,
             color='navy', alpha=0.2)
    ax2.set_xlabel('# distinct genomes')
    ax2.set_xlim([0, 8])


def plot_infection_properties(tx):
    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), num='InfectionProperties')
    onward_transmissions(tx, ax1)
    genomes_per_infection(tx, ax2)
    f.set_tight_layout(True)


def mode(x):
    return x.value_counts().index[0]


def repeat_genomes(tx, repeat_threshold=3, reindex=0):
    """
    Generate the series of recurrent genomes that are transmitted
    and group according to transmission time and location.
    """

    # Assign unique numbers to population IDs for plt.imshow color scale
    unique_values = np.unique(tx.pid)
    enumerated_pids = {v: i for (i, v) in enumerate(unique_values)}
    tx['pid'] = tx.pid.map(lambda s: enumerated_pids[s])  # popId string --> int

    repeat_groups = tx.groupby(['gid', 'day'])['pid']

    repeats = repeat_groups.agg(mode).unstack('day')  # most common Population.id

    if not os.path.exists('output'):
        os.mkdir('output')

    tx.groupby(['gid'])['pid'].agg(mode).to_csv('output/genome_population_map.csv')  # used for IBD network coloring
    tx.groupby(['gid'])['pid'].count().to_csv('output/genome_counts.csv')  # used for IBD network node sizing

    repeats.dropna(thresh=repeat_threshold, inplace=True)

    if reindex:
        repeats = repeats.T.reindex(np.arange(0, tx.day.max(), reindex)).T  # time axis re-binned by time step

    return repeats


def plot_repeat_genomes(repeats, reindex=0):
    """
    Plot the recurrence of identical genome IDs by time and population ID.
    """

    f = plt.figure('RepeatGenomes')
    extent = (repeats.columns[0], repeats.columns[-1], repeats.index[-1], repeats.index[0]) if reindex else None
    plt.imshow(repeats.values, interpolation='nearest', aspect='auto', cmap=cmap, extent=extent)
    plt.xlabel('Days' if reindex else 'Repeated Genome Timestep')
    plt.ylabel('Genome ID')
    f.set_tight_layout(True)


def transmission_tree(tx, date_interval=None):
    """
    Construct a directed graph of transmission events
    """

    tree = nx.DiGraph()

    groups = tx.groupby(['day', 'iid'])

    for (day, iid), group in groups:

        if date_interval and day not in range(*date_interval):
            continue

        tree.add_node(iid, population=mode(group.pid))

        parent_infection_id = group.iidParent.mean()
        if not np.isnan(parent_infection_id):
            tree.add_edge(parent_infection_id, iid)

    return tree


def plot_transmission_tree(tree, gexf_output='transmission_tree.gexf'):
    """
    Plot transmission tree and optionally save to Gephi output format
    """

    f = plt.figure('TransmissionTree', facecolor='w', figsize=(9, 9))
    ax = f.add_axes([0, 0, 1, 1], aspect='equal', frameon=False, xticks=[], yticks=[])
    ax.set_title('Transmission Tree', y=0.95, color=(0.1, 0.1, 0.1))

    pos = nx.spring_layout(tree)

    nx.draw_networkx_edges(tree, pos, edge_width=1e-4, edge_color='gray', alpha=0.4)
    nx.draw_networkx_nodes(tree, pos, node_color='navy', node_size=60, alpha=0.4)

    if gexf_output:
        nx.write_gexf(tree, 'transmission_tree.gexf')  # Force Atlas, etc.


def transmission_analysis(file='simulations/TransmissionGeneticsReport.csv', **kwargs):
    """
    Analysis of the TransmissionGeneticsReport output
    """

    tx = pd.read_csv(file)

    # plot_infection_properties(tx)

    repeats = repeat_genomes(tx, **kwargs)
    plot_repeat_genomes(repeats, kwargs.get('reindex', 0))

    # tree = transmission_tree(tx)
    # plot_transmission_tree(tree, '')


if __name__ == '__main__':
    transmission_analysis('../../examples/simulations/TransmissionGeneticsReport.csv')
    plt.show()
