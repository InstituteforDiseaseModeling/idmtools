#********************************************************************************
#
# Python 3.6.0
#
#********************************************************************************

import os, sys, shutil, json

import numpy as np

from genParams                      import dataDic        as gParam
from simParams                      import dataDic        as pDic

import global_data

#********************************************************************************

def application(oDirName=''):

  # Simulation parameters
  simIdx    = pDic['simIdx']
  repNames  = gParam['repNames']
  sampDic   = gParam['sampling']


  # Global data
  gREPORT   = global_data.REP_COUNTER


  # Prep output dictionary
  keyStr = '{:05d}'.format(simIdx)
  tmpDat = {keyStr:{}}


  # Output sampling
  for sampSet in sampDic:
    oFilName = '{:s}{:05d}'.format(sampSet,simIdx)
    oDatName = os.path.join(oDirName,oFilName)
    with open(oDatName,'r') as outFile:
      datSet = np.loadtxt(fname=outFile,dtype=float,delimiter=',')
    tmpDat[keyStr][sampSet] = datSet.tolist()


  # In-process reports
  tmpDat[keyStr]['INPROC_REP'] = gREPORT
  

  # Write output dictionary
  with open('tmpOutfile','w') as tmpFile:
    json.dump(tmpDat, tmpFile)


  # Transfer data bricks
  for repType in repNames:
    fName = repType+'{:05d}'.format(simIdx)


  # Transfer dataframe if present
  if(os.path.isfile('GD_DATAFRAME')):
    oFilName = 'DATAFRAME{:05d}'.format(simIdx)
    shutil.copyfile('GD_DATAFRAME',os.path.join(oDirName,oFilName))


  # Any other one-time-per-experiment operations
  if(not simIdx):
    pass

  
  return None

#end-application

#********************************************************************************
