import os
import matplotlib
from sys import platform
if platform == "linux" or platform == "linux2":
    print('Linux OS. Using non-interactive Agg backend')
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import math

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class TimeseriesAnalyzer(IAnalyzer):
    data_group_names = ['group', 'tags', 'sim_id', 'channel']
    ordered_levels = ['channel', 'group', 'tags', 'sim_id']
    output_file = 'timeseries.csv'
    diff_filename = 'timeseries_diff.csv'

    def __init__(self, filenames=[os.path.join('output', 'InsetChart.json')], channels=('Statistical Population',
                                                                                        'Infectious Population',
                                                                                        'Waning Population',
                                                                                        'Campaign Cost',
                                                                                        'New Infections',
                                                                                        'Symptomatic Population'),
                 save_output=True, working_dir="."):

        super(TimeseriesAnalyzer, self).__init__(filenames=filenames, working_dir=working_dir)
        self.channels = set(channels)
        self.save_output = save_output

    def default_select_fn(self, ts):
        return pd.Series(ts)

    def default_group_fn(self, k, v):
        if isinstance(v, dict):
            v.pop('Run_Number', None)
        if v:
            return str(k) + "_" + str(v)
        else:
            return str(k)

    def default_compare_and_plot_fn(self, df, ax):
        grouped = df.groupby(level=['group'], axis=1)
        m = grouped.mean()
        m.plot(ax=ax, legend=False)
        group_names = m.columns
        if len(group_names) == 2: # not the best way to do, but work for now.
            m['diff'] = m[group_names[1]] - m[group_names[0]]
            m['diff'] =m['diff'].abs()
            return m['diff']

    def default_filter_fn(self, md):
        return True

    def filter(self, simulation):
        return self.default_filter_fn(simulation.tags)

    def get_channel_data(self, data_by_channel, selected_channels):
        channel_series = [self.default_select_fn(data_by_channel[channel]["Data"]) for channel in selected_channels]
        return pd.concat(channel_series, axis=1, keys=selected_channels)

    def map(self, data, simulation):
        mdata = data[self.filenames[0]]['Header']
        start_time = mdata["Start_Time"]
        cdata = data[self.filenames[0]]['Channels']
        if start_time > 0:
            for key, value in cdata.items():
                value['Data'] = np.append([math.nan] * start_time, value['Data'])

        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()
        return self.get_channel_data(cdata, selected_channels)

    def compare_and_plot_by_channel(self, channels, compare_and_plot_fn):
        ncol = int(1 + len(channels) / 4)
        nrow = int(np.ceil(float(len(channels)) / ncol))

        fig, axs = plt.subplots(figsize=(max(6, min(8, 4 * ncol)), min(6, 3 * nrow)), nrows=nrow, ncols=ncol,
                                sharex=True)

        flat_axes = [axs] if ncol * nrow == 1 else axs.flat

        compare_result = {}
        for (channel, ax) in zip(channels, flat_axes):
            ax.set_title(channel)
            m = compare_and_plot_fn(channel, ax)
            if m is not None:
                compare_result[channel] = m
        return compare_result


    def reduce(self, all_data):
        selected = []
        for sim, data in all_data.items():
            # Enrich the data with info
            #data.group = self.default_group_fn(str(sim.uid).split('-')[0], sim.tags)
            exp = sim.experiment
            data.group = self.default_group_fn(exp.name, sim.tags)
            #data.group = sim.parent_id
            data.tags = str(sim.tags)
            data.sim_id = sim.uid
            selected.append(data)

        if len(selected) == 0:
            print("\n No data have been returned... Exiting...")
            return

        # Combining selected data...
        combined = pd.concat(selected, axis=1,
                             keys=[(d.group, d.tags, d.sim_id) for d in selected],
                             names=self.data_group_names)

        # Re-ordering multi-index levels...
        data = combined.reorder_levels(self.ordered_levels, axis=1).sort_index(axis=1)

        def compare_and_plot_fn(channel, ax):
            return self.default_compare_and_plot_fn(data[channel].dropna(), ax)

        channels = data.columns.levels[0]
        compare_result = self.compare_and_plot_by_channel(channels, compare_and_plot_fn)

        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5,
                   fontsize='xx-small')

        # analyzer_path = os.path.dirname(__file__)
        current_path = os.getcwd()

        # plt.show()
        plt.savefig(os.path.join(current_path, 'timeseries.png'))

        # save results to csv files
        if compare_result:
            df = pd.DataFrame.from_dict(compare_result)
            df.to_csv(os.path.join(current_path, self.diff_filename))

        if self.save_output:
            data.to_csv(os.path.join(current_path, self.output_file))


if __name__ == "__main__":
    platform = Platform('COMPS2')

    exp_id = '3dda8b9b-b5ea-e911-a2be-f0921c167861'  # comps2 exp_id

    filenames = ['output/InsetChart.json']
    analyzers = [TimeseriesAnalyzer(filenames=filenames)]

    manager = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    manager.analyze()
