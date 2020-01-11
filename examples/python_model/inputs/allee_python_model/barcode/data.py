import os
import warnings
import time
from datetime import datetime

import json

import numpy as np
import pandas

import barcode.unittests as bu
import barcode.barcode as bc



'''
Read in barcode data from csv files
Outputs:
  dfSpatial - barcodes from Senegal, focused around Thies, matched with GPS and timestamp
  dfZambia - barcodes from Zambia, with GPS, house IDs, and timestamps
  dfThies - barcodes from Thies, Senegal, more comprehensive list with only the year, and no GPS
'''
def readData():
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_path,'..','data', 'Zambia_SupplementalTables_20180806.csv')
    dfZambia = pandas.read_csv(filepath)
    filepath = os.path.join(current_path,'..','data', 'BarcodeAndSpatialData.csv')
    dfSpatial = pandas.read_csv(filepath, encoding='ISO-8859-1')
    filepath = os.path.join(current_path,'..','data', 'Updated_Thies_2016_Modified.csv')
    dfThies = pandas.read_csv(filepath, encoding='ISO-8859-1')
    return dfZambia, dfSpatial, dfThies



'''
Read in PNAS data
'''
def readPNAS():
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_path,'..','data', 'pnas.1505691112.sd01.csv')
    df1 = pandas.read_csv(filepath)
    filepath = os.path.join(current_path,'..','data', 'pnas.1505691112.sd02.csv')
    df2 = pandas.read_csv(filepath)
    filepath = os.path.join(current_path,'..','data', 'pnas.1505691112.sd03.csv')
    df3 = pandas.read_csv(filepath)
    return df1, df2, df3



def getIntBarcode(barcodeDF):
    
    # Count no. of C,G,A,T for each column
    barcode = bc.getBarcode(barcodeDF)
    nC = np.sum(barcode=='C',axis=0)
    nG = np.sum(barcode=='G',axis=0)
    nA = np.sum(barcode=='A',axis=0)
    nT = np.sum(barcode=='T',axis=0)
    nX = np.sum(barcode=='X',axis=0)
    nN = np.sum(barcode=='N',axis=0)
    tally = np.array( [nC.tolist(),nG.tolist(),nA.tolist(),nT.tolist()] )
    
    # Make a reference barcode by picking more prevalent allele for each column
    whereMajor = np.argmax(tally,axis=0)
    refBarcode = whereMajor.astype('str')
    
    # Initialize a numerical array to add values correctly in next step
    barcodeNew = np.zeros(list(barcode.shape))

    # Catergorize each SNP as major, minor, N, or X, going by columns
    for i,w in enumerate(whereMajor.tolist()):
        if w==0:
            letter = 'C'
        elif w==1:
            letter = 'G'
        elif w==2:
            letter = 'A'
        else:
            letter = 'T'
        refBarcode[i] = letter
        barcodeNew[:,i] = 1*np.isin(barcode[:,i],letter) + \
                          3*np.isin(barcode[:,i],'N') + \
                          4*np.isin(barcode[:,i],'X') + \
                          10*np.isin(barcode[:,i],['C','G','A','T'])
    #
    # Convert chars to ints
    # Any element == 10 is one that didn't match with reference barcode, so it's a minor allele
    barcode = barcodeNew.astype(float)
    barcode[ barcode==10 ] = 2.
    barcode[ barcode==11 ] = 1.
    barcode[ barcode==0 ] = np.NaN
    return barcode
    



