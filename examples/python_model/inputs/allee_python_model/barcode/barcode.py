import os
import warnings
import time
from datetime import datetime

import numpy as np
import pandas
import scipy

import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors




# TO DO
# Matrix builders may go in a utils.py file?



'''
Constants and reference variables
'''
reftypeTimestamp = type(np.datetime64('2005-02-25'))

nSNPs = 24
base4array = np.power( np.ones(nSNPs).astype('uint64')*4, nSNPs-1-np.arange(nSNPs) )
binTemplate1 = int('01'*nSNPs,2)
binTemplate2 = int('10'*nSNPs,2)


'''
Return barcodes as numpy array
(not array of lists, which is what barcodeDF['Barcode'].values does)
'''
def getBarcode(barcodeDF, rows=[]):
    return np.vstack(barcodeDF['Barcode'].values) if len(rows)==0 \
           else np.vstack(barcodeDF.loc[rows,'Barcode'].values)


'''
Functions for getting dates or years from dataframe as numpy array
'''
def convertTime(x):
    try:
        y = x.toordinal()
    except ValueError:
        return np.nan
    except AttributeError:
        return np.nan
    else:
        return y
    

def getDates(barcodeDF, rows=[]):
    if len(rows)==0:
        dates = barcodeDF['Date'].apply(lambda x: convertTime(x)).values
    else:
        dates = barcodeDF.loc[rows,'Date'].apply(lambda x: convertTime(x)).values
    return dates


'''
Return ordinal dates or year in units of days or years
Inputs:
  barcodeDF - pandas dataframe in barcode format
  rows - selects rows to return
    if empty, returns all
  option - chooses between time formats
    1 - Get ordinal time in units of days
    2 - Get years converted into ordinal time with units of days
    3 - Get years converted to ordinal time if 'Date' is invalid, else get ordinal time from 'Date'
    4 - Get years in units of years
'''
def getDatesOrYear(barcodeDF, rows=[], option=1):
    if option==4:
        dates = barcodeDF['Year'].values
    elif option==3:
        barcodeTemp = barcodeDF.copy()
        barcodeTemp['Date'] = barcodeTemp['Year'].values.astype(int).astype(str)
        barcodeTemp['Date'] = barcodeTemp['Date'].apply(lambda x: np.datetime64(x,'D'))
        dates = getDates(barcodeTemp)
        datesOrig = getDates(barcodeDF)
        dates[(dates != dates)] = datesOrig[(dates != dates)]
    elif option==2:
        # Maybe move this inside getDates()?
        barcodeTemp = barcodeDF.copy()
        barcodeTemp['Date'] = barcodeTemp['Year'].values.astype(int).astype(str)
        barcodeTemp['Date'] = barcodeTemp['Date'].apply(lambda x: np.datetime64(x,'D'))
        dates = getDates(barcodeTemp)
    else:
        dates = getDates(barcodeDF)
    return dates




'''
Computes genetic distance between two barcodes using some metric specified by option
Inputs:
  b1 - barcode 1
  b2 - barcode 2
  option - chooses between metric formulations
    0 - L1 norm
    1 - L2 norm
    2 - Poisson point mutation model (used in POTN in Famulare&Hu 2014)
Outputs:
  relation - evaluation of distance (scalar)
'''
# To do - change order of options?
def relateBarcode(b1,b2, option=1):

    if option==1:    # L2 norm
        relation = np.sqrt( np.sum( (b1 == b2) ) )
    elif option==2:  # Poisson point mutation model
        m = np.sum(b1!=b2)
        r = 1        # Rate (pt mutation per gen/day) - eventually feed in as parameter
        deltat = 1   # Time between observations - feed in with data
        relation = np.power(r*deltat,m)*np.exp(-(r*delta))/scipy.special.gamma(m+1)
    else:            # L1 norm
        relation = np.sum(b1==b2)

    return relation





