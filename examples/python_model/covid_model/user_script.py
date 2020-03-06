"""
Simple script for running the Covid-19 agent-based model
"""

import multiprocessing as mp
import time

import covid_abm


def run_sim(seed):
    simstart = time.time()
    sim = covid_abm.Sim()
    sim.set_seed(seed)
    sim.run(verbose=0)
    sim.likelihood(verbose=0)
    print('{} - total sim time: {}'.format(str(seed), time.time() - simstart))

    return seed, sim


if __name__ == "__main__":
    print('{} cores'.format(str(mp.cpu_count())))

    start = time.time()

    with mp.Pool() as p:
        results = p.map(run_sim, range(100))

    for seed, sim in results:
        print()
        print("Ran simulation (seed {}):".format(seed))
        print("\t{}".format('\n\t'.join([k + ": " + str(v) for k, v in sim.summary_stats().items()])))
        print("\tLikelihood: {}".format(sim.likelihood(verbose=0)))

    print()
    print('total run time: {}'.format(time.time() - start))