'''
This is currently kind of silly because each data set has its quirks

Convert data imported with readData into format easy for analysis
Inputs:
  dfSpatial - see readData
  dfZambia
  dfThies
  integerCode - convert barcode to integer format, where
    1 - major allele
    2 - minor allele
    3 - N
    4 - X
Outputs:
  dfZ - pandas dataframe of Zambia data (with some formatting)
  dfS - pandas dataframe for Senegal
  dfT - pandas dataframe for Thies, no cuts
'''
def convertData(dfZambia, dfSpatial, dfThies, dfPNAS=[], integerCode=1, verbose=1):
    t0 = time.time()

    if verbose>=1:
        print('Zambia data:')

    # Convert GPS data to floats
    dfZ = dfZambia.copy()
    dfZ['Lat'] = dfZ['Latitude'].apply(lambda x: float(x)).values
    dfZ['Lon'] = dfZ['Longitude'].apply(lambda x: float(x)).values

    # Convert time data to datetime
    dfZ['Date'] = pandas.to_datetime(dfZ['Date'],errors='coerce')

    # Add year column for consistency with Senegal datasets
    dfZ['Year'] = dfZ['Date'].apply(lambda x: x.year).values

    # Turn barcode into array
    dfZ['A1'] = dfZ['A1'].apply(lambda x: x[-1] if x==x else np.NaN).values  # Remove '\t' from beginning of str
    dfZ['Barcode'] = dfZ[['A1','B1','A2','B2','A3','B3','A4','B4',
                          'A5','B5','A6','B6','A7','B7','A8','B8',
                          'A9','B9','A10','B10','A11','B11','A12','B12']].values.tolist()
    if integerCode:
        dfZ['Barcode'] = getIntBarcode(dfZ).tolist()

    # Add other potentially useful columns
    dfZ['Complexity'] = dfZ['P/M']
    dfZ.loc[dfZ.Complexity.values != dfZ.Complexity.values,['Complexity']] = -1
    dfZ.loc[dfZ.Complexity.values == 'Mono',['Complexity']] = 1
    dfZ.loc[dfZ.Complexity.values == 'Poly',['Complexity']] = 2

    if verbose >= 2:
        print('Column list: ',dfZ.columns.tolist())

    # Do we have enough entries to use in analysis?
    nSamps = len(dfZ)
    if verbose >= 1:
        print('# samples:',nSamps)
        
    if verbose >= 1:
        print('Time elapsed:', time.time() - t0)
        print('')

    '''
    Repeat for Senegal data (Spatial processed)
    '''

    if verbose>=1:
        print('Senegal data:')

    # Convert GPS and time data to floats
    dfS = dfSpatial.copy()
    dfS['Lat'] = dfS['Lat'].apply(lambda x: float(x)).values
    dfS['Lon'] = dfS['Long'].apply(lambda x: float(x)).values
    dfS['Date_orig'] = dfS['Date'].apply(lambda x: float(x)).values

    # Convert Date to datetime
    # Year column already exists
    dfS.Date = dfS.Date.apply(lambda x: float(x) if x==x else np.NaN)
    dfS.Date = dfS.Date.apply(lambda x: datetime.fromordinal(int(x)) if x==x else np.NaN)

    # Turn barcode into array
    dfS['Barcode'] = dfS[['Pos 1','Pos 2','Pos 3','Pos 4','Pos 5','Pos 6',
                          'Pos 7','Pos 8','Pos 9','Pos 10','Pos 11','Pos 12',
                          'Pos 13','Pos 14','Pos 15','Pos 16','Pos 17','Pos 18',
                          'Pos 19','Pos 20','Pos 21','Pos 22','Pos 23','Pos 24']].values.tolist()

    # Add other potentially useful columns
    dfS['Complexity'] = np.NaN #dfZ['P/M']
    dfS['ID'] = dfS['SampleID']

    if verbose>=2:
        print('Column list: ',dfS.columns.tolist())

    # Keep only samples with GPS data, if 'cut' is True
    nSamps = len(dfS)
    if verbose>=1:
        print('# samples:',nSamps)    
    #if cut:
    #    dfS = dfS.loc[ (dfS['Lat']==dfS['Lat']) & (dfS['Lon']==dfS['Lon'])].reset_index()
    #    nSamps = len(dfS)
    #    if verbose>=1:
    #        print('# samples after cut: ',nSamps)

    if verbose>=1:
        print('Time elapsed:', time.time() - t0)
        print('')

    '''
    Repeat for Senegal data (just Thies barcodes)
    '''

    if verbose>=1:
        print('Thies, Senegal data:')

    # Convert time data to floats
    dfT = dfThies.copy()
    # This data has no detailed time or space data
    dfT['Lat'] = np.NaN
    dfT['Lon'] = np.NaN
    dfT['Date'] = np.NaN
    dfT['Complexity'] = np.NaN
    dfT['ID'] = dfT['Sample Name']

    # Dates
    dfT['Date'] = bc.getDatesOrYear(dfT,option=2)
    dfT.Date = dfT.Date.apply(lambda x: datetime.fromordinal(int(x)) if x==x else np.NaN)

    # Turn barcode into array
    dfT['Barcode'] = dfT[['A1','B1','A2','B2','A3','B3','A4','B4',
                          'A5','B5','A6','B6','A7','B7','A8','B8',
                          'A9','B9','A10','B10','A11','B11','A12','B12']].values.tolist()
    if integerCode:
        dfT['Barcode'] = getIntBarcode(dfT).tolist()

    if verbose>=2:
        print('Column list: ',dfT.columns.tolist())

    nSamps = len(dfT)
    if verbose>=1:
        print('# samples:',nSamps)    

    if verbose>=1:
        print('Time elapsed:', time.time() - t0)
        print('')

    # Reorder columns and only keep the ones we need
    dfZ = dfZ[['ID','Date','Lat','Lon','Barcode','Complexity','Year']]
    dfS = dfS[['ID','Date','Lat','Lon','Barcode','Complexity','Year']]
    dfT = dfT[['ID','Date','Lat','Lon','Barcode','Complexity','Year']]

    '''
    Convert df1 if provided
    '''
    if len(dfPNAS) > 0:
        if verbose>=1:
            print('Senegal data, from PNAS:')

        # Convert time data to floats
        dfP = dfPNAS.copy()
        # This data has no detailed time or space data
        dfP['Lat'] = np.NaN
        dfP['Lon'] = np.NaN
        dfP['Complexity'] = np.NaN
        dfP['ID'] = dfP['name']

        # Dates
        dfP['Year'] = dfP.year
        dfP['Date'] = bc.getDatesOrYear(dfP,option=2)
        dfP.Date = dfP.Date.apply(lambda x: datetime.fromordinal(int(x)) if x==x else np.NaN)

        # Turn barcode into array
        dfP['Barcode'] = dfP[['molecular barcode','Unnamed: 4','Unnamed: 5','Unnamed: 6',
                              'Unnamed: 7','Unnamed: 8','Unnamed: 9','Unnamed: 10',
                              'Unnamed: 11','Unnamed: 12','Unnamed: 13','Unnamed: 14',
                              'Unnamed: 15','Unnamed: 16','Unnamed: 17','Unnamed: 18',
                              'Unnamed: 19','Unnamed: 20','Unnamed: 21','Unnamed: 22',
                              'Unnamed: 23','Unnamed: 24','Unnamed: 25','Unnamed: 26']].values.tolist()
        if integerCode:
            dfP['Barcode'] = getIntBarcode(dfP).tolist()

        if verbose>=2:
            print('Column list: ',dfP.columns.tolist())

        nSamps = len(dfT)
        if verbose>=1:
            print('# samples:',nSamps)    

        if verbose>=1:
            print('Time elapsed:', time.time() - t0)
            print('')

        return dfZ, dfS, dfT, dfP

    
    return dfZ, dfS, dfT





