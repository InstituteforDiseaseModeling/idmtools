import pandas as pd

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


def create_insetchart(results, n=0, dir=None):
    sim_results = {k: results[k].values.tolist() for k in channels}

    sim_results['t'] = results['t']
    df = pd.DataFrame.from_dict(sim_results)

    if n > 0:
        csv_name = f'InsetChart{str(n)}.csv'
    else:
        csv_name = f'InsetChart.csv'
    if dir:
        csv_full_name = f'./{dir}/{csv_name}'
    else:
        csv_full_name = csv_name
    df.to_csv(csv_full_name, index=True)
    return

# For more poliosim timeseries, look to poliosim\tests\baseline.json
