import logging
import math
import random  # use np.random everywhere?

import numpy as np

from genepi import utils

log = logging.getLogger(__name__)


class constant(utils.callable_function):
    def __init__(self, value=1):
        self.value = value

    def __call__(self, t):
        return self.value


class oscillate_and_decay(utils.callable_function):

    def __init__(self, decay_time=100., oscillate_freq=30., shift=35., scale=0.8):
        self.decay_time = decay_time
        self.oscillate_freq = oscillate_freq
        self.shift = shift
        self.scale = scale

    def __call__(self, t):
        return (self.scale
                * np.exp(-(t-self.shift) / self.decay_time)
                * np.cos((t-self.shift) / self.oscillate_freq)**2)


class double_exponential_decay(utils.callable_function):

    def __init__(self, fast_scale=0.8, fast_time=50.,
                 slow_scale=0.05, slow_time=300.,
                 smear=0.1, min_value=1e-6, max_value=1.):

        self.fast_scale = fast_scale
        self.fast_time = fast_time
        self.slow_scale = slow_scale
        self.slow_time = slow_time
        self.smear = smear
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, t):
        mean_value = (self.fast_scale * np.exp(-t/self.fast_time)
                     + self.slow_scale * np.exp(-t/self.slow_time))

        smeared_value = mean_value + random.gauss(0, self.smear)

        return min(self.max_value, max(self.min_value, smeared_value))


class piecewise_antigen_peaks(utils.callable_function):

    def __init__(self):
        self.asexual_peak_log_means = [11.5, 9.2, 5.7, 1]  # roughly 1e5, 1e4, 300, and 3/uL
        self.peak_sigma = 1.0

        weights = dict()  # From DTK simulations with one infection per year

        # immunity (under-5 yr olds)

        weights[0] = [(1, [1, 0, 0, 0]),  # probability weight by density_idx for antigen_index < 1
                      (2, [0.8, 0.15, 0.05, 0]),
                      (3, [0, 0.1, 0.9, 0]),
                      (4, [0, 0.05, 0.85, 0.1])]

        # immunity (5-15 yr olds)

        weights[1] = [(1, [0.95, 0.05, 0, 0]),
                      (2, [0.25, 0.5, 0.25, 0]),
                      (3, [0, 0.3, 0.7, 0]),
                      (4, [0, 0.05, 0.85, 0.1])]

        # immunity (15-30 yr olds)

        weights[2] = [(1, [0.8, 0.15, 0.05, 0]),
                      (2, [0.05, 0.7, 0.25, 0]),
                      (3, [0, 0.2, 0.8, 0]),
                      (4, [0, 0.05, 0.85, 0.1])]

        # immunity (30-50 yr olds)

        weights[3] = [(1, [0.2, 0.7, 0.1, 0]),
                      (2, [0, 0.5, 0.4, 0.1]),
                      (3, [0, 0.2, 0.8, 0]),
                      (4, [0, 0.05, 0.85, 0.1])]

        # immunity (TEST)

        weights[4] = [(1, [0, 0, 1, 0])]

        self.cum_weights = {imm: [(wt_idx, utils.accumulate_cdf(wts)) for (wt_idx, wts) in imm_w]
                            for imm, imm_w in weights.items()}

    def __call__(self, antigen_index, immunity):

        log.debug('Estimating density for immunity = %d' % immunity)

        cumwts_for_immunity = self.cum_weights[immunity]
        for (wt_idx, cumwts) in cumwts_for_immunity:
            if antigen_index < wt_idx:
                break

        log.debug('cumwts = %s', cumwts)
        density_idx = utils.weighted_choice(cumwts)
        log.debug('density_idx = %d', density_idx)
        asexual_peak = random.lognormvariate(self.asexual_peak_log_means[density_idx], self.peak_sigma)

        return asexual_peak


class gaussian_pdf(utils.callable_function):

    """ Gaussian normalized to amplitude=1 at maximum """

    def __init__(self, sigma=1):
        self.sigma = sigma

    def __call__(self, t):
        return math.exp(-t**2 / (2*self.sigma**2))


class expo_gauss_pdf(utils.callable_function):

    """ Convolution of an exponential and a gaussian """

    def __init__(self, sigma=1, lambd=1):
        self.sigma = sigma
        self.lambd = lambd

    def __call__(self, t):
        return math.exp(-self.lambd*t) * \
               math.erfc((self.lambd - t) / (math.sqrt(2)*self.sigma))