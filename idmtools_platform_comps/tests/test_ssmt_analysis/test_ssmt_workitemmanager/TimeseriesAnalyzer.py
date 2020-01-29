import os

import pandas as pd

from dtk.utils.analyzers import default_select_fn, default_group_fn, default_filter_fn, plot_by_channel, default_plot_fn
from dtk.utils.analyzers.plot import plot_by_channel

try:
    # use idmtools image
    from idmtools.entities.ianalyzer import IAnalyzer as BaseAnalyzer
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.BaseAnalyzers.BaseAnalyzer import BaseAnalyzer

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class TimeseriesAnalyzer(BaseAnalyzer):
    data_group_names = ['group', 'sim_id', 'channel']
    ordered_levels = ['channel', 'group', 'sim_id']
    output_file = 'timeseries.csv'

    def __init__(self, filename=os.path.join('output', 'InsetChart.json'), filter_function=default_filter_fn,
                 select_function=default_select_fn, group_function=default_group_fn, plot_function=default_plot_fn,
                 channels=('Statistical Population',
                           'Rainfall', 'Adult Vectors',
                           'Daily EIR', 'Infected',
                           'Air Temperature'), saveOutput=False):
        super(TimeseriesAnalyzer, self).__init__(filenames=(filename,))
        self.channels = set(channels)
        self.group_function = group_function
        self.filter_function = filter_function
        self.select_function = select_function
        self.plot_function = plot_function
        self.saveOutput = saveOutput
        self.dir_name = "output"

    def filter(self, simulation):
        return self.filter_function(simulation.tags)

    def get_channel_data(self, data_by_channel, selected_channels, header):
        channel_series = [self.select_function(data_by_channel[channel]["Data"]) for channel in selected_channels]
        return pd.concat(channel_series, axis=1, keys=selected_channels)

    def select_simulation_data(self, data, simulation):
        cdata = data[self.filenames[0]]['Channels']
        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()
        return self.get_channel_data(cdata, selected_channels, data[self.filenames[0]]["Header"])

    def finalize(self, all_data):
        #import matplotlib.pyplot as plt


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
        combined = pd.concat(selected, axis=1,
                             keys=[(d.group, d.sim_id) for d in selected],
                             names=self.data_group_names)

        # Re-ordering multi-index levels...
        data = combined.reorder_levels(self.ordered_levels, axis=1).sort_index(axis=1)

        output_path = os.path.join(self.working_dir, self.dir_name)
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        if self.saveOutput:
            data.to_csv(os.path.join(output_path,self.output_file))

        def plot_fn(channel, ax):
            self.plot_function(data[channel].dropna(), ax)

        channels = data.columns.levels[0]
        #self.plot_by_channel(channels, plot_fn)
        plot_by_channel(channels, plot_fn)

        plt.legend()
        plt.savefig(os.path.join(output_path, 'timeseries.png'))


