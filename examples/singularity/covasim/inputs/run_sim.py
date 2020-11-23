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

# Configure the sim -- can also just use a normal dictionary
pars = sc.objdict(
    pop_size     = 10000,    # Population size
    pop_infected = 10,       # Number of initial infections
    n_days       = 120,      # Number of days to simulate
    rand_seed    = 1,        # Random seed
    pop_type     = 'hybrid', # Population to use -- "hybrid" is random with household, school,and work structure
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