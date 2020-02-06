#********************************************************************************
#
# Builds a python file out of a dictionary.
#
# Python 3.6.0
#
#********************************************************************************

from io       import StringIO as fstream

from file_builders.writeFlat   import writeDict

#********************************************************************************

def pydicBuilder(pydic = {}):

  # Create string buffer
  pDat = fstream()

  # Module definition  
  pDat.write('#'+'*'*79+'\n')
  pDat.write('#\n')
  pDat.write('# Python 3.6.0\n')
  pDat.write('#\n')
  pDat.write('#'+'*'*79+'\n')
  pDat.write('\n')
  
  pDat.write('dataDic = \\\n')
  writeDict(pDat, pydic, numIndent=4, pyCon=True)

  pDat.write('\n\n')
  pDat.write('#'+'*'*79+'\n')

  # End file construction
  pDatStr = pDat.getvalue()

  return pDatStr

# end-pydicBuilder

#********************************************************************************
