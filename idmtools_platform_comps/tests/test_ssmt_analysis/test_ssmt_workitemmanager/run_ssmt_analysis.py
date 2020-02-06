"""
This script is executed as entrypoint in the docker SSMT worker.
Its role is to collect the experiment ids and analyzers (w/o paramenters) and run the SSMT WorkItemManager in comps.
Change exp_id and simtools.ini file server_endpoint and environment variables for your needs
"""
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.idm_work_item import SSMTWorkItem
from idmtools.assets.file_list import FileList
import os
from COMPS.Data import WorkItem

par_par_dir = os.path.normpath(os.path.join('..', os.pardir))

exp_id = "08fc74a7-b767-e911-a2b8-f0921c167865"  # exp id in comps2

wi_name = "SSMT WorkItemManager Test"
command = "python run_PopulationAnalyzer.py " + exp_id
user_files = FileList(root='.',
                      files_in_root=['PopulationAnalyzer.py', 'run_PopulationAnalyzer.py', 'run_ssmt_analysis.py'])


if __name__ == "__main__":
    platform = Platform('COMPS2')
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files,
                      related_experiments=[exp_id])
    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)
    wi = WorkItem.get(wi.uid)

    barr_out = wi.retrieve_output_files(paths=['InsetChart.json'])
    with open("InsetChart.json", 'wb') as file:
        file.write(barr_out[0])
