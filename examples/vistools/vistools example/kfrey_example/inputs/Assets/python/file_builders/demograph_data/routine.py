#********************************************************************************
#
# Routine immunization chooser
#
# Python 3.6.0
#
#********************************************************************************

def dat_factory(setName=''):

  if  (setName=='MEASLES'):
    from file_builders.demograph_data.routine_measles   import dataDic as refData
  elif(setName=='RUBELLA'):
    from file_builders.demograph_data.routine_rubella   import dataDic as refData
  elif(setName=='INFLUENZA'):
    from file_builders.demograph_data.routine_influenza import dataDic as refData
  else:
    raise Exception('Bad disease name: {:s}'.format(setName))
  #end-if
 
  return refData

#end-dat_factory

#********************************************************************************







