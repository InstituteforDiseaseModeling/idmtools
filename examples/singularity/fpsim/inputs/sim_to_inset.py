import pandas as pd


def create_insetchart(results_json, n=0):
    sim_results = {k: results_json[k] for k in ['births', 'maternal_deaths', 'infant_deaths','t','on_method','total_women_fecund']}
    df = pd.DataFrame.from_dict(sim_results)
    if n == 0:
        df.to_csv('InsetChart.csv', index=True)
    else:
        df.to_csv('InsetChart'+str(n)+ '.csv', index=True)
    return