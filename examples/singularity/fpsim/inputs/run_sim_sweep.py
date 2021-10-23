'''
Simple script for running Covasim
'''
import os
import sys

import fpsim as fp
import fp_analyses.senegal_parameters as sp
import sciris as sc
import sim_to_inset

import numpy as np
from scipy import interpolate as si
import fpsim.defaults as fpd


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

    # This code doesn't work because I don't know how to index in numpy.
    # pars['age_fecundity']['f'][3] = fecundity_20
    # pars['age_fecundity']['f'][4] = fecundity_25
    # pars['age_fecundity']['f'][5] = fecundity_30

    # code ganked from fp.senegal_parameters.py
    fecundity = {
        'bins': np.array([0., 5, 10, 20, 25, 28, 31, 34, 37, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]),
        'f': np.array([0., 0, 0, fecundity_20, fecundity_25, fecundity_30, 76.6, 74.8, 67.4, 55.5, 7.9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])}
    fecundity[
        'f'] /= 100  # Conceptions per hundred to conceptions per woman over 12 menstrual cycles of trying to conceive

    fecundity_interp_model = si.interp1d(x=fecundity['bins'], y=fecundity['f'])
    fecundity_interp = fecundity_interp_model(fpd.spline_ages)
    fecundity_interp = np.minimum(1, np.maximum(0, fecundity_interp))
    pars['age_fecundity'] = fecundity_interp


    sexual_activity_20 = sexual_activity_20_25 * 0.71 # matching approximate ration of default 35.5/49.6
    sexual_activity_25 = sexual_activity_20_25
    sexual_activity_30 = sexual_activity_20_25 * 1.16 # matching approximate ration of default 57.4/49.6

    # This code doesn't work because I don't know how to index in numpy
    # pars['sexual_activity'][1][4] = sexual_activity_20
    # pars['sexual_activity'][1][5] = sexual_activity_25
    # pars['sexual_activity'][1][6] = sexual_activity_30

    sexually_active = np.array([[0, 5, 10, 15,  20,   25,   30,   35,   40,    45,   50],
                                [0, 0,  0,  11.5, sexual_activity_20, sexual_activity_25, sexual_activity_30, 64.4, 64.45, 64.5, 66.8]])

    sexually_active[1] /= 100 # Convert from percent to rate per woman
    activity_ages = sexually_active[0]
    activity_interp_model = si.interp1d(x=activity_ages, y=sexually_active[1])
    activity_interp = activity_interp_model(fpd.spline_preg_ages)  # Evaluate interpolation along resolution of ages
    pars['sexual_activity'] = activity_interp

    pars['seed'] = rand_seed

    # Set the output directory path
    outputs = "outputs"
    if not os.path.exists(outputs):
        os.makedirs(outputs)

    # Make, run, and plot the sim
    sim = fp.Sim(pars=pars)
    sim.run()
    sim_to_inset.create_insetchart(sc.jsonify(sim.results))
    sim.plot()

if __name__ == '__main__':
    sex_base = int(sys.argv[1])
    fecundity_peak = int(sys.argv[2])
    seed = int(sys.argv[3])

    test_sweep(sexual_activity_20_25=sex_base, fecundity_peak_25=fecundity_peak, rand_seed=seed)
