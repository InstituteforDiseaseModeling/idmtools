import random

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

from genepi import utils
from genepi.analysis.genome import load_npz
from genepi.model.functions import piecewise_antigen_peaks, gaussian_pdf
from genepi.model import sample as random_sample

peak_fn = piecewise_antigen_peaks()

template_fn = gaussian_pdf(sigma=1.2)

duration_fn = random_sample.init('lognormvariate', mu=5.13, sigma=0.8)

hist_bins = np.arange(-0.005, 1.0051, 0.01)


def draw_weight_from_age(infection_age, immunity=0):
    if not infection_age:
        return peak_fn(0, immunity)
    else:
        if infection_age > duration_fn():
            return 0
        else:
            return peak_fn(infection_age / 20., immunity) * template_fn(random.randrange(0, 20))


def sample_immunity(immunity_weights):
    choices, weights = zip(*immunity_weights.items())
    cdf = utils.accumulate_cdf(weights)
    return choices[utils.weighted_choice(cdf)]


def select_samples(tx_file='simulations/TransmissionGeneticsReport.csv',
                   date_range=(15*365, 20*365),
                   pop_str='',
                   exclude_single_strain=True,
                   sample_rate=0.01):

    """
    Return sampled infections from the full set of recorded transmission events
    :param tx_file: transmission-record output file
    :param date_range: slice on min and max infection-acquisition dates
    :param pop_str: filter on population ID containing string
    :param exclude_single_strain: boolean to keep only infections with multiple genomes
    :param sample_rate: fraction of transmission events to keep
    :return: dict: infection ID -> (dict: infection day -> list: genome ID)
    """

    tx = pd.read_csv(tx_file)

    tx = tx.query('%d < day < %d' % date_range).set_index(['iid', 'day'])
    if pop_str:
        tx = tx[tx.pid.str.contains(pop_str)]
    # print(tx.head())

    samples = {}
    for iid, group in tx.groupby(level=0):
        if random.random() < sample_rate:
            if exclude_single_strain and len(group.gid.unique()) == 1:
                continue
            # print(group[['pid', 'gid']])
            s = group.groupby(level=1).gid.apply(list)
            samples.update({iid: s.to_dict()})

    # print(samples)
    return samples


def get_true_alt_fractions(samples,
                           gn_file='simulations/GenomeReport.npz',
                           min_density=1e4,
                           immunity_weights={0: 0.1, 1: 0.3, 2: 0.3, 3: 0.2}):

    if gn_file.lower().endswith('.csv'):
        genomes = pd.read_csv(gn_file)
    elif gn_file.lower().endswith('.npz'):
        genomes = load_npz(gn_file)
    else:
        raise Exception("Don't recognize genome file extension.")
    # print(genomes.head())

    alt_fractions = []

    for iid, gid_by_day in samples.items():

        # print(iid, gid_by_day)
        days = sorted(gid_by_day.keys())
        last_day = days[-1]
        # print(last_day)

        weights = []
        strains = []

        for day in days:
            for gid in gid_by_day[day]:
                weights.append(draw_weight_from_age(last_day - day, sample_immunity(immunity_weights)))
                strains.append(genomes.loc[gid].values)

        # print(weights)

        sum_weights = sum(weights)

        if sum_weights < min_density:
            continue  # not symptomatic episode

        norm_weights = [w / sum_weights for w in weights]
        # print(norm_weights)

        strains = np.array([s * w for (s, w) in zip(strains, norm_weights)])
        mean_alt = np.sum(strains, axis=0)
        alt_fractions.append(mean_alt)

        hist, bin_edges = np.histogram(mean_alt, bins=hist_bins)
        # print(hist)

    return alt_fractions


def get_smeared_alt_fractions(true_fractions,
                              noise_rate=1e-4):

    n_samples = len(true_fractions)

    if not n_samples:
        raise Exception('No samples to apply binomial smearing.')

    smeared_fractions = np.zeros((len(true_fractions[0]), n_samples))

    for i, mean_alt in enumerate(true_fractions):
        # depths = np.random.randint(1, 90, mean_alt.shape)
        depths = np.random.normal(80, 20, mean_alt.shape)

        # print(mean_alt)
        smear_alt = []
        for m, d in zip(mean_alt, depths):
            d = max(5, d)
            m = m + random.normalvariate(mu=0, sigma=noise_rate)
            if m >= 1:
                smear_alt.append(1)
            elif m <= 0:
                smear_alt.append(0)
            else:
                # print(m)
                alt = np.random.binomial(d, m) / float(d)
                smear_alt.append(alt)
                # print(smear_alt)

        smeared_fractions[:, i] = smear_alt

    return smeared_fractions


