import os
import matplotlib
from sys import platform
#if os.environ.get('DISPLAY','') == '':
if platform == "linux" or platform == "linux2":
    print('Linux OS. Using non-interactive Agg backend')
    #print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class NodeDemographicsAnalyzer(IAnalyzer):
    data_group_names = ['group', 'tags', 'sim_id', 'column']
    ordered_levels = ['column', 'group', 'tags', 'sim_id']
    png_file = 'node_demographics.png'
    output_file = 'node_demographics.csv'
    diff_filename = 'node_demographics_diff.csv'

    def __init__(self, filenames=[os.path.join('output', 'ReportNodeDemographics.csv')], columns=('NumIndividuals',
                                                                                                  'NumInfected'),
                 indexes = ('Time','NodeID', 'Gender', 'AgeYears'), save_output=True, working_dir="."):

        super(NodeDemographicsAnalyzer, self).__init__(filenames=filenames, working_dir=working_dir)
        self.columns = set(columns)
        self.save_output = save_output
        self.indexes = list(indexes)

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
        m = m.unstack().unstack().unstack()
        m.plot(ax=ax, legend=False)
        multi_index = m.columns
        group_names = multi_index.levels[multi_index.names.index('group')]
        if len(group_names) == 2: # not the best way to do, but work for now.
            res = pd.DataFrame()
            for age in multi_index.levels[multi_index.names.index('AgeYears')]:
                for gender in multi_index.levels[multi_index.names.index('Gender')]:
                    for node in multi_index.levels[multi_index.names.index('NodeID')]:
                        m0= m.xs((group_names[0], age, gender, node),
                                  level=('group', 'AgeYears', 'Gender', 'NodeID'), axis=1)
                        m1 = m.xs((group_names[1], age, gender, node),
                                   level=('group', 'AgeYears', 'Gender', 'NodeID'), axis=1)
                        res[f'{age}_{gender}_{node}_diff'] = m1[m1.columns[0]] - m0[m0.columns[0]]
                        res[f'{age}_{gender}_{node}_diff'] = res[f'{age}_{gender}_{node}_diff'].abs()
            return res

    def default_filter_fn(self, md):
        return True

    def filter(self, simulation):
        return self.default_filter_fn(simulation.tags)

    def get_column_data(self, data_by_column, selected_columns):
        column_series = [self.default_select_fn(data_by_column[column]) for column in selected_columns]
        return pd.concat(column_series, axis=1, keys=selected_columns)

    def map(self, data, simulation):
        column_names = data[self.filenames[0]].columns

        selected_columns = self.columns.intersection(column_names) if self.columns else column_names

        data[self.filenames[0]].set_index(self.indexes, inplace=True)
        return self.get_column_data(data[self.filenames[0]], selected_columns)

    def compare_and_plot_by_column(self, columns, compare_and_plot_fn):
        ncol = int(1 + len(columns) / 4)
        nrow = int(np.ceil(float(len(columns)) / ncol))

        fig, axs = plt.subplots(figsize=(max(6, min(8, 4 * ncol)), min(6, 3 * nrow)), nrows=nrow, ncols=ncol,
                                sharex=True)

        flat_axes = [axs] if ncol * nrow == 1 else axs.flat

        compare_result = {}
        for (column, ax) in zip(columns, flat_axes):
            ax.set_title(column)
            m = compare_and_plot_fn(column, ax)
            if m is not None:
                compare_result[column] = m
        return compare_result


    def reduce(self, all_data):
        selected = []
        for sim, data in all_data.items():
            # Enrich the data with info
            exp = sim.experiment
            data.group = self.default_group_fn(exp.name, sim.tags)
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

        def compare_and_plot_fn(column, ax):
            return self.default_compare_and_plot_fn(data[column].dropna(), ax)

        columns = data.columns.levels[0]
        compare_result = self.compare_and_plot_by_column(columns, compare_and_plot_fn)

        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5,
                   fontsize='xx-small')

        # analyzer_path = os.path.dirname(__file__)
        current_path = os.getcwd()

        # plt.show()
        plt.savefig(os.path.join(current_path, self.png_file))

        # save results to csv files
        if compare_result:
            for key, df in compare_result.items():
                df.to_csv(os.path.join(current_path, str(key) + '_' + self.diff_filename))

        if self.save_output:
            data.to_csv(os.path.join(current_path, self.output_file))


if __name__ == "__main__":
    platform = Platform('COMPS')

    exp_id = 'cb19e482-fcfc-e911-a2be-f0921c167861'  # comps-dev exp_id

    filenames = ['output/ReportNodeDemographics.csv']
    analyzers = [NodeDemographicsAnalyzer(filenames=filenames)]

    manager = AnalyzeManager(platform=platform, ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
    manager.analyze()
