import os
import warnings
import time

import numpy as np
import pandas
import scipy

import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

import barcode.barcode as bc
import barcode.model as bm


'''
Bunch of unit tests

This is dangerous because unit tests will only be valid for
the version of the software they were created for. Believe these
functions only as far as they are recent.
'''



'''
Check whether the correct columns were pulled from a table to be
converted into a barcode array
SETTING verbose to < 0 IS DANGEROUS BECAUSE ERRORS MAY NOT BE CLEAR
'''
def validBarcode(barcode, verbose=1):

    btype = None
    
    try:
        dims = barcode.shape
        nTotal = dims[0]*dims[1]
        nValid1 = np.sum( np.isin(barcode,[1,2,3,4]) )          
        nValid2 = np.sum( np.isin(barcode,['C','G','A','T','X','N']) )      
        
        if nValid1 == nTotal:
            if verbose >= 2:
                print('Barcode is in 1,2,3,4 format')
            btype = 1
            return btype
        
        elif nValid2 == nTotal:
            if verbose >= 2:
                print('Barcode is in C,G,A,T,X,N format')
            btype = 2
            return btype
        
        else:
            if verbose >= 1:
                warnings.warn('Barcode is in unknown format or has invalid entries',
                              RuntimeWarning)

            if nValid1 > nTotal*0.5:
                if verbose >= 1:
                    print('Barcode is probably in 1,2,3,4 format')
                    print(nValid1,'valid entries out of',nTotal,'total.')
                btype = 1
                
            elif nValid2 > nTotal*0.5:
                if verbose >= 1:
                    print('Barcode is probably in C,G,A,T,X,N format')
                    print(nValid2,'valid entries out of',nTotal,'total.')
                btype = 2

        try:
            print('# of numerical elements:',np.sum(barcode > 0))
        except TypeError:
            print('Input has non-numerical elements')
            
    except TypeError:
        if verbose >= 0:
            print('Input is either not a numpy array or incorrectly formatted')

    finally:
        if verbose >= 0:
            print('')

    return btype





def testRelation():

    np.random.seed(11)
    bm.verbose=2
    bm.initStrainNumber = 20
    bm.dateStep = 8
    bm.repeatRange = 32.
    bm.tEnd = 737700
    strainsEvolved, strains, settings = bm.runSim(nsteps=1600, agentbased=0)
    
    if 1:
        t0=time.time()
        r1,x1,y1 = bc.getRelation(strainsEvolved[:1000],option=1,fillLowerLeft=1,useAll=1, verbose=2)
        print(time.time()-t0)

        t0=time.time()
        r2,x2,y2 = bc.getRelation0(strainsEvolved[:1000],option=1,fillLowerLeft=1,useAll=1, verbose=2)
        print(time.time()-t0)
    
    print('dij:')
    print(np.sum(x1==x2),np.sum(y1==y2))
    print(x1.shape[0]*x1.shape[1],y1.shape[0]*y1.shape[1])
    print('barcode:')
    print(np.sum(r1==r2),r1.shape[0]*r1.shape[1],r1.shape[0]*r1.shape[1] - np.sum(r1==r2))
    
    wR = np.where(r1!=r2)
    wX = np.where(x1==x2)
    print('avg diff:',np.average(np.abs(x1[wX]-x2[wX])))
    wX = np.where(x1!=x2)
    print('avg diff:',np.average(np.abs(x1[wX]-x2[wX])))
    print('dij:')
    print(wX)
    print(x1[wX],'\n',x2[wX])
    print('barcode:')
    print(wR)
    print(r1[wR],'\n',r2[wR])

    return 1
