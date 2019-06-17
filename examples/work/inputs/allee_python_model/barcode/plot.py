import os
import warnings
import time

import json
import argparse

import numpy as np
import pandas
from matplotlib import pyplot as plt

import barcode.barcode as bc
import barcode.model as bm
import barcode.data as bdata
import barcode.evaluate as beval
import barcode.modelfit as bmf



'''
Scripts for gathering and plotting simulation results
'''


verbose = 1


nYrs = len(beval.evalYears)
baseErr = np.zeros(0)
#beval.setBaseErr()

__truthMean = []
__truthVar = []



##def setBaseErr():
##    global baseErr
##    baseErr = np.zeros(0)
##    baseErr = np.append(baseErr,np.ones(nYrs)*.04)
##    baseErr = np.append(baseErr,np.ones(nYrs)*.04)
##    baseErr = np.append(baseErr,np.ones(nYrs)*1.)
##    baseErr = np.append(baseErr,np.ones(nYrs)*2.)
##    baseErr = np.append(baseErr,np.ones(4)*1.)
##    baseErr = np.append(baseErr,7.)
##    baseErr = np.append(baseErr,6.)
##    return 1
    
def truthStats():
    df = bmf.getRealData()
    truthVar = bmf.setMeansVariances(df)
    truthMean = bmf.__meanstats__
    return truthMean, truthVar
    
def reEvaluate(outputDF):
    
    global baseErr, __truthMean, __truthVar
    
    # Get error from model
    baseErr = beval.baseErr
    
    # Get truth from real data
    if (len(__truthMean) < 1) or (len(__truthVar) < 1):
        __truthMean, __truthVar = truthStats()
    
    nSamps = len(outputDF)
    logLikelihood = np.zeros(nSamps)
    
    for i in range(nSamps):
        simGroup = retrieveStatArray(outputDF,i)
        #simGroup = np.array( statsData[i] )
        
        if len(simGroup.shape) == 2:
            statErr = np.var(simGroup,axis=0)
            totalErr = baseErr + statErr*0.01 + __truthVar
            nSims = simGroup.shape[0]
            for j in range(nSims):
                logLikelihood[i] += -np.sum( (simGroup[j,:]-__truthMean)**2/totalErr )
        else:
            logLikelihood[i] = np.NaN
        
    newDF = outputDF.copy()
    newDF['logLArray'] = logLikelihood
    
    return newDF




def plotSlice(outputDF, i):

    ldata = outputDF['logLArray'].values.astype(float)

    imgarray = np.reshape(ldata[(i*100):((i+1)*100)]*.1,[10,10])
    print(imgarray)
    wNan = np.where(imgarray != imgarray)
    imgarray[wNan] = -np.inf

    fig = plt.figure(figsize=(6, 5))
    ax1 = fig.add_subplot(111)

    #plt.imshow(imgarray)
    im = ax1.imshow(np.exp(imgarray*.02), 
                    aspect = 'auto', cmap = 'bone', interpolation = 'none', origin = 'lowest',
                    extent=(.3,3.3,.3,3.3), vmin=0,vmax=0.7)
    cb = plt.colorbar(im, label = 'scaled log likelihood')
    ax1.set_xlabel('R_0 start')
    ax1.set_ylabel('R_0 middle')
    ax1.set_title('R_0 end = '+str(i*.3+.3))

    #plt.colorbar()
    plt.show()

    print(ldata[(i*100):((i+1)*100)]*.1)

    return 1




def retrieveStatArray(outputDF, index):
    return np.array( outputDF['statArray'].values[index] )

    
def showStats(outputDF, i, j=-1, k=-1, variance=1):

    np.set_printoptions(precision=4)
    #sdata = outputDF['statArray'].values
    #print(sdata.shape)
    #j=7
    #k=4
    if (j >= 0) and (k >= 0):
        Rindex = i*100+j*10+k
    else:
        Rindex = i

    print('Log Likelihood:', outputDF.loc[Rindex,'logLArray'], '\n')

    simGroupData = retrieveStatArray(outputDF,Rindex) #np.array(sdata[Rindex])
    if verbose > 2:
        print(simGroupData, '\n')

    np.set_printoptions(precision=2)

    stats = np.mean(simGroupData,axis=0)
    beval.printStats(stats)

    staterr = np.var(simGroupData,axis=0)
    if variance == 1:
        print('Variances:')
        beval.printStats(staterr)
    else:
        print('Standard Deviations:')        
        beval.printStats(np.sqrt(staterr))

    np.set_printoptions(precision=4)

    return 1





        
