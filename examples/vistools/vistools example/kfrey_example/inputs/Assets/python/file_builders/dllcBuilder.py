#********************************************************************************
#
# Builds a config file for custom reporter dlls for input to the DTK.
#
# Python 3.6.0
#
#********************************************************************************

from io                                     import StringIO   as fstream

from file_builders.writeFlat                import writeDict

from genParams                              import dataDic   as gParam
from simParams                              import dataDic   as pDic

import global_data

#********************************************************************************

def dllcBuilder():

  # Simulation parameters
  simIdx    = pDic['simIdx']
  repNames  = gParam['repNames']
  repStart  = gParam['repStart']
  sampDic   = gParam['sampling']

  # Create string buffer
  pDat = fstream()
  
  # Dictionary of parameters to be written
  json_set = {}


  
  # ***** Custom reporters *****
  json_set['Custom_Reports'] = \
    {
     'Use_Explicit_Dlls': 1,
     'genericReporter':
       {
        'Enabled':  1,
        'Reports': []
       }
    }


  # General reporting
  for repType in repNames:
    repDic = {'fName':   repType+'{:05d}'.format(simIdx) ,
              'rType':                           repType ,
              'rStart':        365.0*(repStart-1900)+0.5 }

    json_set['Custom_Reports']['genericReporter']['Reports'].append(repDic)
  #end-repType
  

  # Individual data sets
  for sampSet in sampDic:
    repType = sampDic[sampSet]['stype']
    filName = '{:s}{:05d}'.format(sampSet,simIdx)
    
    nodeIDs = list()
    for placeVal in sampDic[sampSet]['place']:
      nodeIDs.extend(global_data.NODE_CODE[placeVal])

    repDic = {'fName': filName, 'rType': repType, 'rNodes': nodeIDs}

    if(repType == 'SEROSURVEY'):
      repDic['aBins']      = sampDic[sampSet]['ages']
      repDic['rStart']     = 365.0*(sampDic[sampSet]['time']      -1900)+0.5
      repDic['rStepTime']  = sampDic[sampSet]['t_step']
    elif(repType == 'AGE_HIST'):
      repDic['aBins']      = sampDic[sampSet]['ages']
      repDic['rStart']     = 365.0*(sampDic[sampSet]['years'][0]  -1900)+0.5
      repDic['rEnd']       = 365.0*(sampDic[sampSet]['years'][1]+1-1900)+0.5
      repDic['rStepTime']  = sampDic[sampSet]['t_step']
    elif(repType == 'INFECT_BIN'):
      repDic['tBins']      = sampDic[sampSet]['bins']        
      repDic['rStart']     = 365.0*(sampDic[sampSet]['years'][0]  -1900)+0.5
      repDic['rEnd']       = 365.0*(sampDic[sampSet]['years'][1]+1-1900)+0.5
      repDic['rSpatial']   = 1 if sampDic[sampSet]['burst'] else 0
    elif(repType == 'SUSCEPT_BIN'):
      repDic['tBins']      = sampDic[sampSet]['bins']        
      repDic['rStart']     = 365.0*(sampDic[sampSet]['years'][0]  -1900)+0.5
      repDic['rEnd']       = 365.0*(sampDic[sampSet]['years'][1]+1-1900)+0.5
      repDic['rSpatial']   = 1 if sampDic[sampSet]['burst'] else 0
    else:
      raise ValueError('Unknown type of sampling requested: {:s}'.format(repType))
    #end-repType

    json_set['Custom_Reports']['genericReporter']['Reports'].append(repDic)
  #end-sampSet

  # End file construction
  writeDict(pDat, json_set)
  pDatStr = pDat.getvalue()
    
  return pDatStr

# end-dllcBuilder

#********************************************************************************