'''
Remove faulty entries from dataframe
Inputs:
  df0 - barcode dataframe to be trimmed
  cut - option to remove entries by a set of filters, listed as an array
    If length is 0 do no cuts, else each element is a flag for one of the filters
    below in the following order:
      1st: if 1/True, cut entries without GPS data
      2nd: if 1, cut entries without valid barcode data
    If multiple flags are set, the set of cut elements is the union of the sets for each flag
Outputs:
  df - trimmed dataframe
'''
def cutData(df0, cut=[1], yearbound=[], verbose=1):

    df = df0.copy()

    nSamps = len(df)
    if verbose >= 2:
        print('# samples:',nSamps)

    # Keep only samples with GPS data and/or valid entries, as specified by 'cut'
    if len(cut) > 0:
        cut = cut+[0]*(3-len(cut)) #If not all elements/flags set, fill rest of array
        keep = np.ones(nSamps).astype('bool')
        if cut[0]:
            keep = keep & (df['Lat']==df['Lat']) & (df['Lon']==df['Lon'])
        if cut[1]:
            barcode = bc.getBarcode(df)
            blength = len(barcode[0])
            btype = bu.validBarcode(barcode)
            if btype==2:
                keep = keep & (np.sum(np.isin(barcode,['C','G','A','T','X','N']),axis=1) == blength)
            elif btype==1:
                keep = keep & (np.sum(np.isin(barcode,[1,2,3,4]),axis=1) == blength)
            else:
                print('Unknown barcode type. Ignoring barcode cut flag.')
        df = df.loc[ keep ].reset_index()
        nSamps = len(df)
        if verbose >= 1:
            print('# samples after cut: ',nSamps)

    if len(yearbound) == 2:
        keep = (df['Year']>=yearbound[0]) & (df['Year']<=yearbound[1])
        df = df.loc[ keep ].reset_index()
        nSamps = len(df)
        if verbose >= 1:
            print('# samples after year cut: ',nSamps)

    return df





'''
json input/output
'''

# From https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def saveJson(fname,jsonData):
    with open(fname,'w') as f:
        json.dump(jsonData,f,cls=NumpyEncoder)
    return 1

    
def saveFits(fname, samples, logArray, statArray):
    jsonDict = {'samples':samples.tolist(), 
                'logLArray':logArray.tolist(),
                'statArray':statArray.tolist()}
    _ = saveJson(fname,jsonDict)
    return 1





def readJson(file):
    with open(file) as f:
        jsonData = json.load(f)
    return jsonData

    
def getGrid(gridFile):
    jsonData = readJson(gridFile)
    return np.array(jsonData)
