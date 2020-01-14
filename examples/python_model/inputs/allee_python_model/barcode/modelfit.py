import warnings
import time
from datetime import datetime

import numpy as np
import pandas
import scipy

import barcode.data as bdata
import barcode.model as bm
import barcode.evaluate as beval
import barcode.barcode as bc



'''
Fit model to Senegal/Zambia data
'''


''' Private run parameters '''

verbose = 1

tStart = 732600-450 #733694
tEnd = 736385  #735300-200   #736637
initStrainNumber = 60 #20
agentbased = 1
numR0=4

allyears = 0
    
nSimSteps = 850

nSlices = 20

nSamps = 5
nSims = 20
nParams = 7

eventsThresh = 1800.

__grid__ = np.zeros(0)
__variances__ = 0
__meanstats__ = 0
__medianstats__ = 0

__settings = {}


'''
Set variances by bootstrapping Senegal barcodes
'''
def setMeansVariances(dfP):

    # Get real data from input files
    #dfPNAS,df2,df3 = bdata.readPNAS()
    #dfZambia,dfSenegal,dfThies = bdata.readData()
    #dfZ, dfS, dfT = bdata.convertData(dfZambia,dfSenegal,dfThies,verbose=0)
    #dfZ, dfS, dfT, dfP = bdata.convertData(dfZambia,dfSenegal,dfThies,
    #                                  dfPNAS=dfPNAS, verbose=0)
    #dfP = bdata.cutData(dfP, cut=[0,0], yearbound=[2005,2013])
    
    nEntries = len(dfP)
    global nSlices
    samples = np.zeros([nSlices,len(beval.getStats(dfP))])

    # Get nSlices different subsamplings of data in order to
    # do bootstrap estimates of diversity statistics
    for i in range(nSlices):
        indices = np.random.permutation(nEntries)[:int(nEntries*.9)]
        bHistorySamp = dfP.loc[indices]
        samples[i,:] = beval.getStats(bHistorySamp) #, yearOption=2) # yearOption=2 for new Senegal data
        
    global __variances__, __meanstats__, __medianstats__
    __variances__ = np.var(samples,axis=0)
    __variances__ = __variances__ + np.min(__variances__[np.where(__variances__>0.)])*.01
    __meanstats__ = np.mean(samples,axis=0)
    
    return __variances__



def adjustErrors():
    global __variances__
    nYrs = len(beval.evalYears)
    __variances__[nYrs:2*nYrs] = 4*__variances__[nYrs:2*nYrs]  ### Loosen errors since this is directly covariate with 0:8
    __variances__[2*nYrs:3*nYrs] = __variances__[2*nYrs:3*nYrs]+0.3  ### Add poisson term for zero processes
    __variances__[3*nYrs:(3*nYrs+2)] += np.sqrt(__variances__[3*nYrs:(3*nYrs+2)])*0.3  ### Poisson counting error (downweighted)
    return 1

  


