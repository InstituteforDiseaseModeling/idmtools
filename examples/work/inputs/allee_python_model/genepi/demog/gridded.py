from itertools import product
import logging

from . import seasonality

log = logging.getLogger(__name__)

init_conditions = dict(n_humans=500, n_infections=20, n_strains=3)


def set_all_vectorial_capacity(populations, V):
    for p in populations.values():
        p['vectorial_capacity_fn'] = seasonality.annual_cycle(*V)


def single_node(V=(0.2, 2e-3, 10), init_conditions=init_conditions):

    populations = {'Population #1': init_conditions.copy()}
    set_all_vectorial_capacity(populations, V)

    return populations


def multi_node(N=10, V=(0.18, 1e-3, 8), M=5e-4, init_conditions=init_conditions):

    def set_population(i):
        population = init_conditions.copy()
        population['migration_rates'] = {'Population #%d' % k: M/N
                                         for k in range(N) if k is not i}
        return population

    populations = {'Population #%d' % k: set_population(k) for k in range(N)}
    set_all_vectorial_capacity(populations, V)

    return populations


def grid_node(L=3, V=(0.18, 1e-3, 8), M=5e-4, init_conditions=init_conditions):

    def idx(i, j):
        return i * L + j

    def in_range(x):
        return 0 <= x < L

    def not_same(di, dj):
        return not (di == 0 and dj == 0)

    def set_population(i, j):
        dx = [-1, 0, 1]
        population = init_conditions.copy()
        population['migration_rates'] = {
            'Population #%d' % idx(i + di, j + dj): M / 8
            for (di, dj) in product(dx, dx)
            if not_same(di, dj) and in_range(i + di) and in_range(j + dj)}
        return population

    populations = {'Population #%d' % idx(i, j): set_population(i, j)
                   for (i, j) in product(range(L), range(L))}

    set_all_vectorial_capacity(populations, V)

    return populations
