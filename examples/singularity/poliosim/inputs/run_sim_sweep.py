'''
Simple script for running Covasim
'''
import os
import sys

import poliosim as ps
import sim_to_inset

sys.path.insert(0, os.path.dirname(__file__))


def test_sweep(vaccine_coverage, scale_beta, rand_seed):

    # Make, run, and plot the sim
    beta = 0.0002 * scale_beta # scale_beta doesn't do anything, so adding it here.

    # Also, vaccine coverage doesn't do anything.
    # If those start working, use this implementation
    # sim = ps.Sim(pop_size=10000, n_days=50, pop_infected=100,
    #              vx_coverage=vaccine_coverage, scale_beta=scale_beta,
    #              rand_seed=rand_seed)

    sim = ps.Sim(pop_size=10000, n_days=50, pop_infected=100,
                 beta=beta, rand_seed=rand_seed)

    sim.run()
    sim_to_inset.create_insetchart(sim.results)


if __name__ == '__main__':
    vaccine_coverage_param = float(sys.argv[1])
    scale_beta_param = float(sys.argv[2])
    rand_seed_param = int(sys.argv[3])

    test_sweep(vaccine_coverage=vaccine_coverage_param,
               scale_beta=scale_beta_param,
               rand_seed=rand_seed_param)