def histogram_alt_fractions(smeared_fractions, true_fractions):

    n_samples = smeared_fractions.shape[1]

    het2d = np.zeros((hist_bins.size - 1, n_samples))
    true_het2d = np.zeros((hist_bins.size - 1, n_samples))
    F_sw = np.zeros(n_samples)

    p_s = smeared_fractions.mean(axis=1)  # TODO: draw MAF directly from GenomeModel
    H_s = 2 * p_s * (1-p_s)

    for i in range(n_samples):
        p_w = smeared_fractions[:, i]  # smeared_fractions is 2-d np.array

        hist, bin_edges = np.histogram(p_w, bins=hist_bins)
        het2d[:, i] = hist

        hist, bin_edges = np.histogram(true_fractions[i], bins=hist_bins)  # true_fractions is a list of np.array
        true_het2d[:, i] = hist

        H_w = 2 * p_w * (1-p_w)
        F_sw[i] = 1.0 - np.mean(H_w[H_s > 0] / H_s[H_s > 0])  # exclude SNPs that are fixated in this sample

    columns = ['q%d' % int(np.round(100 * x)) for x in 0.5 * (hist_bins[1:] + hist_bins[:-1])]
    df = pd.DataFrame(het2d.T, columns=columns)  # N.B. columns only unique for binning >= 1%

    columns = ['true_q%d' % int(np.round(100 * x)) for x in 0.5 * (hist_bins[1:] + hist_bins[:-1])]
    df_true = pd.DataFrame(true_het2d.T, columns=columns)
    df = pd.concat([df, df_true], axis=1)

    # Summary metrics
    df['n_het'] = df.loc[:, 'q5':'q95'].sum(axis=1)
    df['F_sw'] = F_sw
    df['het_peak_idx'] = df.loc[:, 'q5':'q95'].idxmax(axis=1)
    df['n_het_true'] = df.loc[:, 'true_q5':'true_q95'].sum(axis=1)

    df.sort_values(by='n_het', ascending=True, inplace=True)  # TODO: categorical based on summary metrics

    return df


def sample_analysis(tx_file='simulations/TransmissionGeneticsReport.csv',
                    gn_file='simulations/GenomeReport.npz',
                    date_range=(15*365, 20*365),
                    pop_str='',
                    exclude_single_strain=True,
                    min_density=1e4,
                    noise_rate=1e-4,
                    immunity_weights={0: 0.1, 1: 0.3, 2: 0.3, 3: 0.2},
                    sample_rate=0.01):

    samples = select_samples(tx_file,
                             date_range, pop_str,
                             exclude_single_strain, sample_rate)

    true_alt_fractions = get_true_alt_fractions(samples, gn_file,
                                                min_density, immunity_weights)

    smeared_alt_fractions = get_smeared_alt_fractions(true_alt_fractions, noise_rate)

    het2d_df = histogram_alt_fractions(smeared_alt_fractions, np.array(true_alt_fractions))

    f, ax = plt.subplots(1, 1, figsize=(5, 5), num='n_het_vs_F_sw')
    het2d_df.plot('F_sw', 'n_het', kind='scatter', ax=ax)
    ax.set(ylim=(0, 5000), xlim=(0, 1))
    f.set_tight_layout(True)

    f, ax = plt.subplots(1, 1, figsize=(8, 2), num='alt_fraction_hist2d')
    ax.imshow(het2d_df.loc[:, 'q0':'q100'].T,
              cmap='YlGnBu_r', norm=LogNorm(vmin=1, vmax=1e3),
              aspect='auto', interpolation='nearest', origin='lower', extent=[0, len(het2d_df), 0, 1])
    f.set_tight_layout(True)

    f, axs = plt.subplots(3, 4, sharex=True, sharey=True,
                          figsize=(15, 8), num='Multi-strain infections')

    mixed_samples = het2d_df[het2d_df.n_het_true > 0]
    n_samples = len(mixed_samples)
    print(mixed_samples.loc[:, 'n_het':])

    for i in range(12):
        ax = axs[i//4, i % 4]
        logy = True

        sample_index = mixed_samples.index[i * n_samples//12]

        kwargs = dict(width=0.008, log=logy, alpha=0.5)
        ax.bar(hist_bins[:-1], het2d_df.loc[sample_index, 'true_q0':'true_q100'], color='firebrick', **kwargs)
        ax.bar(hist_bins[:-1], het2d_df.loc[sample_index, 'q0':'q100'], color='navy', **kwargs)
        ax.text(0.05, 5e4, het2d_df.loc[sample_index, 'n_het':'het_peak_idx'], va='top', size=9)

        ax.set(xlim=(-0.005, 1.005), ylim=(0.1, 1e5))

    f.set_tight_layout(True)

    return samples


if __name__ == '__main__':
    sample_analysis('../../examples/simulations/TransmissionGeneticsReport.csv',
                    '../../examples/simulations/GenomeReport.npz')
    plt.show()