def getRelation0(barcodeDF, fillLowerLeft=0, useAll=0, option=1, gps=1, getTime=1,
                verbose=1):

    nSamps = len(barcodeDF)

    # Initialize matrix for storing relation coefficients
    relation = np.zeros([nSamps,nSamps])
    dr = np.zeros([nSamps,nSamps])
    dt = np.zeros([nSamps,nSamps])

    # Save df data to numpy arrays for faster access
    barcode = getBarcode(barcodeDF)
    latLon = barcodeDF[['Lat','Lon']].values
    dates = getDatesOrYear(barcodeDF, option=time)
    if np.sum(np.isnan(dates)) == nSamps:
        getTime = 0
    if getTime:
        minDate = np.nanmin(dates)
        maxDate = np.nanmax(dates)
        sDates = (dates-minDate)/(maxDate-minDate) #scaled Dates

    # Assume geographic locus is small enough that we just need one transformation
    if gps:
        jacob2 = np.cos(np.pi*np.mean(latLon[:,0])/180.)**2

    # Make every pairwise comparison
    nInclude = nSamps if useAll else min(500,nSamps)
    if verbose > 1:
        print('Running getRelation()')
    for i in range( 0,nInclude ):
        for j in range( i,nInclude ):
            # option 0: Use L1 norm,  1: Use L2 norm,  2: Use POTN Poisson prob
            relation[i,j] = relateBarcode(barcode[i],barcode[j],option=option)
            if gps:
                dr[i,j] = np.sqrt( (latLon[i,0] - latLon[j,0])**2 + (latLon[i,1] - latLon[j,1])**2*jacob2 )
            if getTime > 0:
                dt[i,j] = sDates[j] - sDates[i]
            # Make this a matrix manipulation??
            if fillLowerLeft:
                relation[j,i] = relation[i,j]
                if gps:
                    dr[j,i] = dr[i,j]
                if getTime > 0:
                    dt[j,i] = -dt[i,j]
        if verbose > 1:
            if (i % int(nInclude*0.1))==0:
                print(':', end='', flush=True)
            if (i % int(nInclude*0.01))==0:
                print('.', end='', flush=True)
    if verbose > 1:
        print('')
            
    # Normalize L2 distance, rescale time to days
    if option==1:
        relation = relation/np.sqrt(24.)
    #elif option==2:
    #    None
    #else:
    #    relation = relation/24.
    if getTime:
         dt = dt*(maxDate-minDate) #/60./60./24.
         if maxDate==minDate:
             #dt[:] = 0.
             dt = np.zeros(dt.shape)
    
    return relation, dr, dt




'''
CountBits copied from Adam Zalcman
https://stackoverflow.com/questions/9829578/fast-way-of-counting-non-zero-bits-in-positive-integer
'''
def CountBits(n0):
    n = n0.astype('uint64')
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
                                         # This last & isn't strictly necessary.
    return n


def bitwise_match(x,y):
    return np.invert(np.bitwise_xor(x,y))


def convertToBin(barcode):
    return np.sum(base4array * (barcode-1))


'''
Convert barcode row to a base 4 integer
'''
def convertToBinAll(barcode):
    if len(barcode.shape)!=2:
        print('Warning: Only one barcode - invalid shape.')
    nSamps = barcode.shape[0]
    base4repeat = np.repeat( np.reshape(base4array,[1,nSNPs]).astype('uint64'),
                             nSamps, axis=0).astype('uint64')
    return np.sum(base4repeat * (barcode.astype('uint64')-1), axis=1).astype('uint64')


def convertToMatches(binDiff):
    N = binDiff.shape[0]
    array1 = np.repeat( np.repeat([[binTemplate1]],N,axis=1).astype('uint64'), N,axis=0)
    array2 = np.repeat( np.repeat([[binTemplate2]],N,axis=1).astype('uint64'), N,axis=0)
    # Each SNP is 2 bits so take every other bit,
    # divide by 2 to shift one decimal and compare with other half of bits.
    # This lets me look for matches for every 2 bits.
    matches = np.bitwise_and( ( np.bitwise_and(binDiff,array1) ).astype('uint64'),
                              ( np.bitwise_and(binDiff,array2)/2 ).astype('uint64') )
    matches = CountBits(matches)
    return matches


def relateAll(matches, option=1):
    if option==1:    # L2 norm
        relation = np.sqrt( matches )
    elif option==2:  # Poisson point mutation model
        m = nSNPs - matches
        r = 1        # Rate (pt mutation per gen/day) - eventually feed in as parameter
        deltat = 1   # Time between observations - feed in with data
        relation = np.power(r*deltat,m)*np.exp(-(r*delta))/scipy.special.gamma(m+1)
    else:            # L1 norm
        relation = matches

    return relation



