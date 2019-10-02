import os
import pandas as pd

from idmtools.analysis.AnalyzeManager import AnalyzeManager
from idmtools.entities import IAnalyzer
from idmtools.core.PlatformFactory import PlatformFactory
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools_test.utils.group import default_select_fn, default_group_fn
from COMPS.Data import Experiment, QueryCriteria


class PopulationAnalyzer(IAnalyzer):

    data_group_names = ['group', 'sim_id', 'channel']
    ordered_levels = ['channel', 'group', 'sim_id']
    output_file = 'population.csv'

    def __init__(self, filename=os.path.join('output', 'InsetChart.json'), channels=(['Statistical Population']), save_output=True, working_dir="."):
        super(PopulationAnalyzer, self).__init__(filenames=[filename], working_dir=working_dir)
        self.channels = set(channels)
        self.save_output = save_output

    def get_channel_data(self, data_by_channel, selected_channels, header):
        channel_series = [default_select_fn(data_by_channel[channel]["Data"]) for channel in selected_channels]
        return pd.concat(channel_series, axis=1, keys=selected_channels)

    def map(self, data, simulation):
        cdata = data[self.filenames[0]]['Channels']
        selected_channels = self.channels.intersection(cdata.keys()) if self.channels else cdata.keys()
        return self.get_channel_data(cdata, selected_channels, data[self.filenames[0]]["Header"])

    def reduce(self, all_data):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        selected = []
        for sim, data in all_data.items():
            # TODO: #238 Simulations AttributeError: 'UUID' object has no attribute 'id'
            # Enrich the data with info
            data.group = default_group_fn(sim, sim.tags)
            data.sim_id = sim
            selected.append(data)

        # selected = []
        # exp_id = 'eba5b47b-f7d3-e911-a2bb-f0921c167866'  # comps2 staging
        # #platform = PlatformFactory.create(key='COMPS')
        # for s in Experiment.get(exp_id).get_simulations(query_criteria=QueryCriteria().select(["id", "state"]).select_children(["tags"])):
        #     sim = experiment.simulation()
        #     sim.uid = s.id
        #     sim.tags = s.tags
        #     s.group = default_group_fn(s.id, s.tags)
        #     selected.append(sim)

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
            data.to_csv(self.output_file)

        fig = plt.figure()
        for pop in list(all_data.values()):
            plt.plot(pop)
        plt.legend([s.id for s in all_data.keys()])
        plt.savefig(os.path.join(os.getcwd(), 'Population.png'))
        plt.close(fig)


if __name__ == "__main__":

    from idmtools.core.PlatformFactory import PlatformFactory

    platform = PlatformFactory.create(key='COMPS')

    exp_id = 'eba5b47b-f7d3-e911-a2bb-f0921c167866' #comps2 staging

    analyzers = [PopulationAnalyzer()]

    experiment = platform.get_item(id=exp_id)

    manager = AnalyzeManager(configuration={}, platform=platform, ids=[exp_id], analyzers=analyzers)
    manager.analyze()
