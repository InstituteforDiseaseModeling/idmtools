import logging
import math
import random

from genepi import utils
from genepi.model import sample, functions
from genepi.config import Global


log = logging.getLogger(__name__)


disease_defaults = {
    'max_transmit_strains': 10,

    'incubation': 7,  # days
    'gametocyte_latency': 10,  # days

    # Collins & Jeffery (1999) "...Patterns of Recrudescence..."
    'time_to_first_peak_parasitemia': 20.0,  # days
    'time_to_next_peak': utils.factory(sample, 'uniform', a=8, b=30),  # days

    'peak_asexual': utils.factory(functions, 'piecewise_antigen_peaks'),
    'asexual_density_template': utils.factory(functions, 'gaussian_pdf', sigma=1.2),

    # Eichner et al. (2001)
    'gametocyte_rate': utils.factory(sample, 'lognormvariate', mu=-3, sigma=2, max_value=0.1, min_value=3e-4),

    # log10(gam_rate) negatively associated with log10(asexual)
    # for first antigenic wave (r=-0.23, p<0.015) in Eichner et al. (2001)
    'asexual_gametocyte_log_correlation': -0.5,

    'gametocyte_density_template': utils.factory(functions, 'expo_gauss_pdf', sigma=1.2, lambd=0.5),

    # Maire et al. (2006) "A model for natural immunity..."
    'infection_duration': utils.factory(sample, 'lognormvariate', mu=5.13, sigma=0.8),

    # Limiting duration on frequent re-infection.  Bretscher et al. (2015)
    'high_COI_duration': utils.factory(sample, 'weibullvariate', beta=0.5, alpha=60.),

    # Fit membrane-feeding data from Burkina Faso: A. Ouedraogo (2015) JID
    'n_oocysts': utils.factory(sample, 'weibullvariate', alpha=2.5, beta=0.65, shift=1),

    'max_infectiousness': 0.8,  # limiting value of infectiousness at high gametocyte density
    'gametocyte_density_threshold': 200,  # threshold density (/uL) of gametocytes for infectiousness sigmoid

    # Bejon et al. (2005) "Calculation of Liver-to-Blood Inocula..."
    'n_hepatocytes': utils.factory(sample, 'lognormvariate', mu=1.6, sigma=0.8, min_value=1)
    }


class DiseaseModel(object):

    def __init__(self, params=disease_defaults):
        for name, value in params.items():
            setattr(self, name, value)

    def sample_gametocyte_rate(self, antigen):

        gametocyte_rate = self.gametocyte_rate()

        if antigen.peak_asexual > 1e4:
            gametocyte_rate *= 10**(self.asexual_gametocyte_log_correlation * \
                                    math.log10(antigen.peak_asexual / 1e4))

        # log.debug('Sampling gametocyte rate = %g for peak asexual density = %g', gametocyte_rate, antigen.peak_asexual)
        return gametocyte_rate

    def sample_peak_asexual(self, antigen_index, immunity):

        # TODO: separate immunity-based weights from peak-sampling function?

        asexual_peak = self.peak_asexual(antigen_index, immunity)

        # log.debug('Sampling peak asexual density = %g for antigen wave idx = %d and immunity = %g', asexual_peak, antigen_index, immunity)
        return asexual_peak

    def sample_time_to_next_peak(self):

        time_to_next = self.time_to_next_peak()
        # log.debug('Sampling time to next peak asexual density = %g', time_to_next)
        return time_to_next

    def sample_infection_duration(self, coi=0):

        if coi > 0:
            coi -= 1  # no interference for first strain

        fraction_max_coi = float(coi) / self.max_transmit_strains

        if random.random() > fraction_max_coi:
            infection_duration = self.infection_duration()
        else:
            infection_duration = self.high_COI_duration()

        # log.debug('Sampled infection duration = %d days', infection_duration)
        return infection_duration

    def infectiousness(self, gametocyte_density):

        infectiousness = self.max_infectiousness * \
                         (1 - math.exp(-gametocyte_density / self.gametocyte_density_threshold))

        # TODO: introduce some overdispersion around this uniform value?

        # log.debug('Infectiousness = %g at gametocyte density = %g', infectiousness, gametocyte_density)
        return infectiousness

    def sample_n_oocysts(self):
        return int(self.n_oocysts())

    def sample_n_hepatocytes(self):
        return int(self.n_hepatocytes())

    @classmethod
    def initialize_from(cls, params, set_global=True):
        _model = cls()
        utils.update_obj(_model, **params)
        if set_global:
            set_model(_model)
        return _model


"""
Access single globally accessible object of
DiseaseModel parameter values and functions.
"""


def model():
    _model = Global.disease_model
    if _model is None:
        _model = DiseaseModel()
        Global.disease_model = _model
    return _model


def set_model(_model):
    Global.disease_model = _model
