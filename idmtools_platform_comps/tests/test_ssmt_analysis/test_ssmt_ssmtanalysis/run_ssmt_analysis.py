# SSMTAnalysis Test

"""
This script is executed as entrypoint in the docker SSMT worker.
Its role is to collect the experiment ids and analyzers (w/o paramenters) and run the SSMTAnalysis in comps.
"""
import os
from idmtools.ssmt.ssmt_analysis import SSMTAnalysis
from test_ssmt_ssmtanalysis.MyAnalyzer import MyAnalyzer
from idmtools.assets.FileList import FileList

par_par_dir = os.path.normpath(os.path.join('..', os.pardir))

additional_files = FileList(root='.', files_in_root=['MyAnalyzer.py', 'run_ssmt_analysis.py'])


if __name__ == "__main__":
    exp_id = "08fc74a7-b767-e911-a2b8-f0921c167865"  # exp_id in staging

    tags = {'Demo': 'idmtools SSMTAnalysis', 'WorkItem type': 'Docker'}

    # args = dict(file_name="InsetChart.json", channels=['Adult Vectors'])
    args = [{'file_name': 'InsetChart.json', 'channels': 'Adult Vectors'}]

    analysis = SSMTAnalysis(experiment_ids=[exp_id],
                            analyzers=[MyAnalyzer],
                            analyzers_args=args,
                            analysis_name="idmtools: run SSMTAnalysis with parameters",
                            tags=tags,
                            additional_files=additional_files)

    analysis.analyze()
