#********************************************************************************
#
# Builds a campaign file for input to the DTK.
#
# Python 3.6.0
#
#********************************************************************************

import numpy as np

from io                                         import StringIO   as fstream

from file_builders.inheritor                    import inheritor
from file_builders.writeFlat                    import writeDict

from file_builders.demograph_data.routine       import dat_factory  as  routine
from file_builders.demograph_data.supplement    import dat_factory  as  supplem

from genParams                                  import dataDic    as gParam
from simParams                                  import dataDic    as pDic

import global_data

#********************************************************************************

def campBuilder():

  # Create string buffer
  pDat = fstream()
  
  # Dictionary to be written
  json_set = {}

  
  # ***** Campaign file *****
  json_set['Campaign_Name'] = 'kfrey001'
  json_set['Events']        = []
  json_set['Use_Defaults']  = 0


  # ***** SIA events *****
  json_set['Events'].extend(IV_SIA())


  # ***** RI events *****
  json_set['Events'].extend(IV_RI())


  # End file construction
  writeDict(pDat, json_set)
  pDatStr = pDat.getvalue()
    
  return pDatStr

# end-campBuilder

#********************************************************************************

# SIA intervention construction
def IV_SIA():
  
  runYears      = gParam['runYears']
  disease       = gParam['disease']  
  bldName       = 'CATAN'
  nodeCodeDic   = global_data.NODE_CODE

  # Build SIA calendar
  supplement  = supplem(disease)
  exReg       = bldName + ':'
  siaSet1     = [val for val in supplement if exReg.startswith(val[0])]
  siaData     = [(val[1],val[2],val[3],val[4]) for val in siaSet1]
  siaSet2     = [val for val in supplement if val[0].startswith(exReg)]
  if(len(siaSet2) > 0):
    siaSubDat   = np.array([[val[1],val[2],val[3],val[4]] for val in siaSet2])
    siaSubCov   = np.array([val[4]*population[val[0]][0]/popVal[0] for val in siaSet2])
    siaGoDays   = np.unique(siaSubDat[:,2])
    for goDay in siaGoDays:
      lIdx = (goDay == siaSubDat[:,2])
      aMin = np.mean(siaSubDat[lIdx,0])
      aMax = np.mean(siaSubDat[lIdx,1])
      tCov = np.sum(siaSubCov[lIdx])
      siaData.append((aMin,aMax,goDay,tCov))
  
  # SIA Lists
  siaMinAgeList = [val[0] for val in siaData]
  siaMaxAgeList = [val[1] for val in siaData]  
  siaDateList   = [val[2] for val in siaData] 
  siaTargList   = [val[3] for val in siaData]

  SIA_list = []

  for k1 in range(len(siaDateList)):
    SIAdic = { 'class':                             'CampaignEvent' ,
               'Nodeset_Config':          { 'class': 'NodeSetAll' } ,
               'Start_Day':                         siaDateList[k1] ,
               'Event_Coordinator_Config':
               { 'class':
                         'StandardInterventionDistributionEventCoordinator' ,
                 'Demographic_Coverage':                    siaTargList[k1] ,
                 'Target_Residents_Only':                                 0 ,
                 'Number_Repetitions':                                    1 ,
                 'Property_Restrictions':                                [] ,
                 'Node_Property_Restrictions':                           [] ,
                 'Property_Restrictions_Within_Node':                    [] ,
                 'Timesteps_Between_Repetitions':                         0 ,
                 'Target_Demographic':                  'ExplicitAgeRanges' ,
                 'Target_Age_Min':                    siaMinAgeList[k1]/365 ,
                 'Target_Age_Max':                    siaMaxAgeList[k1]/365 ,
                 'Intervention_Config':
                 { 'class':                    'SimpleVaccine' ,
                   'Intervention_Name':             'kfrey001' ,
                   'Dont_Allow_Duplicates':                  0 ,
                   'Cost_To_Consumer':                       0 ,
                   'Efficacy_Is_Multiplicative':             1 ,
                   'Disqualifying_Properties':              [] ,
                   'New_Property_Value':                    '' ,
                   'Vaccine_Take':                           0 ,
                   'Vaccine_Type':       'AcquisitionBlocking' ,
                   'Waning_Config':
                   { 'class':              'WaningEffectConstant' ,
                     'Initial_Effect' :                       1.0 }
                 },
               }
             }

    SIA_list.append(SIAdic)

  return []
 
#end-IV_SIA

#*******************************************************************************

# SIA intervention construction
def IV_RI():

  runYears      = gParam['runYears']
  disease       = gParam['disease']
  nodeCodeDic   = global_data.NODE_CODE
  bldName       = 'CATAN'

  riData       = inheritor(place=bldName, dataDic=routine(disease))
  
  riFracList   = [val[0] for val in riData] 
  riMeanList   = [val[1] for val in riData]
  riStdvList   = [val[2] for val in riData]  
  riPrevList   = [val[3] for val in riData]

  RI_list = []

  for k1 in range(1):
    RIdic = { 'class':                                  'CampaignEvent' ,
              'Nodeset_Config':               { 'class': 'NodeSetAll' } ,
              'Start_Day':                   365.0*(runYears[0]-1900)+1 ,
              'Event_Coordinator_Config':
               { 'class':
                     'StandardInterventionDistributionEventCoordinator' ,
                 'Demographic_Coverage':                            1.0 ,
                 'Target_Residents_Only':                             0 ,
                 'Number_Repetitions':                                1 ,
                 'Property_Restrictions':                            [] ,
                 'Node_Property_Restrictions':                       [] ,
                 'Property_Restrictions_Within_Node':                [] ,
                 'Timesteps_Between_Repetitions':                     0 ,
                 'Target_Demographic':                       'Everyone' ,
                 'Intervention_Config':
                 { 'class':                          'BirthTriggeredIV' ,
                   'Intervention_Name':                      'kfrey001' ,
                   'Dont_Allow_Duplicates':                           0 ,
                   'Disqualifying_Properties':                       [] ,
                   'New_Property_Value':                             '' ,
                   'Demographic_Coverage':                          1.0 ,
                   'Target_Residents_Only':                           0 ,
                   'Target_Demographic':                     'Everyone' ,
                   'Duration':                                       -1 ,
                   'Property_Restrictions':                          [] ,
                   'Node_Property_Restrictions':                     [] ,
                   'Property_Restrictions_Within_Node':              [] ,
                   'Actual_IndividualIntervention_Config':
                   { 'class':                           'SimpleVaccine' ,
                     'Intervention_Name':                    'kfrey001' ,
                     'Dont_Allow_Duplicates':                         0 ,
                     'Cost_To_Consumer':                              0 ,
                     'Efficacy_Is_Multiplicative':                    1 ,
                     'Disqualifying_Properties':                     [] ,
                     'New_Property_Value':                           '' ,
                     'Vaccine_Take':                                  0 ,
                     'Vaccine_Type':              'AcquisitionBlocking' ,
                     'Waning_Config':
                     { 'class':                  'WaningEffectConstant' ,
                       'Initial_Effect' :                           1.0 }
                   }
                 }
               }
             }

    RI_list.append(RIdic)

  return []
 
#end-IV_RI

#*******************************************************************************
