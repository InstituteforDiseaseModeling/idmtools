'''
Simple script for running Covasim
'''
import os
import sys

import sciris as sc
import covasim as cv

sys.path.insert(0, os.path.dirname(__file__))
import sim_to_inset

# Run options
do_plot = 1
verbose = 1
interv  = 1


def test_sweep(pop_size=10000, pop_infected=10, n_days=120, rand_seed=1, pop_type='hybrid'):
    # Configure the sim -- can also just use a normal dictionary
    pars = sc.objdict(
        pop_size     = pop_size,    # Population size
        pop_infected = pop_infected,       # Number of initial infections
        n_days       = n_days,      # Number of days to simulate
        rand_seed    = rand_seed,        # Random seed
        pop_type     = pop_type, # Population to use -- "hybrid" is random with household, school,and work structure
    )

    # Optionally add an intervention
    if interv:
        pars.interventions = cv.change_beta(days=45, changes=0.5)

    # Set the output directory path
    outputs = "outputs"
    if not os.path.exists(outputs):
        os.makedirs(outputs)

    # Make, run, and plot the sim
    sim = cv.Sim(pars=pars)
    sim.initialize()
    sim.run(verbose=verbose)

    sim.to_json(filename=os.path.join(outputs, "results.json"))
    sim.to_excel(filename=os.path.join(outputs, "results.xlsx"))

    sim_to_inset.create_insetchart(sim.to_json(tostring=False))

    if do_plot:
        sim.plot()
        cv.savefig(os.path.join(outputs, 'sim.png'))


if __name__ == '__main__':
    pop_size= sys.argv[1]
    pop_infected = sys.argv[2]
    n_days = int(sys.argv[3])
    rand_seed = sys.argv[4]

    test_sweep(pop_size=pop_size, pop_infected=pop_infected, n_days=n_days, rand_seed=rand_seed, pop_type='hybrid')