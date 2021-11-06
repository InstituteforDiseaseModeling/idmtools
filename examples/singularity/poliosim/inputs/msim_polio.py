
import json
import os

import poliosim as ps
import sim_to_inset

channels = [
    'n_naive',
    'n_exposed',
    'n_is_shed',
    'n_symptomatic',
    'n_diagnosed',
    'n_quarantined',
    'n_recovered',
    'prevalence',
    'incidence',
    'r_eff',
    'doubling_time'
]


def test_msim(seeds, scale_betas, pop_infecteds):
    sim_list = []
    sim_index = 0
    sim_legend = []
    for seed in seeds:
        for scale_beta in scale_betas:
            beta = 0.0002 * scale_beta  # scale_beta doesn't do anything, so adding it here.
            for pop_infected in pop_infecteds:
                sim_list.append(
                    ps.Sim(
                        pop_size=10_000,
                        n_days=50,
                        pop_infected=pop_infected,
                        beta=beta,
                        rand_seed=seed
                    )
                )
                legend = {
                    'index': sim_index,
                    'infected': pop_infected,
                    'scale_beta': scale_beta,
                    'seed': seed
                }
                sim_legend.append(legend)
                sim_index += 1

    suite = ps.MultiSim(sims=sim_list)
    suite.run()

    os.mkdir('outputs')

    with open('sim_legend.json', 'w') as outfile:
        json.dump(sim_legend, outfile, indent=4, sort_keys=True)

    for i in range(len(suite.sims)):
        sim_to_inset.create_insetchart(suite.sims[i].results, n=i, dir='outputs')


if __name__ == '__main__':
    test_msim(seeds=range(10),
              scale_betas=[0.2, 0.5, 1.0],
              pop_infecteds=[10, 50, 100]
              )
