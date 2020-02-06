#********************************************************************************
#
# Builds a demographics.json file to be used as input to the DTK.
#
# Python 3.6.0
#
#********************************************************************************

import numpy as np

from io                                     import StringIO   as fstream

from file_builders.writeFlat                import writeDict
from file_builders.demoNodes                import multinode
from file_builders.demograph_data.alias     import dataDic    as  alias

from genParams                              import dataDic    as gParam
from simParams                              import dataDic    as pDic

import global_data

#********************************************************************************

def demoBuilder():

  # Glabal parameters
  demoAlts = global_data.DEMO_ALTS

  # Simulation parameters
  bldName   = gParam['bldName']
  bldDepth  = gParam['bldDepth']
  netCoeff  = gParam['network_coeff']
  netPower  = gParam['network_power']
  obrad     = gParam['outbreak_radius']  

  # Create string buffers
  pDat1 = fstream()
  pDat2 = fstream()  

  # Dictionary of parameters to be written
  json_set = {}



  # ***** Detailed node attributes *****
  addNode = multinode(bldName=bldName, bldDepth=bldDepth)

  # Add node list
  json_set['Nodes'] = addNode[0]
  node_ref          = addNode[1]
  numNodes          = len(json_set['Nodes'])
  node_ref['ALL']   = list(range(1,numNodes+1))



  # ***** Metadata attributes *****
  # Create metadata dictionary
  json_set['Metadata'] = { 'IdReference':   'kfrey-custom' }



  # ***** Network Infectivity *****
  # Full gravity model
  for nodeDic1 in json_set['Nodes']:
    for nodeDic2 in json_set['Nodes']:
      nid1  = nodeDic1['NodeID']
      nid2  = nodeDic2['NodeID']
      if(nid1 == nid2):
        continue
      lat1  = nodeDic1['NodeAttributes']['Latitude']
      long1 = nodeDic1['NodeAttributes']['Longitude']
      lat2  = nodeDic2['NodeAttributes']['Latitude']
      long2 = nodeDic2['NodeAttributes']['Longitude']
      delt  = hDist(lat1,long1,lat2,long2)
      linkv = netCoeff/(delt**netPower) if delt > 0 else 1.0
      nodeDic1['NodeAttributes']['LinkList'].append(nid2)
      nodeDic1['NodeAttributes']['LinkListVal'].append(linkv)
    #end-nodeDic2
  #end-nodeDic1



  # ********************************

  # Update parameter dictionary
  for revEntry in demoAlts:
    if('Prebuild' in revEntry and revEntry['Prebuild']):
       continue
    #end-if
    
    if(revEntry['LocName'] in alias):
      locList = alias[revEntry['LocName']]
    else:
      locList =      [revEntry['LocName']]
    #end-if

    for locName in locList:
      for nodeDic in json_set['Nodes']:
        if( nodeDic['NodeName'] == locName or
           (nodeDic['NodeName']).startswith(locName+':') ):
          revDemo(mainDic=nodeDic, altDic=revEntry)
        #end-if
      #end-nodeDic
    #end-nodeName
          
  #end-revItem

  # Ensure that SIAs are in REVERSE chronological order
  for nodeDic in json_set['Nodes']:
    if('SIADates' in nodeDic['NodeAttributes']):
      sIdx = np.argsort(nodeDic['NodeAttributes']['SIADates'])[::-1]
      nList = (np.array(nodeDic['NodeAttributes']['SIADates'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['SIADates']      = nList
      nList = (np.array(nodeDic['NodeAttributes']['SIAAgeMin'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['SIAAgeMin']     = nList
      nList = (np.array(nodeDic['NodeAttributes']['SIAAgeMax'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['SIAAgeMax']     = nList
      nList = (np.array(nodeDic['NodeAttributes']['SIACoverages'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['SIACoverages']  = nList
    #end-nodeDic

  # Ensure that RI ages are in STANDARD chronological order
  for nodeDic in json_set['Nodes']:
    if('RoutineMean' in nodeDic['NodeAttributes']):
      sIdx = np.argsort(nodeDic['NodeAttributes']['RoutineMean'])
      nList = (np.array(nodeDic['NodeAttributes']['RoutineMean'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['RoutineMean']  = nList
      nList = (np.array(nodeDic['NodeAttributes']['RoutineFrac'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['RoutineFrac']  = nList
      nList = (np.array(nodeDic['NodeAttributes']['RoutineStdv'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['RoutineStdv']  = nList
      nList = (np.array(nodeDic['NodeAttributes']['RoutinePrev'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['RoutinePrev']  = nList
      nList = (np.array(nodeDic['NodeAttributes']['RoutineInit'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['RoutineInit']  = nList
      nList = (np.array(nodeDic['NodeAttributes']['RoutineStop'])[sIdx]).tolist()
      nodeDic['NodeAttributes']['RoutineStop']  = nList
    #end-nodeDic

  # End file construction
  writeDict(pDat1, json_set, pyCon=False)
  pDatStr1 = pDat1.getvalue()
  writeDict(pDat2, node_ref, pyCon=True)
  pDatStr2 = pDat2.getvalue()


  # Global variable assignment
  global_data.DEMOGRAPHICS = json_set
  global_data.NODE_CODE    = node_ref
  global_data.SIA_RECORD   = np.zeros(numNodes+1)
  
  for nodeDic1 in json_set['Nodes']:
    dotname = nodeDic1['NodeName'].split(':')
    if(len(dotname) > 1):
      global_data.region[nodeDic1['NodeID']]    = dotname[1]
    else:
      global_data.region[nodeDic1['NodeID']]    = dotname[0]
    #end-if
    if(len(dotname) > 2):
      global_data.province[nodeDic1['NodeID']]  = dotname[2]
    else:
      global_data.region[nodeDic1['NodeID']]    = dotname[0]
    #end-if
      
    global_data.neighbors[nodeDic1['NodeID']] = tuple()
    for nodeDic2 in json_set['Nodes']:
      nid1  = nodeDic1['NodeID']
      nid2  = nodeDic2['NodeID']
      if(nid1 == nid2):
        continue
      lat1  = nodeDic1['NodeAttributes']['Latitude']
      long1 = nodeDic1['NodeAttributes']['Longitude']
      lat2  = nodeDic2['NodeAttributes']['Latitude']
      long2 = nodeDic2['NodeAttributes']['Longitude']
      delt  = hDist(lat1,long1,lat2,long2)
      if(delt < 200):
        global_data.neighbors[nodeDic1['NodeID']] = \
             global_data.neighbors[nodeDic1['NodeID']] + (nid2,)
    #end-nodeDic2
  #end-nodeDic1

    
  return (pDatStr1,pDatStr2)

#end-demoBuilder

#********************************************************************************

# Updates values within NodeAttributes
def revDemo(mainDic={}, altDic={}):

  nA = 'NodeAttributes'
  vN = altDic['VarName']

  if(isinstance(mainDic[nA][vN],list)):
    if(altDic['ModType'] == 'APPEND'):
      (mainDic[nA][vN]).append(altDic['Value'])
    elif(altDic['ModType'] == 'CLEAR'):
      (mainDic[nA][vN]) = []
    else:
      if(altDic['IdxVal'] == 'ALL'):
        for k1 in range(len(mainDic[nA][vN])):
          mainDic[nA][vN][k1] = revVal(mainVal =mainDic[nA][vN][k1],
                                       newVal  =altDic['Value'],
                                       calcType=altDic['ModType'])
        #end-k1
      elif(altDic['IdxVal'] == 'CONDS'):
        bList1 = [True]*len(mainDic[nA][vN])
        for cSet in altDic['Conds']:
          bList2 = [compVal(val1, cSet[2], compType=cSet[1])
                            for val1 in mainDic[nA][cSet[0]]]
          bList1 = [bList1[k1] and bList2[k1] for k1 in range(len(bList1))]
        #end-cSet
        for k1 in range(len(bList1)):
          if(bList1[k1]):
            mainDic[nA][vN][k1] = revVal(mainVal =mainDic[nA][vN][k1],
                                         newVal  =altDic['Value'],
                                         calcType=altDic['ModType'],)
          #end-if
        #end-k1
      else:
        k1 = int(altDic['IdxVal'])
        mainDic[nA][vN][k1] = revVal(mainVal =mainDic[nA][vN][k1],
                                     newVal  =altDic['Value'],
                                     calcType=altDic['ModType'])
      #end-if
    #end-if
  else:
    mainDic[nA][vN] = revVal(mainVal =mainDic[nA][vN],
                             newVal  =altDic['Value'],
                             calcType=altDic['ModType'])
  #end-if     

  return None
 
#end-revDemo

#*******************************************************************************

# Calculates new value
def revVal(mainVal=0.0, newVal=0.0, calcType=''):

  if(calcType == 'REPLACE'):
    retVal = newVal
  elif(calcType == 'MULT'):
    retVal = newVal * mainVal
  elif(calcType == 'ADD'):
    retVal = newVal + mainVal
  elif(calcType == 'RMULT'):
    if(newVal > 0):
      retVal = 1-(1-mainVal)*(1-newVal)
    else:
      retVal =   (  mainVal)*(1+newVal)
    #end-if
  elif(calcType == 'JITTER'):
    altVal = newVal*np.random.normal()
    if(altVal > 0):
      retVal = 1-(1-mainVal)*(1-altVal)
    else:
      retVal =   (  mainVal)*(1+altVal)
    #end-if
  #end-if

  return retVal
 
#end-revVal

#*******************************************************************************

# Compares two values
def compVal(val1, val2, compType=''):

  if(compType == 'LT'):
    retVal = val1 <  val2
  elif(compType == 'LE'):
    retVal = val1 <= val2
  elif(compType == 'EQ'):
    retVal = val1 == val2
  elif(compType == 'GE'):
    retVal = val1 >= val2
  elif(compType == 'GT'):
    retVal = val1 >  val2
  #end-if

  return retVal
 
#end-compVal

#*******************************************************************************

# Calculated haversine distance
def hDist(lat1=0.0, long1=0.0, lat2=0.0, long2=0.0):

  lat1  = np.pi*lat1 /180.0
  lat2  = np.pi*lat2 /180.0
  long1 = np.pi*long1/180.0
  long2 = np.pi*long2/180.0

  delt = 6371*2*np.arcsin(np.sqrt(np.sin(0.5*lat2-0.5*lat1)**2 +
                     np.cos(lat2)*np.cos(lat1)*np.sin(0.5*long2-0.5*long1)**2))

  return delt
 
#end-hDist

#*******************************************************************************
