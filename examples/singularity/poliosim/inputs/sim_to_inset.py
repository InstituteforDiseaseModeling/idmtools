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


def create_insetchart(results, n=0):
    sim_results = {k: results[k].values.tolist() for k in channels}

    sim_results['t'] = results['t']
    df = pd.DataFrame.from_dict(sim_results)
    if n == 0:
        df.to_csv('InsetChart.csv', index=True)
    else:
        df.to_csv('InsetChart'+str(n)+ '.csv', index=True)
    return

# For more poliosim timeseries, look to poliosim\tests\baseline.json
