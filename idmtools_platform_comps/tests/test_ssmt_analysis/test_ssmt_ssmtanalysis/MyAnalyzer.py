import json
import os

try:
    # use idmtools image
    from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

from dtk.utils.analyzers import default_select_fn, default_group_fn, plot_by_channel, default_plot_fn

import matplotlib as mpl
import pandas as pd
mpl.use('Agg')


class MyAnalyzer(BaseAnalyzer):
    def __init__(self, file_name=None, channels=None,
                 select_function=default_select_fn, group_function=default_group_fn, plot_function=default_plot_fn):
        super().__init__(working_dir='.')
        if file_name is None:
            self.filenames = (os.path.join('output', "InsetChart.json"),)
        else:
            self.filenames = (os.path.join('output', file_name),)

        if channels is None:
            self.channels = ['Statistical Population']
        else:
            self.channels = channels
        self.group_function = group_function
        self.select_function = select_function
        self.plot_function = plot_function

    def map(self, data, simulation):
        cdata = data[self.filenames[0]]['Channels']
        channel_series = [self.select_function(cdata[channel]["Data"]) for channel in self.channels]
        return pd.concat(channel_series, axis=1, keys=self.channels)

    def reduce(self, all_data):
        selected = []
        for sim, data in all_data.items():
            # Enrich the data with info
            data.group = self.group_function(sim.id, sim.tags)
            data.sim_id = sim.id
            selected.append(data)

        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        # Combining selected data...
        data_group_names = ['group', 'sim_id', 'channel']
        combined = pd.concat(selected, axis=1,
                             keys=[(d.group, d.sim_id) for d in selected],
                             names=data_group_names)

        # Re-ordering multi-index levels...
        ordered_levels = ['channel', 'group', 'sim_id']
        data = combined.reorder_levels(ordered_levels, axis=1).sort_index(axis=1)

        data.to_csv('channels.csv')

        def plot_fn(channel, ax):
            self.plot_function(data[channel].dropna(), ax)

        channels = data.columns.levels[0]
        plot_by_channel(channels, plot_fn)

        import matplotlib.pyplot as plt
        plt.legend()
        plt.savefig(os.path.join(os.getcwd(), 'channels.png'))


