import pandas as pd


def create_insetchart(sim_json, n=0):
    sim_results = { k: sim_json['results'][k] for k in sim_json['results']['timeseries_keys']}
    df = pd.DataFrame.from_dict(sim_results)
    if n == 0:
        df.to_csv('InsetChart.csv', index=True)
    else:
        df.to_csv('InsetChart'+str(n)+ '.csv', index=True)
    return