def getRelation(barcodeDF, fillLowerLeft=1, useAll=0, option=1, gps=1, getTime=1,
                verbose=1, timeOption=2):

    t0 = time.time()

    nSamps = len(barcodeDF)

    # Initialize matrix for storing relation coefficients
    relation = np.zeros([nSamps,nSamps])
    dr = np.zeros([nSamps,nSamps])
    dt = np.zeros([nSamps,nSamps])

    # Save df data to numpy arrays for faster access
    barcode = getBarcode(barcodeDF)
    latLon = barcodeDF[['Lat','Lon']].values
    dates = getDatesOrYear(barcodeDF, option=timeOption)
    
    # Maybe move this below for clarity?
    if np.sum(np.isnan(dates)) == nSamps:
        getTime = 0
    if getTime:
        minDate = np.nanmin(dates)
        maxDate = np.nanmax(dates)
        sDates = (dates-minDate)/(maxDate-minDate) #scaled Dates

    # Assume geographic locus is small enough that we just need one transformation
    if gps:
        jacob2 = np.cos(np.pi*np.mean(latLon[:,0])/180.)**2

    # Make every pairwise comparison
    nInclude = nSamps if useAll else min(500,nSamps)
    if verbose > 1:
        print('Running getRelation()')

    # Encode barcode as binary integers
    # Count number of matches by using XOR
    # Get distance from matches
    barcodebin = convertToBinAll(barcode)
    binxx,binyy = np.meshgrid(barcodebin,barcodebin)
    binDiff = bitwise_match(binxx,binyy)  ### use just XOR for dissimilarity!
    binDiff = convertToMatches(binDiff)
    # option 0: Use L1 norm,  1: Use L2 norm,  2: Use POTN Poisson prob
    relation = relateAll(binDiff, option=option)
    ### print(barcode,'\n',barcodebin,'\n',binxx,'\n',binDiff,'\n',relation)

    # latitude on 0 index
    # longitude on 1 index
    if gps:
        latxx,latyy = np.meshgrid(latLon[:,0],latLon[:,0])
        lonxx,lonyy = np.meshgrid(latLon[:,1],latLon[:,1])
        dr = np.sqrt( (latxx - latyy)**2 + (lonxx - lonyy)**2*jacob2 )

    # Get time deltas
    # Be careful with order here. Apparently y is the 0th index
    if getTime:
        txx, tyy = np.meshgrid(sDates,sDates)
        dt = txx - tyy
    
    # Count each pair only once if desired
    if fillLowerLeft==0:
        rangefill = np.arange(nSamps)
        fillxx,fillyy = np.meshgrid(rangefill,rangefill)
        fillTopRight = fillyy<=fillxx
        dt = dt*fillTopRight
        dr = dr*fillTopRight
        relation = relation*fillTopRight
        
    # Normalize L2 distance, rescale time to days
    if option==1:
        relation = relation/np.sqrt(24.)
    #elif option==2:
    #    None
    #else:
    #    relation = relation/24.
    if getTime:
        dt = dt*(maxDate-minDate) #/60./60./24.

    if verbose > 1:
        print('Time elapsed:',time.time()-t0)
    
    return relation, dr, dt





'''
Compute genetic, geographic, and temporal distances for all pairs of barcodes
Inputs:
  dfZ - converted dataframe for Zambia
  dfS - ditto for Senegal (focused on Thies)
  dfT - ditto for Thies, pruned
Outputs:
  relationZ - relation matrix (i.e. table of barcode metric distances) of Zambia data
  dijZ - geographic distance matrix for Zambia
  dtZ - delta_t matrix for Zambia
  relationS - relation matrix for Senegal
  dijS - geo. distance matrix for Senegal
  dtS - delta_t matrix for Senegal
  relationT - relation matrix for Thies
  dtT - delta_t matrix for Thies
'''
def getRelations(dfZ,dfS,dfT,
                 verbose=0, fillLowerLeft=0):

    t0 = time.time()

    '''Do Zambia data'''
    relationZ, dijZ, dtZ = getRelation(dfZ,fillLowerLeft=0, option=1)
    
    if verbose >= 1:
        print('Time elapsed for Zambia data:', time.time() - t0)

    '''Repeat for Senegal data (Spatial processed)'''
    relationS, dijS, dtS = getRelation(dfS,fillLowerLeft, useAll=1, option=1)
    
    if verbose>=1:
        print('Time elapsed for Senegal Data:', time.time() - t0)

    '''Repeat for Senegal data (just Thies barcodes)'''

    relationT, dijT, dtT = getRelation(dfT,fillLowerLeft, useAll=1, option=0, gps=0, getTime=3)

    if verbose>=1:
        print('Time elapsed for Thies Data:', time.time() - t0)
        print('')

    return relationZ, dijZ, dtZ, relationS, dijS, dtS, relationT, dtT





'''
Function for trimming graphs
I.e. erasing edges that don't represent direct links between barcodes
Might also be able to include N/S filling funcionality

Probably better to pass in dataframe for node properties
since this is multidimensional (lat,lon,time,etc)

Edgeweights can strictly be barcode similarity, and thus passed in
using networkx framework

If we eventually want priors on barcode position correlations and frequencies
we'll have to do something else about the edges

Inputs:
  relationM - relation matrix to be trimmed (numpy array)
  dates - dates to be used to determine direction of ancestry (numpy array)
Outputs:
  outM - trimmed relation matrix
'''

