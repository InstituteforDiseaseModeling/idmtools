#********************************************************************************
#
# Build a list of nodes for a demographics file
#
# Python 3.6.0
#
#********************************************************************************

import numpy as np

from genParams                   import dataDic as gParam

from file_builders.demoCalc      import demoCalc_AgeDist
from file_builders.demoCalc      import demoCalc_GrowTarg, demoCalc_SusTarg
from file_builders.inheritor     import inheritor

from file_builders.demograph_data.area          import dataDic  as  area
from file_builders.demograph_data.alias         import dataDic  as  alias
from file_builders.demograph_data.birthforce    import dataDic  as  birthforce
from file_builders.demograph_data.birthrate     import dataDic  as  birthrate
from file_builders.demograph_data.geography     import dataDic  as  geography
from file_builders.demograph_data.mortality     import dataDic  as  mortality
from file_builders.demograph_data.mortality     import bEdges   as  mortVecX
from file_builders.demograph_data.population    import dataDic  as  population

from file_builders.demograph_data.routine       import dat_factory  as  routine
from file_builders.demograph_data.supplement    import dat_factory  as  supplem

import global_data

#********************************************************************************

def singlenode(bldName='', nodeVal=1):

  # Glabal parameters
  demoAlts = global_data.DEMO_ALTS
  config   = global_data.CONFIG

  # Simulation parameters
  disease     = gParam['disease']
  exInf       = gParam['exInfect']
  exInfPow    = gParam['exInfectPow']
  repNMFR     = gParam['repNMFR']
  agentRat    = gParam['agentRat']
  runYears    = gParam['runYears']

  # Data lookup
  popVal      = population[bldName]
  areaVal     = area[bldName]

  bForceVec   = inheritor(place=bldName, dataDic=birthforce)
  bRatVal     = inheritor(place=bldName, dataDic=birthrate)
  geog        = inheritor(place=bldName, dataDic=geography)
  mortVecY    = inheritor(place=bldName, dataDic=mortality)
  
  riData      = inheritor(place=bldName, dataDic=routine(disease))

  R0          = config['Base_Infectivity']*config['Infectious_Period_Gaussian_Mean']
  tFracSus    = 1.0/R0 if R0 > 1.0 else 1.0
  simplSus    = False

  # Check for revisions
  for revEntry in demoAlts:
    if('Prebuild' not in revEntry or not revEntry['Prebuild']):
       continue
    #end-if
    
    if(revEntry['LocName'] in alias):
      locList = alias[revEntry['LocName']]
    else:
      locList =      [revEntry['LocName']]
    #end-if
      
    for locName in locList:
      if(bldName == locName or bldName.startswith(locName+':')):
        if(revEntry['Prebuild'] == 1):
          bRatVal  = revEntry['Birthrate']
          targ_gR  = revEntry['Growth']
          mortVecY = demoCalc_GrowTarg(bRatVal, targ_gR)
        if(revEntry['Prebuild'] == 2):
          simplSus = revEntry['InitSusFlat']
          tFracSus = revEntry['InitSusTarg']
        #end-if
      #end-if
    #end-nodeName
  #end-revItem

  # Build SIA calendar
  supplement  = supplem(disease)
  exReg       = bldName + ':'

  # Current node is region or sub-region targeted by SIA
  siaSet1     = [val for val in supplement if exReg.startswith(val[0])]
  siaData     = [(val[1],val[2],val[3],val[4]) for val in siaSet1]

  # Current node is super-region of location targeted by SIA
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
    #end-goDay
  #end-if
  
  # Susceptible Age Groups
  sus_age_groups = [  90.0,  180.0,  270.0,  365.0,  548.0,  730.0,
                    1095.0, 1460.0, 1825.0, 2555.0, 3650.0] 

  # SIA Lists
  siaMinAgeList = [val[0] for val in siaData]
  siaMaxAgeList = [val[1] for val in siaData]  
  siaDateList   = [val[2] for val in siaData] 
  siaTargList   = [val[3] for val in siaData]

  # RI Lists
  riFracList    = [val[0] if len(val)>0 else   0.0   for val in riData] 
  riMeanList    = [val[1] if len(val)>1 else 300.0   for val in riData]
  riStdvList    = [val[2] if len(val)>2 else  45.0   for val in riData]  
  riPrevList    = [val[3] if len(val)>3 else     0   for val in riData]
  riInitList    = [val[4] if len(val)>4 else   0.0   for val in riData]
  riStopList    = [val[5] if len(val)>5 else   1.0e6 for val in riData]

  # Steady-state age distribution
  if(config['Enable_Vital_Dynamics']):
    (gR,ageX,ageY) = demoCalc_AgeDist(bRatVal,mortVecY,bForceVec)
    mFac = (gR**(runYears[0]-popVal[1]))/agentRat
  else:
    gR   = 1.0
    mFac = 1.0

  # Initial susceptibility
  if(config['Enable_Initial_Susceptibility_Distribution']):
    iSX      = [0] + list(np.logspace(1.475,4.540,20,dtype=int))
    if(simplSus):
      iSY      = [round(min(tFracSus,1.0),2) for val in iSX]
    else:
      age_year = np.array(ageY[1:])/365.0
      age_prob = np.diff(np.array(ageX))
      iSP0     = demoCalc_SusTarg(age_year,age_prob,tFracSus)
      iSY      = [round(min(np.exp(iSP0*(val/365.0-0.75)),1.0),4) for val in iSX]
    #end-if

  # Initial population 
  popVal    = int(mFac*popVal[0])

  # Exogeneous challenge rate
  infResVal   = exInf*np.power(popVal/1.0e5,exInfPow)
  endTimeVal  = 365.0*(runYears[1]-1900+1) + 1.0

  # NMFR rate (per day)
  nmfrVal   = repNMFR*(popVal/1.0e5)/365.0

  # ***** Node List *****
  node_set  = list()

  # ***** Node Instance *****
  nodeDic   = dict()

  nodeDic['NodeID'] =                                     nodeVal
  nodeDic['NodeName'] =                                   bldName
  nodeDic['NodeAttributes'] = \
             {'InitialPopulation':                        popVal ,
              'BirthRate':                               bRatVal ,
              'MonthlyBirthForcing':                   bForceVec ,
              'GrowthRate':                                   gR ,
              'InfectivityMultiplier':                       1.0 ,
              'InfectivityReservoirSize':              infResVal ,
              'InfectivityReservoirStartTime':               0.0 ,
              'InfectivityReservoirEndTime':          endTimeVal ,         
              'InfectPulseAmp':                               [] ,
              'InfectPulseStart':                             [] ,
              'InfectPulseStop':                              [] ,
              'LinkList':                                     [] ,
              'LinkListVal':                                  [] ,
              'NMFR':                                    nmfrVal ,
              'SIADates':                            siaDateList ,
              'SIAAgeMin':                         siaMinAgeList ,
              'SIAAgeMax':                         siaMaxAgeList ,
              'SIACoverages':                        siaTargList ,
              'RoutineFrac':                          riFracList ,
              'RoutineMean':                          riMeanList ,
              'RoutineStdv':                          riStdvList ,
              'RoutinePrev':                          riPrevList ,
              'RoutineInit':                          riInitList ,
              'RoutineStop':                          riStopList ,   
              'Latitude':                                geog[1] ,
              'Longitude':                               geog[0] ,
              'Area':                                    areaVal ,
              'SusceptibleAgeGroups':             sus_age_groups , 
              'SurveillanceRate':                           0.00 ,
              'OBR_SIA_Coverage':                           0.75 ,
              'OBR_SIA_MinAge':                              275 ,
              'OBR_SIA_MaxAge':                             1825 }

  nodeDic['IndividualAttributes'] = dict()

  if(config['Enable_Initial_Susceptibility_Distribution']):
    nodeDic['IndividualAttributes']['SusceptibilityDistribution'] = \
               {'DistributionValues':                     [iSX] ,
                'ResultScaleFactor':                          1 , 
                'ResultValues':                           [iSY] }
  if(config['Age_Initialization_Distribution_Type'] == 'DISTRIBUTION_COMPLEX'):
    nodeDic['IndividualAttributes']['SusceptibilityDistribution'] = \
               {'DistributionValues':                    [ageX] ,
                'ResultScaleFactor':                          1 ,
                'ResultValues':                          [ageY] }
  if(config['Enable_Vital_Dynamics'] and config['Enable_Natural_Mortality']):
    nodeDic['IndividualAttributes']['MortalityDistribution'] = \
               {'NumPopulationGroups':        [2,len(mortVecX)] ,
                'NumDistributionAxes':                        2 ,
                'AxisNames':                   ['gender','age'] ,
                'AxisScaleFactors':                       [1,1] ,
                'ResultScaleFactor':                          1 ,
                'PopulationGroups':           [[0,1], mortVecX] ,
                'ResultValues':             [mortVecY,mortVecY] } 

  dickeys = list(nodeDic['NodeAttributes'].keys())
  for kval in dickeys:
    if(kval.startswith('Routine') and len(nodeDic['NodeAttributes'][kval]) == 0):
      nodeDic['NodeAttributes'].pop(kval)
    if(kval.startswith('SIA') and len(nodeDic['NodeAttributes'][kval]) == 0):
      nodeDic['NodeAttributes'].pop(kval)
    if(kval.startswith('InfectPulse') and len(nodeDic['NodeAttributes'][kval]) == 0):
      nodeDic['NodeAttributes'].pop(kval)

  # Omit nodes with negligible population 
  if(popVal >= 5):
    node_set.append(nodeDic)
  #end-if
    
  return (node_set, dict())