'''
Function to get log likelihood of a single point phi in parameter space
Loops over nSims different stochastic realizations of phi 
'''
def loglikelihood(phi, truthStats, variances, seed=[]):
    
    # Set seed
    if len(seed) == 0:
        seed = (np.random.random(1)*1000000).astype('int64')
    else:
        seed = seed[0]
        
    np.random.seed(seed)
    
    # Set run params
    bm.verbose=2
    bm.initStrainNumber = initStrainNumber
    bm.tEnd = tEnd

    global agentbased, numR0
    if agentbased:
        # Set model params (phi)
        # (for generic method)
        bm.dailyNew = phi[0]    # Avg. no. of new parasites to generate each day
        bm.dailyDeaths = phi[1] # Avg. no. of expiring strains
        bm.dateStep = 8         # make this a model param?
        bm.importRate = phi[5]
        bm.importNum = phi[6]
        #
        # (for agent-based method)
        bm.offspringRate = phi[2]     # Fraction of parasites that produce offspring
        bm.offspringReproNum = phi[3] # Reproductive number of parasites that produce offspring
        bm.repeatRange = 32.          # make this a model param?
    elif numR0==3:
        # Set model params (phi)
        # (for wallclock method)
        bm.__rho__ = phi[3]
        bm.__R0 = [phi[0],phi[1],phi[2]]
        bm.dateStep = 4
        bm.__deathRatePerDay = phi[4]
        bm.importRate = phi[5]
        bm.importNum = phi[6]
        #
        #bm.__R0__ = 1.8           # max reproductive number (obsolete)
        #bm.__offspringRate = 0.2  # Fraction of parasites that produce offspring
        #bm.offspringReproNum = 5. # Reproductive number of parasites that produce offspring
        #bm.__scaleThresh = 0.5
        #bm.repeatRange = 32.
    else:
        # Params for four R_0 vals
        bm.__rho__ = phi[4]
        bm.__R0 = [phi[0],phi[1],phi[2],phi[3]]
        bm.dateStep = 4
        bm.__deathRatePerDay = phi[5]
        bm.importRate = phi[6]
        bm.importNum = phi[7]

    barcodeHistories = []
    stats = np.zeros([nSims,len(variances)])

    # Run nSims different stochastic realizations of simulation
    # Evaluate diversity metrics for each run
    global eventsThresh
    for i in range(nSims):
        np.random.seed(seed+i)
        strainsEvolved, strains, settings = bm.runSim(nsteps=nSimSteps, agentbased=agentbased)
        barcodeHistories += [strainsEvolved]
        
        nEvents = len(strainsEvolved)
        if (nEvents > (eventsThresh+200)) and not agentbased:
            strainsEvolved = strainsEvolved.loc[np.random.random(nEvents) < (eventsThresh/nEvents)]
        stats[i,:] = beval.getStats(strainsEvolved)

    # Get mean and variance over the different stochastic runs in order to fit to truth (real Senegal data)
    statsmean = np.mean(stats,axis=0)
    statsvar = np.var(stats,axis=0)
    logL = -np.sum((statsmean-truthStats)**2/(variances+statsvar) )
                # assume no covariance for now
                # this is clearly wrong for uniques and repeated

    return logL, stats, barcodeHistories




def sampler():
    
    phi = getParams()
        
    return None



'''
Set up grid for param search
Return first row/entry of grid
'''
def initParams():
    
    global __grid__ 
    global nSamps, agentbased, nParams, numR0
    if numR0==4:
        nParams = 8
    else:
        nParams = 7
    
    N = 2
    nSamps = N**2
    __grid__ = np.zeros([nSamps,nParams])
    
    if agentbased:
        rateVals = np.reshape(np.repeat( np.reshape(np.arange(N)*2+1, [1,N]), N, axis=0),
                              [nSamps])
        __grid__[:,0] = rateVals
        __grid__[:,1] = rateVals
        __grid__[:,2] = 0.2
        __grid__[:,3] = 5.
        __grid__[:,4] = np.repeat(np.arange(N)*0.05, N)
        __grid__[:,5] = 1.
    elif numR0==3:
        rateVals = np.reshape(np.repeat( np.reshape(np.arange(N)*0.2+1.5, [1,N]), N, axis=0),
                              [nSamps])
        __grid__[:,0] = rateVals
        __grid__[:,1] = np.repeat(np.arange(N)*0.2+1.5, N)
        __grid__[:,2] = 1.8
        __grid__[:,3] = 0.01 #0.02
        __grid__[:,4] = 0.02 #np.repeat(np.arange(N)*0.05, N)
        __grid__[:,5] = 0.04
        __grid__[:,6] = 1.
    else:
        rateVals = np.reshape(np.repeat( np.reshape(np.arange(N)*0.2+1.5, [1,N]), N, axis=0),
                              [nSamps])
        __grid__[:,0] = rateVals
        __grid__[:,1] = np.repeat(np.arange(N)*0.2+1.5, N)
        __grid__[:,2] = 2.4
        __grid__[:,3] = 1.8
        __grid__[:,4] = 0.01 #0.02
        __grid__[:,5] = 0.02 #np.repeat(np.arange(N)*0.05, N)
        __grid__[:,6] = 0.04
        __grid__[:,7] = 1.

        
    return __grid__[0,:]



def getVariances():
    return __variances__




def setSettings():
    global verbose, tStart, tEnd, initStrainNumber, \
           agentbased, nSimSteps, nSamps, nSims, nParams, __variances__
    global __settings
    if type(__variances__) is np.ndarray:
        variances = __variances__.tolist()
    else:
        variances = []
    __settings = {'verbose':verbose,
                  'tstart':tStart,
                  'tend':tEnd,
                  'initStrainNumber':initStrainNumber,
                  'agentbased':agentbased,
                  'nSimSteps':nSimSteps,
                  'nSamps':nSamps,
                  'nSims':nSims,
                  'nParams':nParams,
                  'variances':variances}
    return 1


