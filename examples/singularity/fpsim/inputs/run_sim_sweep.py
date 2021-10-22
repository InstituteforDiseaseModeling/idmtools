'''
Simple script for running Covasim
'''
import os
import sys

import fpsim as fp
import fp_analyses.senegal_parameters as sp
import fp_analyses.test_parameters as tp
import sciris as sc
import sim_to_inset

sys.path.insert(0, os.path.dirname(__file__))

# Run options
do_plot = 1
verbose = 1
interv  = 1


def test_sweep(sexual_activity_20_25=50, fecundity_peak_25=79, rand_seed=1):
    senegal_pars = sp.make_pars()
    pars = sc.dcp(senegal_pars)
    fecundity_20 = fecundity_peak_25 * 0.89 # matching approximate ratio of default 70.8/79.3
    fecundity_25 = fecundity_peak_25
    fecundity_30 = fecundity_peak_25 * 0.99 # matching approximate ratio of default 77.9/79.3
    pars['age_fecundity']['f'][3] = fecundity_20
    pars['age_fecundity']['f'][4] = fecundity_25
    pars['age_fecundity']['f'][5] = fecundity_30

    sexual_activity_20 = sexual_activity_20_25 * 0.71 # matching approximate ration of default 35.5/49.6
    sexual_activity_25 = sexual_activity_20_25
    sexual_activity_30 = sexual_activity_20_25 * 1.16 # matching approximate ration of default 57.4/49.6
    pars['sexual_activity'][1][4] = sexual_activity_20
    pars['sexual_activity'][1][5] = sexual_activity_25
    pars['sexual_activity'][1][6] = sexual_activity_30

    pars['seed'] = rand_seed
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