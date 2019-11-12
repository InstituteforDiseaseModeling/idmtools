import os
from abc import ABCMeta, abstractmethod
from sys import platform

import matplotlib

if platform == "linux" or platform == "linux2":
    print('Linux OS. Using non-interactive Agg backend')
    matplotlib.use('Agg')

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import math

from idmtools.entities import IAnalyzer


def is_float(string):
    string = str(string)
    try:
        fl = float(string)
        if math.isnan(fl):
            return False
        return True
    except Exception:  # String is not a number
        return False


class CompareAnalyzer(IAnalyzer, metaclass=ABCMeta):
    data_group_names = ['group', 'tags', 'sim_id', 'channel']
    ordered_levels = ['channel', 'group', 'tags', 'sim_id']

    def __init__(self, filenames, output_file, diff_filename, png_filename, save_output=True):
        super().__init__(filenames=filenames)
        self.output_file = output_file
        self.diff_filename = diff_filename
        self.png_filename = png_filename
        self.save_output = save_output

    @abstractmethod
    def write_comparisons_to_disk(self):
        pass

    @abstractmethod
    def compare_and_plot(self, data, channels, flat_axes):
        pass

    @abstractmethod
    def interpret_results(self, tolerances, filename="results.txt"):
        pass

    def reduce(self, all_data: dict):
        selected = []
        for sim, data in all_data.items():
            # Enrich the data with info
            exp = sim.experiment

            sim.tags.pop('Run_Number', None)
            if sim.tags:
                data.group = str(exp.name) + "_" + str(sim.tags)
            else:
                data.group = exp.name

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

        channels = data.columns.levels[0]
        ncol = int(1 + len(channels) / 4)
        nrow = int(np.ceil(float(len(channels)) / ncol))

        fig, axs = plt.subplots(figsize=(max(6, min(8, 4 * ncol)), min(6, 3 * nrow)), nrows=nrow, ncols=ncol,
                                sharex=True)
        flat_axes = [axs] if ncol * nrow == 1 else axs.flat

        compare_result = self.compare_and_plot(data, channels, flat_axes)

        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5,
                   fontsize='xx-small')

        plt.savefig(os.path.join(self.working_dir, self.png_filename))

        self.results = compare_result

        # save results to csv files
        if compare_result:
            self.write_comparisons_to_disk()

        if self.save_output:
            data.to_csv(os.path.join(self.working_dir, self.output_file))

        return compare_result


class TimeseriesAnalyzer(CompareAnalyzer):
    def __init__(self, channels=None, save_output=True):

        super(TimeseriesAnalyzer, self).__init__(filenames=[os.path.join('output', 'InsetChart.json')],
                                                 png_filename='timeseries.png', output_file='timeseries.csv',
                                                 diff_filename='timeseries_diff.csv')

        self.channels = channels or ('Statistical Population',
                                     'Infectious Population',
                                     'Waning Population',
                                     'Campaign Cost',
                                     'New Infections',
                                     'Symptomatic Population')
        self.channels = set(self.channels)
        self.save_output = save_output

    def write_comparisons_to_disk(self):
        df = pd.DataFrame.from_dict(self.results)
        df.to_csv(os.path.join(self.working_dir, self.diff_filename))

    def compare_and_plot(self, data, channels, flat_axes):
        compare_result = {}
        for (channel, ax) in zip(channels, flat_axes):
            ax.set_title(channel)
            grouped = data[channel].groupby(level=['group'], axis=1)
            m = grouped.mean()
            m.plot(ax=ax, legend=False)
            group_names = m.columns
            if len(group_names) == 2:  # not the best way to do, but work for now.
                m['diff'] = m[group_names[1]] - m[group_names[0]]
                m['diff'] = m['diff'].abs()
                compare_result[channel] = m['diff']
        return compare_result

    def map(self, data, simulation):
        mdata = data[self.filenames[0]]['Header']
        start_time = mdata["Start_Time"]
        cdata = data[self.filenames[0]]['Channels']
        if start_time > 0:
            for key, value in cdata.items():
                value['Data'] = np.append([math.nan] * start_time, value['Data'])

        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()

        channel_series = [pd.Series(cdata[channel]["Data"]) for channel in selected_channels]
        return pd.concat(channel_series, axis=1, keys=selected_channels)

    def interpret_results(self, tolerances, filename="results.txt"):
        with open(filename, "w") as result_file:
            if self.results:
                for channel, tolerance in tolerances.items():
                    results = [v for v in self.results[channel] if is_float(v)]
                    if any([v > tolerance for v in results]):
                        result_file.write(f"BAD: {channel} channel in InetChart.json from both experiments has large "
                                          f"gap({max(results)}), please see timeseries.png.\n")
                    else:
                        result_file.write(f"GOOD: {channel} channel in InetChart.json from both experiments has small"
                                          f" gap({max(results)}), please see timeseries.png.\n")
            else:
                result_file.write(
                    "# of Experiments > 2, we don't compare the difference, please see timeseries.png.\n ")


