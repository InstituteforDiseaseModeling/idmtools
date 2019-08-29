import sys
import numpy as np
import pandas as pd
#from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.managers import AnalyzeManager
from idmtools.analysis.AddAnalyzer import AddAnalyzer
from idmtools.entities import IAnalyzer
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform

from idmtools.utils.entities import retrieve_experiment


class EndpointsAnalyzer(IAnalyzer):
    def __init__(self, save_file=None):
        # self.reference should be a dataframe with columns: node/round/date/prev/N
        filenames = ['output/ReportMalariaFilteredCatchment.json']
        super().__init__(filenames=filenames)

        self.save_file = save_file

    def map(self, data, simulation):
        y = np.array([])
        cases = np.array([])
        infections = np.array([])
        EIR = np.array([])
        prev = np.array([])

        for j in range(7):  # 7-year simulations:
            s = j * 365
            e = (j + 1) * 365
            cases_array = np.array(data[self.filenames[0]]["Channels"]["Infected"]["Data"][s:e])
            infec_array = np.array(data[self.filenames[0]]["Channels"]["New Infections"]["Data"][s:e])
            EIR_array = np.array(data[self.filenames[0]]["Channels"]["Daily (Human) Infection Rate"]["Data"][s:e])
            RDT_prev_arr = np.array(data[self.filenames[0]]["Channels"]["Newly Symptomatic"]["Data"][s:e])

            y = np.append(y, j + 2010)
            cases = np.append(cases, np.sum(cases_array))
            infections = np.append(infections, np.sum(infec_array))
            EIR = np.append(EIR, np.sum(EIR_array))
            prev = np.append(prev, np.average(RDT_prev_arr))

        # Special entry for mid-2015 to mid-2016
        s = 5 * 365 + 182
        e = 6 * 365 + 182
        cases_array = np.array(data[self.filenames[0]]["Channels"]["Infected"]["Data"][s:e])
        infec_array = np.array(data[self.filenames[0]]["Channels"]["New Infections"]["Data"][s:e])
        EIR_array = np.array(data[self.filenames[0]]["Channels"]["Daily (Human) Infection Rate"]["Data"][s:e])
        RDT_prev_arr = np.array(data[self.filenames[0]]["Channels"]["Newly Symptomatic"]["Data"][s:e])

        y = np.append(y, 2015.5)
        cases = np.append(cases, np.sum(cases_array))
        infections = np.append(infections, np.sum(infec_array))
        EIR = np.append(EIR, np.sum(EIR_array))
        prev = np.append(prev, np.average(RDT_prev_arr))

        sim_data = {
            "year": y,
            "cases": cases,
            "infections": infections,
            "EIR": EIR,
            "avg_RDT_prev": prev}
        # for tag in ["catch", "sample", "arab", "funest", "itn", "irs", "msat", "mda", "chw_hs", "chw_rcd", "Run_Number"]:
        for tag in simulation.tags:
            sim_data[tag] = simulation.tags[tag]

        return pd.DataFrame(sim_data)

    def combine(self, all_data):
        data_list = []
        for sim in all_data.keys():
            data_list.append(all_data[sim])

        return pd.concat(data_list)

    def reduce(self, all_data):
        sim_data_full = self.combine(all_data)
        print("all_data ",all_data)
        print("sim_data_full ", sim_data_full)
        if self.save_file:
            sim_data_full.to_csv(self.save_file, index=False)
        return sim_data_full

if __name__ == "__main__":
    exp_id = '8deacaaf-30c9-e911-a2bb-f0921c167866'

    p = COMPSPlatform()
    am = AnalyzeManager(experiments=[exp_id],
                        analyzers=[EndpointsAnalyzer(save_file="endpoints_{}.csv".format(exp_id))],
                        platform=p)
    # am.add_analyzer(EndpointsAnalyzer(save_file="endpoints_{}.csv".format(expid)))
    exp = retrieve_experiment(exp_id)
    am.analyze()
