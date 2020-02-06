#********************************************************************************
#
# SIA list chooser
#
# Python 3.6.0
#
#********************************************************************************

def dat_factory(setName=''):

  if  (setName=='MEASLES'):
    from file_builders.demograph_data.supplement_measles   import dataList as refData
  elif(setName=='RUBELLA'):
    from file_builders.demograph_data.supplement_rubella   import dataList as refData
  elif(setName=='INFLUENZA'):
    from file_builders.demograph_data.supplement_influenza import dataList as refData
  else:
    raise Exception('Bad disease name: {:s}'.format(setName))
  #end-if
 
  return refData

#end-dat_factory

#********************************************************************************
