# First, import some necessary system and idmtools packages.
import os
from sys import platform
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
if platform == "linux" or platform == "linux2":
    print('Linux OS. Using non-interactive Agg backend')
    matplotlib.use('Agg')


# Create a class for individual level analyzer
class InfectiousnessCSVAnalyzer(BaseAnalyzer):

    def __init__(self, filenames, channel="infectiousness", filter_by='is_infected'):
        super().__init__(filenames=filenames)
        self.channel = channel
        self.filter_by = filter_by
        # Raise exception early if files are not csv files
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data, simulation):
        # Filter by filenames in this analyzer
        my_data = [data[filename] for filename in self.filenames]
        # If there are 1 to many csv files, concatenate csv data columns into one dataframe
        # Collect the infectiousness data when is_infected is True only
        concatenated_df = pd.concat([channel_data[channel_data[self.filter_by] == 1][self.channel] for
                                     channel_data in my_data],
                                    axis=0, ignore_index=True, sort=True)
        return concatenated_df

    # In reduce, we are printing and plotting the simulation and result data filtered in map
    def reduce(self, all_data):
        # Let's hope the first simulation is representative
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = str(first_sim.experiment.id)  # Set the exp id from the first sim data
        keys = []
        for k in all_data.keys():
            if 'simulation_name_tag' in k.tags:
                k.tags.pop('simulation_name_tag')
            keys.append(str(k.tags))
        results = pd.concat(list(all_data.values()), axis=0,  # Combine a list of all the sims csv data column values
                            keys=keys,  # Add a hierarchical index with the keys option
                            names=['SimTags'])  # Using Simulation tags as the keys
        results.index = results.index.droplevel(1)  # Remove default index

        # Make a directory labeled the exp id to write the csv results to
        os.makedirs(exp_id, exist_ok=True)
        # NOTE: If running twice with different filename, the output files will collide
        results.to_csv(os.path.join(exp_id, self.__class__.__name__ + '.csv'))

        sims = results.index.unique().to_list()
        fig, ax = plt.subplots()

        # Plot
        for sim in sims:
            # Filter data by sim tags and then generate the kernel density estimation plot
            results[results.index == sim].plot.kde(bw_method='scott', ax=ax, label=str(sim))
            # sns.distplot() would generate a prettier kde plot but seaborn is not a required library in idmtools.
            # import seaborn as sns
            # sns.distplot(results[results.index==sim], kde=True, hist=False, ax=ax, label=str(sim))
        plt.legend(loc=0, fontsize='xx-small')
        ax.set_title(self.channel + "(kde)")
        ax.set_ylim(bottom=0)
        # Save the figure
        plt.savefig(os.path.join(exp_id, self.__class__.__name__ + '.png'))
