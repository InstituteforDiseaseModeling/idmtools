import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class TimeseriesAnalyzer(IAnalyzer):
    data_group_names = ['group', 'sim_id', 'channel']
    ordered_levels = ['channel', 'group', 'sim_id']
    output_file = 'timeseries.csv'

    def __init__(self, filenames=[os.path.join('output', 'InsetChart.json')], channels=('Statistical Population',
                                                                                        'Infectious Population',
                                                                                        'Infected',
                                                                                        'Waning Population'),
                 save_output=True, working_dir="."):

        super(TimeseriesAnalyzer, self).__init__(filenames=filenames, working_dir=working_dir)
        self.channels = set(channels)
        self.save_output = save_output

    def default_select_fn(self, ts):
        return pd.Series(ts)

    def default_group_fn(self, k, v):
        return k

    def default_plot_fn(self, df, ax):
        grouped = df.groupby(level=['group'], axis=1)
        m = grouped.mean()
        m.plot(ax=ax, legend=False)

    def default_filter_fn(self, md):
        return True

    def filter(self, simulation):
        return self.default_filter_fn(simulation.tags)

    def get_channel_data(self, data_by_channel, selected_channels):
        channel_series = [self.default_select_fn(data_by_channel[channel]["Data"]) for channel in selected_channels]
        return pd.concat(channel_series, axis=1, keys=selected_channels)

    def map(self, data, simulation):
        cdata = data[self.filenames[0]]['Channels']
        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()
        return self.get_channel_data(cdata, selected_channels)

    def plot_by_channel(self, channels, plot_fn):

        import matplotlib.pyplot as plt

        ncol = int(1 + len(channels) / 4)
        nrow = int(np.ceil(float(len(channels)) / ncol))

        fig, axs = plt.subplots(figsize=(max(6, min(8, 4 * ncol)), min(6, 3 * nrow)), nrows=nrow, ncols=ncol,
                                sharex=True)

        flat_axes = [axs] if ncol * nrow == 1 else axs.flat
        for (channel, ax) in zip(channels, flat_axes):
            ax.set_title(channel)
            plot_fn(channel, ax)

    def reduce(self, all_data):
        selected = []
        for sim, data in all_data.items():
            # Enrich the data with info
            data.group = self.default_group_fn(sim.uid, sim.tags)
            data.sim_id = sim.uid
            selected.append(data)

        if len(selected) == 0:
            print("\n No data have been returned... Exiting...")
            return

        # Combining selected data...
        combined = pd.concat(selected, axis=1,
                             keys=[(d.group, d.sim_id) for d in selected],
                             names=self.data_group_names)

        # Re-ordering multi-index levels...
        data = combined.reorder_levels(self.ordered_levels, axis=1).sort_index(axis=1)

        analyzer_path = os.path.dirname(__file__)

        if self.save_output:
            data.to_csv(os.path.join(analyzer_path, self.output_file))

        def plot_fn(channel, ax):
            self.default_plot_fn(data[channel].dropna(), ax)

        channels = data.columns.levels[0]
        self.plot_by_channel(channels, plot_fn)

        plt.legend()
        # plt.show()
        plt.savefig(os.path.join(analyzer_path, 'timeseries.png'))


if __name__ == "__main__":
    platform = Platform('COMPS2')

    exp_id = '3dda8b9b-b5ea-e911-a2be-f0921c167861'  # comps2 exp_id

    filenames = ['output/InsetChart.json']
    analyzers = [TimeseriesAnalyzer(filenames=filenames)]

    manager = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    manager.analyze()
