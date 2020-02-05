"""
This script is executed as entrypoint in the docker SSMT worker.
Its role is to collect the experiment ids and analyzers (w/o paramenters) and run the SSMT WorkItemManager in comps.
Change exp_id and simtools.ini file server_endpoint and environment variables for your needs
"""
from idmtools.core.platform_factory import Platform
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools.ssmt.ssmt_work_item import SSMTWorkItem
from idmtools.assets.FileList import FileList
import os
from COMPS.Data import WorkItem

wi_name = "SSMT WorkItemManager Test w Multi Exp"
command = "python run_ssmt_analysis.py"
user_files = FileList(root='.',
                      files_in_root=['PopulationAnalyzer.py', 'run_ssmt_analysis.py'])

exp_list = ["a585c439-b37d-e911-a2bb-f0921c167866",
          "7afc5160-e086-e911-a2bb-f0921c167866"]  # comps2 staging exp ids

if __name__ == "__main__":

    platform = Platform('COMPS2')
    wi = SSMTWorkItem(item_name=wi_name, command=command, user_files=user_files,
                      related_experiments=exp_list)
    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)
    wi = WorkItem.get(wi.uid)

    barr_out = wi.retrieve_output_files(paths=['results.json'])
    with open("results.json", 'wb') as file:
        file.write(barr_out[0])
