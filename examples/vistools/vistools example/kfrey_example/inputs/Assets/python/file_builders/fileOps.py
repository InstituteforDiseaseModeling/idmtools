#********************************************************************************
#
# Python 3.6.0
#
#********************************************************************************

import os, shutil, json

from file_struct.filePaths        import fileDic

#********************************************************************************

# Check / create / clear directory
def CCCdir(dirNameJ='.', clearOld=False):

  if(not os.path.isdir(dirNameJ)):
    os.makedirs(dirNameJ)
  #end-if
    
  if(clearOld):  
    fList = os.listdir(dirNameJ)
    for fName in fList:
      fNameJ = os.path.join(dirNameJ,fName) 
      if(not os.path.isdir(fNameJ)):
        os.remove(fNameJ)
      else:
        shutil.rmtree(path=fNameJ,ignore_errors=True)
      #end-if
    #end-fName
  #end-if

  return None

#end-CCCdir

#********************************************************************************

# Write a dictionary to results directory
def saveResults(simName='', jsonDic={}, fileName=''):
  
  # Directory pathway
  wdirNameJ = os.path.join(fileDic['dtkOutDir'],simName)
  wdirNameJ = os.path.join(wdirNameJ,'results')

  # Check results directory
  CCCdir(wdirNameJ)

  # Write json file
  foutNameJ = os.path.join(wdirNameJ,fileName+'.json')
  with open(foutNameJ,'w') as resFile:
    json.dump(jsonDic, resFile, separators=(',',':'))
  #end-resFile

  return None

#end-saveResults

#********************************************************************************
    
# Retrieve a dictionary from results directory
def loadResults(simName='', fileName=''):
  
  # Directory pathway
  wdirNameJ = os.path.join(fileDic['dtkOutDir'],simName)
  wdirNameJ = os.path.join(wdirNameJ,'results')
  wfilNameJ = os.path.join(wdirNameJ,fileName+'.json')  

  # Check results directory
  CCCdir(wdirNameJ)

  # Read json file
  if(os.path.isfile(wfilNameJ)):
    with open(wfilNameJ,'r') as jfil:
      loadDic = json.load(jfil)
    #end-jfil
  else:
    loadDic = {}
  #end-if

  return loadDic

#end-loadResults

#********************************************************************************
