#********************************************************************************
#
# Python 3.6.0
#
#********************************************************************************

from io                        import StringIO as fstream

from file_builders.writeFlat   import writeDict

#********************************************************************************

import  numpy  as np
import  pandas as pd

from    genParams   import dataDic   as gParam
from    simParams   import dataDic   as pDic

import  global_data

if('riskmap' in gParam['blobName']):
  from ml_utils import ConstructFeatureDf, RandomForestProjection
  from nk_utils import simTime_to_datetime
 
#********************************************************************************

def application(simTime=0.0, nodeDat=[]):

  # Simulation parameters
  inVer      = gParam['pyinproc_ver']
  siaDelay   = gParam['sia_delay']
  u5trig     = gParam['u5frac_trigger']
  bThresh    = gParam['burden_threshold']
  timeDF     = 365*(gParam['start_dataframe'] - 1900)
  timeRM     = 365*(gParam['start_riskmap'] - 1900)

  goTime     = simTime + siaDelay
  if(goTime % 365.0 == 1.0):
    goTime = goTime + 1.0

  
  # Global data
  gDEM      = global_data.DEMOGRAPHICS['Nodes']
  gSIA      = global_data.SIA_LIST
  gTIME     = global_data.SIA_RECORD
  gRISKMAP  = global_data.riskmap
  gREPORT   = global_data.REP_COUNTER
  

  # Return value
  nodesSIA = list()
  

  # Standard reports
  t_str = '{:8.2f}'.format(simTime)
  gREPORT[t_str] = dict()
  gREPORT[t_str]['nodes'] = [nVal[ 0] for nVal in nodeDat]
  gREPORT[t_str]['infct'] = [nVal[ 1] for nVal in nodeDat]
  gREPORT[t_str]['t_pop'] = [nVal[ 4] for nVal in nodeDat]
  gREPORT[t_str]['brths'] = [nVal[ 5] for nVal in nodeDat]
  gREPORT[t_str]['t_sia'] = [nVal[ 8] for nVal in nodeDat]
  gREPORT[t_str]['g_rid'] = [nVal[10] for nVal in nodeDat]
  gREPORT[t_str]['g_sia'] = [nVal[ 9] for nVal in nodeDat]



  # Incidence based
  if(inVer == 'REACTIVE'):
    # Copy previous list of nodes within radius of observed incidence
    gSIAold = gSIA.copy()
    gSIA.clear()


    # Construct current list of nodes within radius of observed incidence
    obsNodes = [nVal[0] for nVal in nodeDat if nVal[2] > 0]

    for nodeNum in obsNodes:
      for nodeDic in gDEM:
        if(nodeNum == nodeDic['NodeID']):
          gSIA.extend(nodeDic['NodeAttributes']['OutbreakNodes'])

    gSIA = list(set(gSIA))


    # Assign SIA if node in current and previous list, and no recent SIA
    nodesSIA = [(nVal,goTime) for nVal in gSIAold if
                (nVal in gSIA) and (gTIME[nVal] + 90.0 < simTime)]
    for nVal in nodesSIA:
      gTIME[nVal[0]] = nVal[1]



  # Sero based
  if(inVer == 'PROACTIVE'):
    # All nodes with insufficient sero status
    nodesSIA = [(nVal[0],goTime) for nVal in nodeDat if nVal[3] > u5trig]



  # ML based
  if(inVer == 'RISKMAP'):
    # Bypass early sims
    if(simTime < timeDF):
      return nodesSIA
    if(simTime > timeRM):
      gRISKMAP = True
    
    # Load new data frame with simulation data
    newNodeDat = [(nVal[0],nVal[1],nVal[4],nVal[5],nVal[6],nVal[7],) for nVal in nodeDat]
    updated_df = pd.DataFrame(newNodeDat, columns=['node_id','cases','population','births','mcv1','sia'])
    pd_time    = simTime_to_datetime(simTime)
    updated_df['time'] = len(newNodeDat)*[pd_time]
    updated_df = updated_df.set_index(['node_id','time'])

    # Update the global dataframe
    global_data.df = (global_data.df).append(updated_df).sort_index()
    #(global_data.df).to_csv('GD_DATAFRAME')

    # Run the riskmap
    if(gRISKMAP):
      # Perform feature construction
      local_df = ConstructFeatureDf(global_data.df)

      # Fit a random forest and compute the projection
      (r2_score, projection) = RandomForestProjection(local_df, pd_time)

      # Sort, restructure, and return
      projection = projection.sort_values()
      res_list = list(zip(projection.index,projection))
      nodesSIA = [(nVal[0], goTime) for nVal in res_list if
                  (nVal[1] > bThresh)]

  # End function
  return nodesSIA

#end-application

#********************************************************************************
