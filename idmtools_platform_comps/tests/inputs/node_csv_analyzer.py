# First, import some necessary system and idmtools packages.
import os
from sys import platform
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
if platform == "linux" or platform == "linux2":
    print('Linux OS. Using non-interactive Agg backend')
    matplotlib.use('Agg')


# Create a class for node level analyzer
class NodeCSVAnalyzer(BaseAnalyzer):
    def __init__(self, filenames):
        super().__init__(filenames=filenames)
        # Raise exception early if files are not csv files
        if not all(['csv' in os.path.splitext(f)[1].lower() for f in self.filenames]):
            raise Exception('Please ensure all filenames provided to CSVAnalyzer have a csv extension.')

    # Map is called to get for each simulation a data object (all the metadata of the simulations) and simulation object
    def map(self, data, simulation):
        # If there are 1 to many csv files, concatenate csv data columns into one dataframe
        # filter the data by filenames (data could contains data/dataframe from other analyzers within the same AnalyzerManager)
        concatenated_df = pd.concat([data[filename] for filename in self.filenames],
                                    axis=0, ignore_index=True, sort=True)
        return concatenated_df

    # In reduce, we are printing and plotting the simulation and result data filtered in map
    def reduce(self, all_data):
        # Let's hope the first simulation is representative
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = str(first_sim.experiment.id)  # Set the exp id from the first sim data

        results = pd.concat(list(all_data.values()), axis=0,  # Combine a list of all the sims csv data column values
                            keys=[str(k.uid) for k in all_data.keys()],  # Add a hierarchical index with the keys option
                            names=['SimId'])  # Label the index keys you create with the names option

        results.index = results.index.droplevel(1)  # Remove default index

        # Make a directory labeled the exp id to write the csv results to
        os.makedirs(exp_id, exist_ok=True)
        # NOTE: If running twice with different filename, the output files will collide
        results.to_csv(os.path.join(exp_id, self.__class__.__name__ + '.csv'))

        channels = results.drop(['TimeStep'], axis=1).columns.tolist()
        sims = results.index.unique().to_list()
        # Create the sub plots
        ncol = int(len(channels) / 2)
        nrow = int(np.ceil(float(len(channels)) / ncol))
        figsize = (max(10, min(10, 8 * ncol)), min(10, 6 * nrow))
        fig, axs = plt.subplots(figsize=figsize, nrows=nrow, ncols=ncol, sharex=True)
        flat_axes = [axs] if ncol * nrow == 1 else axs.flat

        # Plot
        for channel, ax in zip(channels, flat_axes):
            ax.set_title(channel)
            ax.set_xlabel("TimeStep")
            for sim in sims:
                ax.plot(results[results.index == sim]['TimeStep'], results[results.index == sim][channel])

        # Create the legend
        sims_label = [str(sim).split('-')[0] for sim in sims]
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5,
                   fontsize='xx-small', labels=sims_label)

        # Save the figure
        plt.savefig(os.path.join(exp_id, self.__class__.__name__ + '.png'))
