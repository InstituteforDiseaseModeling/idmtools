#********************************************************************************
#
# Python 3.6.0
#
#********************************************************************************

import os, sys, shutil, time

from sims_builds.bldFile            import dtkBuilder

from file_builders.cnfgBuilder      import cnfgBuilder
from file_builders.demoBuilder      import demoBuilder
from file_builders.campBuilder      import campBuilder
from file_builders.dllcBuilder      import dllcBuilder
from file_builders.writeFlat        import writeDict

from genParams                      import dataDic        as gParam
from simParams                      import dataDic        as pDic

import global_data

#*******************************************************************************

# Try all DTK python imports ASAP to check syntax

from dtk_in_process                 import application    as notused01
from dtk_post_process               import application    as notused02

#*******************************************************************************

def application(cFileName=''):

  # Read index of simulation parameter set
  with open('idxStrFile','r') as fid01:
    simIdx = int(fid01.readline())


  # Select parameter set, apply update function, save revisison sets
  for keyval in pDic:
    pDic[keyval] = pDic[keyval][simIdx]
  dtkDic   = dtkBuilder(pDic=pDic)

  global_data.CNFG_ALTS = dtkDic['cnfgAlts']
  global_data.DEMO_ALTS = dtkDic['demoAlts']


  # Update simulation control variables
  genAlts  = dtkDic['genAlts']
  for keyval in genAlts:
    gParam[keyval] = genAlts[keyval]
  #end-if


  # Simulation configuration file
  cnfgStr = cnfgBuilder()
  with open('config.json','w') as fid01:
    fid01.write(cnfgStr)


  # Demographics file and node code dictionary
  demoDat = demoBuilder()
  with open('demo.json','w')     as fid01:
    fid01.write(demoDat[0])
  with open('id_table.json','w') as fid01:
    fid01.write(demoDat[1])


  # Campaign interventions file
  campStr = campBuilder()
  with open('camp.json','w') as fid01:
    fid01.write(campStr)


  # Custom reports configuration file  
  dllcStr = dllcBuilder()
  with open('dllc.json','w') as fid01:
    fid01.write(dllcStr)


  # Any other one-time-per-experiment operations
  if(not simIdx):
    pass


  # Wait for file creation to complete
  time.sleep(10)


  return cFileName

# end-application

#*******************************************************************************
