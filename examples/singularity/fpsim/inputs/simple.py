'''
Simple example usage for FPsim
'''

import fpsim as fp
import fp_analyses.senegal_parameters as sp
import sciris as sc
import sim_to_inset

# Set options
do_plot = True
pars = sp.make_pars()
pars['n'] = 500 # Small population size
pars['end_year'] = 2020 # 1961 - 2020 is the normal date range
pars['exposure_correction'] = 1.0 # Overall scale factor on probability of becoming pregnant

sim = fp.Sim(pars=pars)
sim.run()
sim_to_inset.create_insetchart(sc.jsonify(sim.results))


if do_plot:
    sim.plot()

print('Done.')
