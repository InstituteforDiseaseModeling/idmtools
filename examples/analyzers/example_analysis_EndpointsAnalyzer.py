# Example Analyzer for EMOD Experiment
# In this example, we will demonstrate how to create an analyzer to analyze EMOD output files

# First, import some necessary system and idmtools packages.
import numpy as np
import pandas as pd
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer
from idmtools.core import ItemType


# Create a class for your analyzer
class EndpointsAnalyzer(IAnalyzer):
    def __init__(self, save_file=None):
        # Arg option for analyzer init are uid, working_dir, data in the method map (aka select_simulation_data),
        # and filenames
        # In this case, we want to provide a filename to analyze
        self.filenames = ['output\\InsetChart.json']
        super().__init__(filenames=self.filenames)

        # Create a variable to save the results of the analysis to file
        self.save_file = save_file

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    # In this case, we want to get specific Channels for a range of simulations
    def map(self, data, simulation):
        y = np.array([])
        cases = np.array([])
        infections = np.array([])
        EIR = np.array([])
        prev = np.array([])

        for j in range(7):  # 7-year simulations:
            s = j * 365
            e = (j + 1) * 365
            cases_array = np.array(data[self.filenames[0]]["Channels"]["New Clinical Cases"]["Data"][s:e])
            infec_array = np.array(data[self.filenames[0]]["Channels"]["New Infections"]["Data"][s:e])
            EIR_array = np.array(data[self.filenames[0]]["Channels"]["Daily EIR"]["Data"][s:e])
            RDT_prev_arr = np.array(data[self.filenames[0]]["Channels"]["Blood Smear Parasite Prevalence"]["Data"][s:e])

            y = np.append(y, j + 2010)
            cases = np.append(cases, np.sum(cases_array))
            infections = np.append(infections, np.sum(infec_array))
            EIR = np.append(EIR, np.sum(EIR_array))
            prev = np.append(prev, np.average(RDT_prev_arr))

            # Special entry for mid-2015 to mid-2016
            s = 5 * 365 + 182
            e = 6 * 365 + 182
            cases_array = np.array(data[self.filenames[0]]["Channels"]["New Clinical Cases"]["Data"][s:e])
            infec_array = np.array(data[self.filenames[0]]["Channels"]["New Infections"]["Data"][s:e])
            EIR_array = np.array(data[self.filenames[0]]["Channels"]["Daily EIR"]["Data"][s:e])
            RDT_prev_arr = np.array(data[self.filenames[0]]["Channels"]["Blood Smear Parasite Prevalence"]["Data"][s:e])

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

            # And get the tags identifying the simulation
            for tag in simulation.tags:
                sim_data[tag] = simulation.tags[tag]

            return pd.DataFrame(sim_data)

    # In combine, you are combining all the data returned from simulation puts and then output to pandas dataframe
    def combine(self, all_data):
        data_list = []
        for sim in all_data.keys():
            data_list.append(all_data[sim])

        return pd.concat(data_list)

    # In reduce here, we are saving the combined data to a csv file to keep a record  of all our filtered sim outputs
    def reduce(self, all_data):
        sim_data_full = self.combine(all_data)
        print("all_data ", all_data)
        print("sim_data_full ", sim_data_full)
        if self.save_file:
            sim_data_full.to_csv(self.save_file, index=False)
        return sim_data_full


if __name__ == "__main__":

    # Set the platform where you want to run your analysis
    with Platform('CALCULON') as platform:

        # Set the experiment you want to analyze
        exp_id = 'adad3ad2-4304-eb11-a2c7-c4346bcb1553'  # comps exp id

        # Initialize the analyser class with the name of file to save to and start the analysis
        analyzers = [EndpointsAnalyzer(save_file="endpoints_{}.csv".format(exp_id))]

        # Specify the id Type, in this case an Experiment
        manager = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        manager.analyze()
