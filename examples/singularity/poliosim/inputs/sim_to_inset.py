import pandas as pd
import sciris as sc

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

'''
    "new_infections": 0.0,
    "new_sus_para_infs": 0.0,
    "new_tests": 2.0,
    "new_diagnoses": 0.0,
    "new_recoveries": 0.0,
    "new_symptomatic": 0.0,
    "new_quarantined": 0.0,
    "new_symp_triggered_surveilled": 0.0,
'''
def create_insetchart(results, n=0):
    sim_results = {k: results[k].values.tolist() for k in channels}

    # TODO: remove this commented out loop. Here for debugging help.
    # sim_results = {}
    # for k in channels:
    #     print(k)
    #     channel = results[k]
    #     print(channel)
    #     values = channel.values
    #     print(values)
    #     values_list = values.tolist()
    #     sim_results[k] = values_list
    # sim_results_json = sc.jsonify(sim_results)
    # sim_results_json['t'] = results['t']

    sim_results['t'] = results['t']
    df = pd.DataFrame.from_dict(sim_results)
    if n == 0:
        df.to_csv('InsetChart.csv', index=True)
    else:
        df.to_csv('InsetChart'+str(n)+ '.csv', index=True)
    return

# For more poliosim timeseries, look to poliosim\tests\baseline.json