def trimGraph(relationM, dates): #G,nodeweights=[],edgeweights=[]):
    
    t0 = time.time()

    nSamps = relationM.shape[0]
    if nSamps != relationM.shape[1]:
        print('Relation matrix is not square. Aborting...')
        return 0
    if nSamps != len(dates):
        print('Number of dates do not match relation matrix. Aborting...')
        return 0

    # Copy relation matrix to use for output
    outM = relationM.copy()
    if 1:
        outM = np.maximum(outM,outM.transpose())
        
    # Sort matrix by dates to make ordered comparions simpler
    isort = np.argsort(dates)
    outM = outM[isort,:][:,isort]
    if np.sum( np.diag(outM)==1 ) != nSamps:
        warnings.warn('Diagonals are not 1. Matrix error', RuntimeWarning)
                     
    for i in range(1,nSamps):
        for j in range(i,nSamps):
            for k in range(j,nSamps):
                if (outM[i,k]<outM[i,j]) and (outM[i,k]<outM[j,k]):
                    outM[i,k] = 0.
                    outM[k,i] = 0.
                elif (outM[j,k]<outM[i,j]) and (outM[j,k]<outM[i,k]):
                    outM[j,k] = 0.
                    outM[k,j] = 0.
                    
    # Revert matrix to original order
    outM[isort,:] = outM
    outM[:,isort] = outM
    
    print('Time elapsed:', time.time()-t0)
    
    # Return trimmed relation matrix
    return outM




'''
Sort clone clusters from largest to smallest cluster
Inputs:
  barcodes - numpy array of barcodes (current version does not use this)
  relationM - numpy square matrix containing all pairwise values according to similarity metric
  option - (int) chooses between two options for the first output variable:
    0 - list of indices that sorts original dataframe or array (keeps all entries) or
    1 - list of indices that returns only one entry from each cluster
    Use the latter option when looping to do analyses on individual clusters
    Use former when needing to do aggregate cluster on full population but grouped by clones
Outputs:
  1 - numpy array of indices that sorts barcodes from largest to smallest cluster
  2 - numpy array of the number of instances of each clone
'''

def cloneSort(barcodes, relationM, option=0, gethaplo=0, fullMatch = 24.):

    # "barcodes" is not currently used
    try:
        if relationM.shape[0] != barcodes.shape[0]:
            warnings.warn('Array shapes do not match', RuntimeWarning)
            print('ARRAY SHAPES DO NOT MATCH')
            return 0, 0
    except TypeError:
        print('Inputs should both be numpy arrays')

    ###fullMatch = 24.
    
    # Find number of clones each barcode has
    numClones = np.sum(relationM==fullMatch, axis=1)

    # Sort first by clone sum
    indices = np.flip( np.argsort(numClones), 0 )
    relationSort = relationM[indices,:][:,indices]

    # Combine clone sum with relation matrix
    # Maybe not needed
    #sumAndCodes = np.append(relationM[indices,:][:,indices],
    #                        numClones[indices].reshape([len(numClones),1]),
    #                        axis=1)

    # TODO: test if rebuilding array is faster than lookup
    # Sort next by match
    # i will move along SORTED index
    # thus indexList needs to be converted back to indexing of original input before returning
    checked = np.zeros(len(numClones)) # list of barcodes that have been checked
    indexList = []   # list of indices of elements from original array
    countList = []   # list of how many clones each entry has
    haploList = []   # list of newly assigned haploype IDs for each unique strain
    hapcount = 1
    i = 0
    while np.sum(checked==0) > 0:
        w = np.where(relationSort[i,:]==fullMatch)
        if len(w[0])==0:
            warnings.warn('Entry/row without valid data, possibly NaNs', RuntimeWarning)
            indexList += [i]
            countList += [1]
            haploList += [hapcount]
            hapcount += 1
            w = i
        elif option==0:
            indexList += w[0].tolist()
            countList += [len(w[0])]*len(w[0])
            haploList += [hapcount]*len(w[0])
            hapcount += 1
        else:
            indexList += [w[0][0]]
            countList += [len(w[0])]
            haploList += [hapcount]
            hapcount += 1
        checked[w] = 1
        unchecked = np.where(checked==0)[0]
        if len(unchecked) > 0:
            i = unchecked[0]
        else:
            break

    if gethaplo==1:
        return indices[ np.array(indexList) ], np.array(countList), np.array(haploList)

    return indices[ np.array(indexList) ], np.array(countList)





def dummy():

    nan_count = 0
    if nan_count:
        warnings.warn('Some warning', RuntimeWarning)
    inf_count = 0
    if inf_count:
        warnings.warn('There are %d Inf values in strain ID %d' % (inf_count,clusterID), RuntimeWarning)
        
    return 1



if __name__ == '__main__':
    print('Hello')
