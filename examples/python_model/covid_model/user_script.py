"""
Simple script for running the Covid-19 agent-based model
"""

import datetime as dt

import pylab as pl
import sciris as sc

import covid_seattle

print('Setting up...')

pars = covid_seattle.make_pars()

# Other options
verbose = False
n = 12
xmin = pars['day_0']
xmax = xmin + pars['n_days']
noise = 0 * 0.2  # Turn off noise
seed = 1
reskeys = ['cum_exposed', 'n_exposed']

fn_fig = 'seattle-covid-projections_2020mar10e_v2.png'
fn_obj = 'seattle-projection-results_v4e.obj'

scenarios = {
    '25': '25% contact reduction',
    '50': '50% contact reduction',
    '75': '75% contact reduction',
}

sc.tic()

if __name__ == "__main__":

    print('Baseline run')

    # Set up a simulation
    orig_sim = covid_seattle.Sim()
    orig_sim.set_seed(seed)
    finished_sims = covid_seattle.multi_run(orig_sim, n=n, noise=noise)

    res0 = finished_sims[0].results
    npts = len(res0[reskeys[0]])
    tvec = xmin + res0['t']

    both = {}
    for key in reskeys:
        both[key] = pl.zeros((npts, n))
    for key in reskeys:
        for s, sim in enumerate(finished_sims):
            both[key][:, s] = sim.results[key]

    best = {}
    low = {}
    high = {}
    for key in reskeys:
        best[key] = pl.median(both[key], axis=1) * orig_sim['scale']
        low[key] = both[key].min(axis=1) * orig_sim['scale']
        high[key] = both[key].max(axis=1) * orig_sim['scale']

    final = sc.objdict()
    final['Baseline'] = sc.objdict(
        {'scenname': 'Business as ususal', 'best': sc.dcp(best), 'low': sc.dcp(low), 'high': sc.dcp(high)})

    for scenkey, scenname in scenarios.items():

        scen_sim = covid_seattle.Sim()
        scen_sim.set_seed(seed)
        if scenkey == '25':
            scen_sim['quarantine'] = 17
            scen_sim['quarantine_eff'] = 0.75
        elif scenkey == '50':
            scen_sim['quarantine'] = 17
            scen_sim['quarantine_eff'] = 0.50
        elif scenkey == '75':
            scen_sim['quarantine'] = 17
            scen_sim['quarantine_eff'] = 0.25

        print(f'Multirun for {scenkey}')

        scen_sims = covid_seattle.multi_run(scen_sim, n=n, noise=noise)

        print(f'Processing {scenkey}')

        scenboth = {}
        for key in reskeys:
            scenboth[key] = pl.zeros((npts, n))
            for s, sim in enumerate(scen_sims):
                scenboth[key][:, s] = sim.results[key]

        scen_best = {}
        scen_low = {}
        scen_high = {}
        for key in reskeys:
            scen_best[key] = pl.median(scenboth[key], axis=1) * orig_sim['scale']
            scen_low[key] = scenboth[key].min(axis=1) * orig_sim['scale']
            scen_high[key] = scenboth[key].max(axis=1) * orig_sim['scale']

        final[scenkey] = sc.objdict(
            {'scenname': scenname, 'best': sc.dcp(scen_best), 'low': sc.dcp(scen_low), 'high': sc.dcp(scen_high)})

    print('Plotting')

    fig_args = {'figsize': (16, 12)}
    plot_args = {'lw': 3, 'alpha': 0.7}
    scatter_args = {'s': 150, 'marker': 's'}
    axis_args = {'left': 0.10, 'bottom': 0.1, 'right': 0.95, 'top': 0.95, 'wspace': 0.2, 'hspace': 0.25}
    fill_args = {'alpha': 0.3}
    font_size = 18
    fig = pl.figure(**fig_args)
    pl.subplots_adjust(**axis_args)
    pl.rcParams['font.size'] = font_size

    # Create the tvec based on the results
    tvec = xmin + pl.arange(len(final['Baseline']['best'][reskeys[0]]))

    for key, data in final.items():
        print(key)
        if key in scenarios:
            scenname = scenarios[key]
        else:
            scenname = data['scenname']

        # %% Plotting
        for k, key in enumerate(reskeys):
            pl.subplot(len(reskeys), 1, k + 1)
            pl.plot(tvec, data['best'][key], label=scenname, **plot_args)

            interv_col = [0.5, 0.2, 0.4]

            if key == 'cum_exposed':
                sc.setylim()
                pl.title('Cumulative infections', fontweight='bold')
                pl.legend()
                pl.text(xmin + 16.5, 12000, 'Intervention', color=interv_col, fontstyle='italic')

            elif key == 'n_exposed':
                sc.setylim()
                pl.title('Active infections', fontweight='bold')

            pl.grid(True)

            pl.plot([xmin + 16] * 2, pl.ylim(), '--', lw=2, c=interv_col)  # Plot intervention
            pl.xlabel('Date', fontweight='bold')
            pl.ylabel('Count', fontweight='bold')
            pl.gca().set_xticks(pl.arange(xmin, xmax + 1, 7))

            xt = pl.gca().get_xticks()
            print(xt)
            lab = []
            for t in xt:
                tmp = dt.datetime(2020, 1, 1) + dt.timedelta(days=int(t))  # + pars['day_0']
                print(t, tmp)

                lab.append(tmp.strftime('%B %d'))
            pl.gca().set_xticklabels(lab)

            sc.commaticks(axis='y')

    pl.savefig(f'seattle_projections_v3.png')

    # %% Print statistics
    for k in list(scenarios.keys()):
        for key in reskeys:
            print(f'{k} {key}: {final[k].best[key][-1]:0.0f}')

    pl.savefig(fn_fig, dpi=100)
    sc.saveobj(fn_obj, final)

    sc.toc()
    pl.show()
