#********************************************************************************
#
# Writes a python dictionary as a json-file
#
# Python 3.6.0
#
#********************************************************************************

def writeDict(fileID, pDict, regName='', numIndent=0, pyCon=False):

  # Last item enumeration
  #   First item in dic -> lItem = 0
  lItem = 0

  # Prep indent
  wsp1 = numIndent*' '
  wsp2 = wsp1 + '  '

  # Write parameter list
  #   Key value (regName) must be string; top level dic may not have key value
  if(regName != ''):
    fileID.write(wsp1+'"'+regName+'":\n')
  #end-if
  fileID.write(wsp1+'{\n')

  # Key values (strings) get sorted because why not
  keylist = list(pDict.keys())
  keylist.sort()
  for kval01 in keylist:
    # Extra line if not first item
    if(lItem != 0):
      fileID.write(',\n')
    #end-if
      
    if(isinstance(pDict[kval01],str)):      # Item Type 1  (string)
      fileID.write(wsp2+'"')
      fileID.write(kval01+'": ')
      fileID.write('"'+str(pDict[kval01])+'"')
      lItem = 1
    elif(isinstance(pDict[kval01],list)):   # Item Type 2  (list)
      fileID.write(wsp2+'"')
      fileID.write(kval01+'": \n')
      writeList(fileID, pDict[kval01], numIndent+2, pyCon)
      lItem = 2
    elif(isinstance(pDict[kval01],dict)):   # Item Type 3  (dic)
      writeDict(fileID, pDict[kval01], kval01, numIndent+2, pyCon)
      lItem = 3
    elif(pDict[kval01] is None):            # Item Type 4a (null)
      fileID.write(wsp2+'"')
      fileID.write(kval01+'": ')
      if(not pyCon):
        fileID.write('null')
      else:
        fileID.write('None')
      #end-if      
      lItem = 4
    elif(isinstance(pDict[kval01],bool)):   # Item Type 4b (boolean)
      fileID.write(wsp2+'"')
      fileID.write(kval01+'": ')
      if(pDict[kval01]):
        if(not pyCon):
          fileID.write('true')
        else:
          fileID.write('True')
        #end-if
      else:
        if(not pyCon):        
          fileID.write('false')
        else:
          fileID.write('False')
        #end-if
      #end-if        
      lItem = 4
    else:                                   # Item Type 5  (numeric)
      fileID.write(wsp2+'"')
      fileID.write(kval01+'": ')
      if(pDict[kval01]==int(pDict[kval01])):
        fileID.write('{:d}'.format(int(pDict[kval01])))
      else:
        fileID.write('{:g}'.format(pDict[kval01]))
      #end-if
      lItem = 5
    #end-if
  #end-pairval01

  fileID.write('\n')
  fileID.write(wsp1+'}')

  return

#end-writeFlat

#********************************************************************************
#
# Writes a python list as a json-file
#
# Python 3.6.0
#
#********************************************************************************

def writeList(fileID, pList, numIndent=0, pyCon=False):

  # Last item enumeration
  #   First item in list -> lItem = 0  
  lItem = 0
  
  # Prep indent
  wsp1 = numIndent*' '
  wsp2 = wsp1 + '  '

  # Write parameter list
  fileID.write(wsp1+'[\n')
      
  for listval01 in pList:
    # Comma after last item if not first item    
    if(lItem != 0):
      fileID.write(',')
    #end-if
    # New line if last item was dic
    if(lItem == 2 or lItem == 3):
      fileID.write('\n')
    #end-if
          
    if(isinstance(listval01,str)):       # Item Type 1  (string)
      if(lItem == 0 or lItem == 2 or lItem == 3):
        fileID.write(wsp2)
      #end-if
      fileID.write('"'+str(listval01)+'"')
      lItem = 1
    elif(isinstance(listval01,list)):    # Item Type 2  (list)
      if(lItem == 1 or lItem == 4 or lItem == 5):
        fileID.write('\n')
      #end-if        
      writeList(fileID, listval01, numIndent+2, pyCon)
      lItem = 2
    elif(isinstance(listval01,dict)):    # Item Type 3  (dic)
      if(lItem == 1 or lItem == 5):
        fileID.write('\n')
      #end-if        
      writeDict(fileID, listval01, '', numIndent+2, pyCon)
      lItem = 3
    elif(listval01 is None):             # Item Type 4a (null)
      if(lItem == 0 or lItem == 2 or lItem == 3):
        fileID.write(wsp2)
      #end-if      
      if(not pyCon):
        fileID.write('null')
      else:
        fileID.write('None')
      #end-if  
      lItem = 4
    elif(isinstance(listval01,bool)):    # Item Type 4b (boolean)
      if(lItem == 0 or lItem == 2 or lItem == 3):
        fileID.write(wsp2)
      #end-if      
      if(listval01):
        if(not pyCon):
          fileID.write('true')
        else:
          fileID.write('True')
        #end-if
      else:
        if(not pyCon):        
          fileID.write('false')
        else:
          fileID.write('False')
        #end-if
      #end-if
      lItem = 4          
    else:                                # Item Type 5  (numeric)
      if(lItem == 0 or lItem == 2 or lItem == 3):
        fileID.write(wsp2)
      #end-if
      if(listval01==int(listval01)):
        fileID.write('{:d}'.format(int(listval01)))
      else:
        fileID.write('{:g}'.format(listval01))
      #end-if
      lItem = 5      
    #end-if
  #end-listval01
        
  fileID.write('\n'+wsp1+']')

  return

#end-writeList

#********************************************************************************
