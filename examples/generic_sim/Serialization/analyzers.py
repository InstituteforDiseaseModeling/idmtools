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
    def __init__(self, filenames, output_file, diff_filename, png_filename, save_output=True):
        super().__init__(filenames=filenames)
        self.output_file = output_file
        self.diff_filename = diff_filename
        self.png_filename = png_filename
        self.save_output = save_output

    @abstractmethod
    def write_comparisons_to_disk(self, compare_result):
        pass

    @abstractmethod
    def compare_groups(self, data, channels, groups):
        pass

    @abstractmethod
    def interpret_results(self, tolerances, filename="results.txt"):
        pass

    def reduce(self, all_data: dict):
        combined = pd.DataFrame()

        for sim, data in all_data.items():
            data['group'] = sim.experiment.name
            combined = combined.append(data)

        if len(combined) == 0:
            print("\n No data have been returned... Exiting...")
            return

        # Create a dataframe that groups by group and time and mean over all repetitions
        combined.set_index(['group'], append=True, inplace=True)
        combined.sort_index(inplace=True)
        combined = combined.groupby(combined.index.names).mean()

        # Make sure all values of the index exists
        combined = combined.unstack().stack(dropna=False)

        # Get the available channels from the data
        channels = combined.columns.tolist()
        groups = combined.index.get_level_values('group').unique().to_list()

        # Create the sub plots
        ncol = int(1 + len(channels) / 4)
        nrow = int(np.ceil(float(len(channels)) / ncol))
        figsize = (max(6, min(8, 4 * ncol)), min(6, 3 * nrow))
        fig, axs = plt.subplots(figsize=figsize, nrows=nrow, ncols=ncol, sharex=True)
        flat_axes = [axs] if ncol * nrow == 1 else axs.flat

        # Plot
        for channel, ax in zip(channels, flat_axes):
            channel_data = combined[channel]
            for group in groups:
                ax.set_title(channel)
                ax.plot(channel_data.groupby(["Time", "group"]).mean().loc[(slice(None), group)])

        # Create the legend
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5,
                   fontsize='xx-small', labels=groups)

        # Save the figure
        plt.savefig(os.path.join(self.working_dir, self.png_filename))

        compare_result = self.compare_groups(combined, channels, groups)

        # save results to csv files
        if compare_result:
            self.write_comparisons_to_disk(compare_result)

        if self.save_output:
            combined.to_csv(os.path.join(self.working_dir, self.output_file))

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

    def write_comparisons_to_disk(self, compare_result):
        df = pd.DataFrame.from_dict(compare_result)
        df.to_csv(os.path.join(self.working_dir, self.diff_filename))

    def compare_groups(self, data, channels, groups):
        if len(groups) != 2:
            return {}

        compare_result = {}
        differences = data.xs(groups[1], level='group') - data.xs(groups[0], level='group')
        # Plot the available groups per channel
        for channel in channels:
            compare_result[channel] = differences[channel]

        return compare_result

    def map(self, data, simulation):
        # Retrieve the start time
        start_time = data[self.filenames[0]]['Header']["Start_Time"]

        # Get the channels data for the selected channels
        cdata = data[self.filenames[0]]['Channels']
        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()
        channel_series = {channel: cdata[channel]["Data"] for channel in selected_channels}

        # If start_time is not 0 pad the data with nan
        if start_time > 0:
            for series in channel_series.values():
                series[0:0] = [np.nan] * start_time

        # Return the series
        df = pd.DataFrame(channel_series)
        df["Time"] = df.index
        df.set_index("Time", inplace=True)
        return df

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
                node_data = self.results[node_column]
                if len(node_data) == 0:
                    continue

                for column, column_data in node_data.items():
                    column_data = [float(v) for v in column_data if is_float(v)]
                    if any([v > tolerance for v in column_data]):
                        nd_result_file.write(f"BAD: {node_column}_{column} in ReportNodeDemographics.csv from"
                                             f" both experiments has large gap(max={max(column_data)}), "
                                             f"please see node_demographics.png.\n")
                    else:
                        nd_result_file.write(f"GOOD: {node_column}_{column} in ReportNodeDemographics.csv from"
                                             f" both experiments has small gap(max={max(column_data)}), "
                                             f"please see node_demographics.png.\n")

    def compare_groups(self, data, channels, groups):
        if len(groups) != 2:
            return {}

        compare_result = {}
        differences = data.xs(groups[1], level='group') - data.xs(groups[0], level='group')
        differences = differences.abs()

        for channel in channels:
            channel_data = differences[channel]
            res = {}

            for age in data.index.get_level_values("AgeYears").unique():
                for gender in data.index.get_level_values("Gender").unique():
                    for node in data.index.get_level_values("NodeID").unique():
                        res[f'{age}_{gender}_{node}_diff'] = channel_data.loc[
                            (slice(None), node, gender, age)].to_list()

            if res is not None:
                compare_result[channel] = res

        return compare_result

    def write_comparisons_to_disk(self, compare_result):
        for key, df in compare_result.items():
            df = pd.DataFrame(df)
            df.to_csv(os.path.join(self.working_dir, str(key) + '_' + self.diff_filename))

    def map(self, data, simulation):
        csv_data = data[self.filenames[0]]
        # Get the columns
        column_names = csv_data.columns.to_list()
        selected_columns = list(self.columns.intersection(column_names) if self.columns else column_names)

        # Return them
        csv_data.set_index(self.indexes, inplace=True)
        csv_data.sort_index(inplace=True)

        return csv_data[selected_columns]