#end-singlenode

#********************************************************************************

def multinode(bldName='', nodeVal=1, bldDepth=0):

  # Initialize
  node_set    = list()


  # Check for alias
  if(bldName in alias):
    bldNameList = alias[bldName]

  # Construct recusion tree if no alias
  elif(bldDepth > 0):
    nL1 = list(filter(lambda n: n.startswith(bldName+':'), list(population.keys())))
    bldNameList = list(filter(lambda n: n.count(':')==(bldName.count(':')+1), nL1))
    
    # Decrement depth
    bldDepth = bldDepth - 1

    # Check for over-depth
    if(len(bldNameList) == 0):
      bldNameList = [bldName]
    #end-if

  # No alias and no more depth 
  else:
    bldNameList = [bldName]    
  #end-if


  # Down the rabbit hole
  node_ref = dict()
  ref_list = list()
  for bldNameVal in bldNameList:
    if(bldDepth > 0):
      addNode = multinode(bldName=bldNameVal, nodeVal=nodeVal, bldDepth=bldDepth)
      node_ref.update(addNode[1])
      ref_list.extend(addNode[1][bldNameVal])      
      nodeVal = max(ref_list) + 1
    else:
      addNode = singlenode(bldName=bldNameVal, nodeVal=nodeVal)
      if(len(addNode[0]) == 1):
        node_ref[bldNameVal] = [nodeVal]
        ref_list.append(nodeVal)
        nodeVal = nodeVal + 1
      #end-if
    #end-if
    node_set.extend(addNode[0])
  #end-bldNameVal
  node_ref[bldName] = ref_list
 
  return (node_set, node_ref)

#end-multinode

#********************************************************************************
