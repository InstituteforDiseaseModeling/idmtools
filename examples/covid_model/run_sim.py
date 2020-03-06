'''
Simple script for running the Covid-19 agent-based model
'''

import multiprocessing as mp
import time

import covid_abm


def run_sim(seed):
    sim = covid_abm.Sim()
    sim.set_seed(seed)  # 4 ok, 5 ok, 6 good
    sim.run(verbose=0)
    sim.likelihood()
    # if do_plot:
    # sim.plot(do_save=do_save)

    return sim


if __name__ == "__main__":
    print('{} cores'.format(str(mp.cpu_count())))

    start = time.time()

    with mp.Pool(48) as p:
        results = p.map(run_sim, range(48))

    for sim in results:
        print()
        print("Ran simulation:")
        print("\t{}".format('\n\t'.join([k + ": " + str(v) for k, v in sim.summary_stats().items()])))

    print(time.time() - start)
