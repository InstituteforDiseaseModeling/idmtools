from importlib import import_module
from itertools import tee, takewhile
import logging
import math
import random

try:
    from itertools import izip as zip
except ImportError: # will be 3.x series
    pass

log = logging.getLogger(__name__)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def by_pair(l):
    "l -> (l0,l1), (l2,l3), (l4, l5), ..."
    if len(l) % 2:
        l.append(None)
    a = iter(l)
    return zip(a, a)


def cumsum(it):
    total = 0
    for x in it:
        total += x
        yield total


def accumulate_cdf(iterable):

    cdf, subtotal = [], 0
    norm = float(sum(iterable))

    if not norm:
        return []

    for it in iterable:
        subtotal += it/norm
        cdf.append(subtotal)

    cdf[-1] = 1.0

    return cdf


def nextTime(rateParameter):

    if rateParameter <= 0:
        raise Exception('Cannot calculate next time from zero rate.')

    return -math.log(1.0 - random.random()) / rateParameter


def poissonRandom(lam):

    if lam <= 0:
        return 0

    sumTime = 0
    N = 0

    while True:
        sumTime += nextTime(lam)
        if sumTime > 1:
            break
        N += 1

    return N


def binomialApproxRandom(n, p):
    """
    Small numbers: exact Binomial
    Near edges: Poisson approximation
    Intermediate probabilities: normal approximation
    """

    if n < 0 or p < 0:
        raise Exception('Binomial requires positive (n,p)=(%d,%f)' % (n, p))

    if n == 0 or p == 0:
        return 0

    if p > 1:
        log.warning('Fixing probability %f>1.0 to one.', p)
        return n

    if n < 10:
        return(sum([random.random() < p for _ in range(n)]))

    lt50pct = p < 0.5
    p_tmp = p if lt50pct else (1 - p)

    if n < 9 * (1 - p_tmp) / p_tmp:
        poisson_tmp = poissonRandom(n * p_tmp)
        return poisson_tmp if lt50pct else (n - poisson_tmp)

    normal_tmp = int(round(random.gauss(mu=n*p, sigma=math.sqrt(n * p * (1-p)))))

    return max(0, min(n, normal_tmp))


def weighted_choice(cumwts):

    R = random.random()
    idx = sum(takewhile(bool, (cw < R for cw in cumwts)))

    return idx


def choose_with_replacement(M, N):

    choose = random.choice
    indices = range(N)

    return [choose(indices) for _ in range(M)]


def choose_without_replacement(M, N):
    """
    Floyd algorithm: O(M) in choose M from N scenario,
    which can be much faster for some typical use cases
    than random.sample, which seems to be O(N)
    """

    if M > N:
        raise Exception('Cannot sample %d from %d without replacement', (M, N))

    if M == N:
        return range(M)

    chosen_idxs = set()
    for j in range(N-M, N):
        t = random.randint(0, j)
        idx = t if t not in chosen_idxs else j
        chosen_idxs.add(idx)

    return list(chosen_idxs)


def update_dict(base_dict, **overrides):

    for param_name, param_value in overrides.items():
        if param_name not in base_dict:
            log.warning('Cannot override non-existent parameter: %s', param_name)
        else:
            base_dict[param_name] = param_value
            log.info('  Setting %s to %s', param_name, param_value)


def update_obj(base_obj, **overrides):

    for param_name, param_value in overrides.items():
        if not hasattr(base_obj, param_name):
            log.warning('Cannot override non-existent %s parameter: %s', base_obj.__class__.__name__, param_name)
        else:
            setattr(base_obj, param_name, param_value)
            log.info('  Setting %s.%s = %s', base_obj.__class__.__name__, param_name, param_value)


class callable_function(object):

    def __init__(self):
        pass

    def __str__(self):
        params = ['%s=%s' % (k, v) for (k, v) in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(params))

    def __call__(self, t):
        return 1


def init_from_settings(settings, subpackage='', param_name=''):
    """ Recursive construction of serialized objects in settings dictionary. """

    if '_module_' in settings:
        module, mod_settings = module_from_settings(settings, param_name)
        log.debug('_module_ = %s, mod_settings = %s', module, mod_settings)
        mod_settings = init_from_settings(mod_settings, subpackage, param_name)
        return initialize_module(subpackage, module, **mod_settings)
    else:
        for name, value in settings.items():
            if isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, dict):
                        settings[name][i] = init_from_settings(v, subpackage)
            elif isinstance(value, dict):
                settings[name] = init_from_settings(value, subpackage, name)
            else:
                pass  # will just return this part of 'settings' unmodified

    return settings


def module_from_settings(settings, param_name=''):

    param_name = param_name if param_name else 'parameter'

    try:
        func_params = settings.copy()  # copy before destructive pop operation
        func_module = func_params.pop('_module_')
    except KeyError:
        log.warning('Unable to configure %s from settings: %s', param_name, func_params)
        raise

    return func_module, func_params


def initialize_module(subpackage, module, *args, **kwargs):

    try:
        mod_path = module.split('.')

        if len(mod_path) == 1 and subpackage:
            mod_path = [subpackage] + mod_path

        mod = import_module('.'.join(['genepi'] + mod_path))

        return factory(mod, *args, **kwargs)

    except ImportError:
        log.warning("ImportError for %s module: %s", subpackage, mod_path[-1])
        raise


def factory(module, *args, **kwargs):

    if 'init' in dir(module):
        return module.init(*args, **kwargs)  # module specific initialization

    def default_init(function_name, **params):
        """
        Default factory method where first argument is function_name
        and all others are parameters passed to that function.
        """
        if function_name in dir(module):
            func = getattr(module, function_name)
            return func(**params)
        else:
            raise Exception('No function %s in module.' % function_name)

    return default_init(*args, **kwargs)  # use default factory method
