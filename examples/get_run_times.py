import json
import time

import pandas as pd
from COMPS import Client
from COMPS.Data import Simulation, Experiment, Configuration, QueryCriteria
from tqdm import tqdm

compshost = 'https://comps.idmod.org'

Client.login(compshost)
TEST_OWNERS =  ['ccollins', 'shchen', 'cwiswell', 'mafisher', 'yechen', 'zdu', 'jbloedow', 'stitova']
ITEMS_PER_BATCH = 1000

sim_info = []


TOTAL_SIMS = 300 * 1000


for i in tqdm(range(int(TOTAL_SIMS / ITEMS_PER_BATCH))):
    qc = QueryCriteria().select_children('hpc_jobs')\
        .where_tag('exe_collection_id')\
    .where()
        .count(ITEMS_PER_BATCH).offset(i * ITEMS_PER_BATCH)

    while True:
        try:
            sims = Simulation.get(query_criteria=qc)
            break
        except Exception as e:
            print(e)
            time.sleep(2)
    sim_info.extend([dict(id=s.id, owner=s.owner, tags=s.tags, run_time=(s.hpc_jobs[0].end_time - s.hpc_jobs[0].start_time).total_seconds(), year=s.hpc_jobs[0].submit_time.year) for s in sims if s.owner not in TEST_OWNERS and s.hpc_jobs[0].start_time and s.hpc_jobs[0].end_time])
df = pd.DataFrame.from_records(sim_info)
df.to_csv('dtktools_sims.csv')


sim_info = []
for i in tqdm(range(int(TOTAL_SIMS / ITEMS_PER_BATCH))):
    qc = QueryCriteria().select_children('hpc_jobs').where_tag('task_type=emodpy.emod_task.EMODTask').count(ITEMS_PER_BATCH).offset(i * ITEMS_PER_BATCH)
    sims = Simulation.get(query_criteria=qc)
    while True:
        try:
            sims = Simulation.get(query_criteria=qc)
            break
        except Exception as e:
            print(e)
            time.sleep(2)
    sim_info.extend([dict(id=s.id, owner=s.owner, tags=s.tags, run_time=(s.hpc_jobs[0].end_time - s.hpc_jobs[0].start_time).total_seconds(), year=s.hpc_jobs[0].year) for s in sims if s.owner not in TEST_OWNERS and s.hpc_jobs[0].submit_time.start_time and s.hpc_jobs[0].end_time])
df = pd.DataFrame.from_records(sim_info)
df.to_csv('idmtools_sims.csv')



