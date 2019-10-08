import os
import pandas as pd

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class PopulationAnalyzer(IAnalyzer):
    data_group_names = ['group', 'sim_id', 'channel']
    ordered_levels = ['channel', 'group', 'sim_id']

    def __init__(self, filenames=None, channels=(['Statistical Population']), save_output=True):
        super().__init__()
        self.filenames = filenames or []
        self.channels = set(channels)
        self.save_output = save_output

    def default_select_fn(self, ts):
        return pd.Series(ts)

    def default_group_fn(self, k, v):
        return k

    def get_channel_data(self, data_by_channel, selected_channels):
        channel_series = [self.default_select_fn(data_by_channel[channel]["Data"]) for channel in selected_channels]
        return pd.concat(channel_series, axis=1, keys=selected_channels)

    def map(self, data, simulation):
        # Apply is called for every simulations included into the experiment
        # We are simply storing the population data in the pop_data dictionary
        # return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]
        cdata = data[self.filenames[0]]['Channels']
        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()
        return self.get_channel_data(cdata, selected_channels)

    def reduce(self, all_data):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        analyzer_path = os.path.dirname(__file__)
        selected = []
        for sim, data in all_data.items():
            # Enrich the data with info
            data.group = self.default_group_fn(str(sim.uid), sim.tags)
            data.sim_id = str(sim.uid)
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

        if self.save_output:
            data.to_csv(os.path.join(analyzer_path, 'population.csv'))
            # data.to_csv('population.csv')

        fig = plt.figure()
        for pop in list(all_data.values()):
            plt.plot(pop)
        plt.legend([s.uid for s in all_data.keys()])
        # plt.show()
        plt.savefig(os.path.join(analyzer_path, 'population.png'))
        plt.close(fig)


if __name__ == "__main__":
    platform = Platform('COMPS2')

    filenames = ['output/InsetChart.json']
    analyzers = [PopulationAnalyzer(filenames=filenames)]

    exp_id = '65a93d51-04db-e911-a2be-f0921c167861'  # comps2 exp_id
    manager = AnalyzeManager(platform=platform, ids=[exp_id], analyzers=analyzers)
    manager.analyze()
