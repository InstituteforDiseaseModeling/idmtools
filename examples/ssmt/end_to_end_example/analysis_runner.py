import json
import os

import pandas as pd

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.analysis.platform_anaylsis import PlatformAnalysis
from idmtools.core import ItemType
from idmtools.entities.ianalyzer import BaseAnalyzer
from idmtools.core.platform_factory import Platform

class MyAnalyzer(BaseAnalyzer):

    def __init__(self, output_path="output", filenames=["output/output.json"]):
        super().__init__(filenames=filenames)
        self.output_path = output_path

    def filter(self, simulation) -> bool:
        return int(simulation.tags.get("a")) >= 1

    # idmtools analyzer
    def map(self, data, simulation):
        return data[self.filenames[0]]

    def reduce(self, all_data: dict):
        first_sim = list(all_data.keys())[0]  # get first Simulation
        exp_id = first_sim.experiment.id  # Set the exp id from the first sim data

        # Build a dictionary with 'sim_id' and corresponding value 'a'
        rows = []
        for s, v in all_data.items():
            rows.append({'sim_id': str(s.uid), 'output': v})

        # Convert to DataFrame
        df = pd.DataFrame(rows)

        # Set 'sim_id' as index
        df.set_index('sim_id', inplace=True)

        # Save to CSV
        output_folder = os.path.join(self.output_path, exp_id)
        os.makedirs(output_folder, exist_ok=True)
        # Save to csv file under output/exp_id/total_output.csv
        df.to_csv(os.path.join(output_folder,'total_output.csv'))

def ssmt_analysis(experiment_id, platform):
    filenames = ['output/output.json']
    # Specify the id Type, in this case an Experiment
    analysis = PlatformAnalysis(platform=platform, experiment_ids=[experiment_id],
                                analyzers=[MyAnalyzer],
                                analyzers_args=[{'filenames': filenames}],
                                analysis_name='test platformanalysis with experiment',
                                tags={'idmtools': 'test_ssmt'},
                                extra_args={"max_workers": 8})

    analysis.analyze(check_status=True)
    wi = analysis.get_work_item()
    # Download analyzer result to local
    local_output_path = "output_ssmt"  # specify local output path
    out_filenames = [f"output/{experiment_id}/total_output.csv"]  # specify output filenames to download
    # Download files from SSMT workitem aggregated result to local directory.
    # The actual local_output_path is output_ssmt/workitem_id/output/experiment_id/total_output.csv
    platform.get_files_by_id(wi.id, ItemType.WORKFLOW_ITEM, out_filenames, local_output_path)

def local_analysis(experiment_id, platform):
    filenames = ['output/output.json']
    # Initialize the analyser class with the path of the output files to download
    analyzers = [MyAnalyzer(filenames=filenames, output_path='output')]
    # Specify the id Type, in this case an Experiment
    manager = AnalyzeManager(platform, ids=[(experiment_id, ItemType.EXPERIMENT)],
                             analyzers=analyzers, max_workers=1)
    manager.analyze()

if __name__ == '__main__':
    platform = Platform("Calculon")
    experiment_id = 'dc4d5d86-6460-f011-9311-f0921c167864'
    ssmt_analysis(experiment_id, platform)
   #local_analysis(experiment_id, platform)