class NodeDemographicsAnalyzer(CompareAnalyzer):
    def __init__(self, columns=('NumIndividuals', 'NumInfected'),
                 indexes=('Time', 'NodeID', 'Gender', 'AgeYears'), save_output=True):

        super().__init__(filenames=[os.path.join('output', 'ReportNodeDemographics.csv')],
                         output_file='node_demographics.csv', diff_filename='node_demographics_diff.csv',
                         png_filename='node_demographics.png', save_output=save_output)
        self.columns = set(columns)
        self.indexes = list(indexes)

    def interpret_results(self, tolerances, filename="node_demographics_result.txt"):
        with open(filename, "w") as nd_result_file:
            for node_column, tolerance in tolerances.items():
                node_df = self.results[node_column]
                if node_df is not None and not node_df.empty:
                    for column in node_df.columns:
                        if column != 'Time':
                            results = [v for v in node_df[column] if is_float(v)]
                            if any([v > tolerance for v in results]):
                                nd_result_file.write(f"BAD: {node_column}_{column} in ReportNodeDemographics.csv from"
                                                     f" both experiments has large gap(max={max(results)}), "
                                                     f"please see node_demographics.png.\n")
                            else:
                                nd_result_file.write(f"GOOD: {node_column}_{column} in ReportNodeDemographics.csv from"
                                                     f" both experiments has small gap(max={max(results)}), "
                                                     f"please see node_demographics.png.\n")
                else:
                    nd_result_file.write("# of Experiments > 2, we don't compare the difference, "
                                         "please see node_demographics.png.\n")

    def compare_and_plot(self, data, columns, flat_axes):
        compare_result = {}
        for (column, ax) in zip(columns, flat_axes):
            ax.set_title(column)
            grouped = data[column].groupby(level=['group'], axis=1).mean()
            grouped = grouped.unstack().unstack().unstack()
            grouped.plot(ax=ax, legend=False)
            multi_index = grouped.columns
            group_names = multi_index.levels[multi_index.names.index('group')]
            res = None
            if len(group_names) == 2:  # not the best way to do, but work for now.
                res = pd.DataFrame()
                for age in multi_index.levels[multi_index.names.index('AgeYears')]:
                    for gender in multi_index.levels[multi_index.names.index('Gender')]:
                        for node in multi_index.levels[multi_index.names.index('NodeID')]:
                            m0 = grouped.xs((group_names[0], age, gender, node),
                                            level=('group', 'AgeYears', 'Gender', 'NodeID'), axis=1)
                            m1 = grouped.xs((group_names[1], age, gender, node),
                                            level=('group', 'AgeYears', 'Gender', 'NodeID'), axis=1)
                            res[f'{age}_{gender}_{node}_diff'] = m1[m1.columns[0]] - m0[m0.columns[0]]
                            res[f'{age}_{gender}_{node}_diff'] = res[f'{age}_{gender}_{node}_diff'].abs()

            if res is not None:
                compare_result[column] = res

        return compare_result

    def write_comparisons_to_disk(self):
        for key, df in self.results.items():
            df.to_csv(os.path.join(self.working_dir, str(key) + '_' + self.diff_filename))

    def map(self, data, simulation):
        column_names = data[self.filenames[0]].columns

        selected_columns = self.columns.intersection(column_names) if self.columns else column_names

        data[self.filenames[0]].set_index(self.indexes, inplace=True)
        column_series = [pd.Series(data[self.filenames[0]][column]) for column in selected_columns]
        return pd.concat(column_series, axis=1, keys=selected_columns)
