#********************************************************************************
#
# Trace up a dot-name string for an apporpriate dictionary entry
#
# Python 3.6.0
#
#********************************************************************************

def inheritor(place='', dataDic={}):

  if(place in dataDic):
    return(dataDic[place])
  else:
    while(len(place)>0):
      place = place.rpartition(':')[0]
      if(place in dataDic):
        return(dataDic[place])
      #end-if
    #end-while
    raise Exception('No acceptable default values.')
  #end-if

#end-birthforce

#********************************************************************************