def saveSettings(fname=''):
    if fname=='':
        fname = 'settings'+str(time.time())+'.json'
    global __settings
    bdata.saveJson(fname,__settings)
    return 1



'''
Function to propose new sample
For now just return next entry in grid
Might seem redundant but this structure will be needed for 
  more complex sampling schemes
'''
def sampleStep(sample, i):
    return __grid__[(i+1),:]



def getRealData():
    dfPNAS,df2,df3 = bdata.readPNAS()
    dfZambia,dfSenegal,dfThies = bdata.readData()
    dfZ, dfS, dfT, dfP = bdata.convertData(dfZambia,dfSenegal,dfThies,
                                      dfPNAS=dfPNAS, verbose=0)
    global allyears
    if allyears==1:
        dfP = bdata.cutData(dfS, cut=[0,0], yearbound=[2005,2017])
    else:
        dfP = bdata.cutData(dfP, cut=[0,0], yearbound=[2005,2013])
    return dfP



def setModel(option=1):
    global allyears, tStart, tEnd, eventsThresh
    if option>=2:
        print('Using extended years (2006 to 2016)')
        allyears = 1
        beval.setYears(2006,2016+1)
        tStart = 732150
        tEnd = 736385
        bm.tStart = 732150
        bm.tEnd = 736385
        bm.div1 = 0.104 #0.15
        bm.div2 = 0.348 #0.5
        bm.div3 = 0.522 #0.75
        bm.div4 = 0.70
        if option >= 3:
            bm.extendYears = 1
        else:
            bm.extendYears = 0
        eventsThresh = 1000
        historyMax = 300000
    elif option==1:
        print('Using original years (2006 to 2013)')
        allyears = 0
        beval.setYears(2006,2013+1)
        tStart = 732150
        tEnd = 735100
        bm.tStart = 732150
        bm.tEnd = 735100
        bm.div1 = 0.15
        bm.div2 = 0.5
        bm.div3 = 0.75
        bm.div4 = 0.99
        bm.extendYears = 0
        eventsThresh = 1800
        historyMax = 200000
    else:
        print('Invalid option')
    return 1
        
        


def fitModel():
    
    #df1,df2,df3 = bdata.readPNAS()
    #df1 = bdata.convertData ###
    
    bc.verbose=0
    bm.verbose=0
    beval.verbose=0
    
    # Stand in example until above is coded up
    print('Loading data...')
    dfP = getRealData()
     
    print('Initializing run parameters...')
    global __grid__, nSamps
    if len(__grid__) == 0:
        sample0 = initParams()
    else:
        sample0 = __grid__[0,:]
    samples = np.zeros([nSamps,len(sample0)])
    samples[0,:] = sample0 ### change this?
    
    #truthStats = beval.getStats(dfP)
    
    setMeansVariances(dfP)
    adjustErrors()
    variances = getVariances() 
    print('Variances:', variances)

    global __meanstats__
    truthStats = __meanstats__
    print('Means:', __meanstats__)
    
    statArray = np.zeros([nSamps,nSims,len(variances)])
    logLArray = np.zeros(nSamps)

    # Run one set of stochastics sims for every sample specified by grid
    # both __grid__ and nSamps are set by barcode.scripts
    print('')
    print('Running samples...')
    print('')
    for i in range(nSamps):
        print('Current sample:',samples[i,:])
        print('')
        logLArray[i], statArray[i,:,:], _ = loglikelihood(samples[i,:], truthStats, variances, seed=[1])
        if i < (nSamps-1):
            samples[i+1,:] = sampleStep(samples[i,:],i)
    
        if verbose > 1:
            if int(i % ceil(nSamps*0.1))==0:
                print(':', end='', flush=True)
            if int(i % ceil(nSamps*0.01))==0:
                print('.', end='', flush=True)
    if verbose > 1:
        print('')

    return samples, logLArray, statArray





if __name__ == '__main__':
    print('Starting fit')
    samples, logArray, statArray = fitModel()
    current_path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(current_path,'..','output','test.npy')
    #file = 'test.npy'
    np.save(file,samples)
    print('End of run')
