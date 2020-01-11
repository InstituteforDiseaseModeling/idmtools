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


# Borrowing functions from E Wenger's genepi
# github.com/InstituteforDiseaseModeling/genepi/blob/master/genepi/meiosis.py
import genepi.genome as gn
gn_model = gn.GenomeModel.initialize_from('barcode')

from genepi.meiosis import meiosis_genomes
def one_meiotic_product(parent1, parent2):
    """ Return one meiotic product of two specified parent genomes """
    return meiosis_genomes(np.stack([parent1, parent2]), N=1)[0]




'''
Constants and reference variables
'''
# reftypeTimestamp = type(np.datetime64('2005-02-25'))




'''
Turn this into a class?
Make a barcode class object? (to update and replace current barcode package)
'''


''' Private variables '''

verbose = 1

numSNPs = 24 # **** I should set this a better way

# runSIm():
tStart = 732150 #733694
tEnd = 736385 #735100 #736637

# initStrain():
initStrainNumber = 60 #20

# dummyStrains():
dummyDateStep = 40
nStrainsDummy = 50

# importation():
__importRatePerDay = 0.01
importRate = 0.04
importNum = 1.

# clonal_prop()
probAll = 0.2
probPerSite = 0.5

# simOffspring():
repeatRange = 16.

__R0__ = 1.5     # max reproductive number
__rho__ = 0.18   # seasonal modulation coeff.
__R0 = [1.9,1.6,1.8,1.9]
div1 = 0.15
div2 = 0.5
div3 = 0.75
div4 = .99
extendYears = 0

__nHumans = 2000.

# evolveBarcode():
__offspringRate = 0.2  # Fraction of parasites that produce offspring
offspringReproNum = 5. # Reproductive number of parasites that produce offspring
__scaleThresh = 0.5    # Fraction of parasites that infect in same season

# timeStepReservoir():
__deathRate = 0.015 # Fraction of reservoir that dies off every time step
__deathRatePerDay = 0.022 # Fraction of reservoir that dies off every time step

# timeStep():
dailyNew = 3.    # Avg. no. of new parasites to generate each day
dailyDeaths = 3. # Avg. no. of expiring strains
dateStep = 4     # was 1

reservoirMax = 10000
historyMax = 300000

__dailyNewList = []  ###
__resSize = []
__dates = []




def getMeanCOI():
    global __nHumans, __resSize
    return float(__resSize[-1])/__nHumans


def defaultColumns():
    return ['ID','Date','Barcode','Lat','Lon','Complexity','Year','ParentA', 'ParentB']


def genTimes(nStrain, tRange=1):
    times = np.random.random(nStrain)*tRange + tStart
    return times

def genCoords(nStrain, senegal=1):
    if senegal:
        lonR = [-16.96,-16.89]
        latR = [14.74,14.84]
    else:
        lonR = [-16.96,-16.89]
        latR = [14.74,14.84]
    coords = np.random.random([nStrain,2])
    coords[:,0] = coords[:,0]*(lonR[1]-lonR[0])+lonR[0]
    coords[:,1] = coords[:,1]*(latR[1]-latR[0])+latR[0]
    return coords

def genIDs(nStrain):
    IDs = np.arange(nStrain)
    return IDs


def genBarcodes(nStrain, timestamps=[], positions=[], nSNPs=24):

    rawRand = np.random.random([nStrain,nSNPs])
    segment = np.random.random(nStrain)
    barcodes = np.zeros([nStrain,nSNPs])
    
    splitLine = 0.5
    wGood = np.where(segment >= splitLine)
    wBad = np.where(segment < splitLine)
    barcodes[wGood] = (rawRand[wGood] < 0.6)*1. + (rawRand[wGood] >=0.6)*2.
    barcodes[wBad] = (rawRand[wBad] < 0.4)*1. + ((rawRand[wBad] >=0.4) & (rawRand[wBad] < 0.8))*2. \
        + ((rawRand[wBad] >=0.8) & (rawRand[wBad] < 0.9))*3. + (rawRand[wBad] >= 0.9)*4.

    return barcodes



def toDateTime(df0):
    df0['DateOrdinal'] = df0['Date']
    df0['Date'] = df0.Date.apply(lambda x: datetime.fromordinal(int(x)) if x==x else np.NaN)
    return 1



'''
Initialize reservoir of parasite strains
'''
def initStrains(nStrain = 20, tRange=4, coordRange=[]):

    timestamps = genTimes(nStrain, tRange=tRange)
    positions = genCoords(nStrain)
    
    barcodes = genBarcodes(nStrain, timestamps=[], positions=[])
    
    IDs = genIDs(nStrain)
    
    columns = defaultColumns()
    strains = pandas.DataFrame(index=range(len(IDs)), columns=columns)
    strains['ID'] = IDs
    strains['Date'] = timestamps
    strains['Barcode'] = barcodes.tolist()
    strains['Lat'] = positions[:,0]
    strains['Lon'] = positions[:,1]
    
    if verbose > 2:
        print(strains)
    
    return strains




'''
Generates simple phylogenetic history for unit tests
'''
def dummyStrains(simOutput=1):

    timestamp0 = genTimes(1)
    position0 = genCoords(1)
    barcode0 = genBarcodes(1) * 0. + 1.
    nSNPs = len(barcode0[0])
    IDcounter = 0

    timestamps = np.zeros(0)
    positions = np.zeros([0,2])
    barcodes = np.zeros([0,nSNPs])
    IDs = np.zeros(0)
        
    for i in range(1,nStrainsDummy+1):

        # Convert barcode-length binary string into numpy barcode
        wOnes = np.array( list( ("{0:{fill}"+str(nSNPs)+"b}").format(i, fill='0') ) ).astype('int')

        barcodeTemp = np.ones([i,nSNPs])
        barcodeTemp[:,(wOnes==1)] = 2

        barcodes = np.append( barcodes, barcodeTemp, axis=0 )
        timestamps = np.append( timestamps, np.arange(i)*dummyDateStep + timestamp0 )

        positionTemp = np.zeros([i,2])
        positionTemp[:,0] = np.arange(i) + position0[0,0]
        positionTemp[:,1] = np.arange(i) + position0[0,1]
        positions = np.append( positions, positionTemp, axis=0)
                   
        IDs = np.append( IDs, np.arange(i)+IDcounter)
        IDcounter = IDs[-1]+1

    columns = defaultColumns()
    strains = pandas.DataFrame(index=range(len(IDs)), columns=columns)
    strains['ID'] = IDs
    strains['Date'] = timestamps
    strains['Barcode'] = barcodes.tolist()
    strains['Lat'] = positions[:,0]
    strains['Lon'] = positions[:,1]

    if simOutput:
        toDateTime(strains)
        strains['Year_orig'] = strains['Year']
        strains['Year'] = strains['Date'].dt.year

            
    if verbose > 2:
        print(strains)
        
    return strains
    





'''
These next few will likely become functions in the barcode class

I am currently feeding the entire history of strains to each function
this is very clunky and hard to follow
Would be better to make it a local attribute, but don't want to make a bloated class
'''

def mixed_infection_prob(mean_COI):
     # From edwenger/barcode-model: 1 - P(0) - P(1) = P(>=2)
     return 1 - np.exp(-mean_COI) - mean_COI*np.exp(-mean_COI)

    
def outcross(barcodeA, allBarcodes, option=1):
    i = ( np.random.random(1)*len(allBarcodes) ).astype('int')
    parentB = i
    barcodeB = np.array(allBarcodes[i])[0]

    if option==1:
        barcode = one_meiotic_product(barcodeA, barcodeB)
    else:
        # Get half of SNPs from parent A and the other half from parent B
        mask = (np.random.random(len(barcodeB)) < 0.5).astype('float')
        #print(barcodeA, barcodeB, mask, type(barcodeA), type(barcodeB), type(mask))
        barcode = barcodeA*mask + barcodeB*(1-mask)
    return barcode, parentB



def clonalProp(barcode):
    whereN = (barcode == 4)
    numNs = np.sum(whereN)
    if numNs == 0:
        outcode = barcode
    else:
        # **** fix this to use allele freq.
        #print("usenew")
        global numSNPs,probAll,probPerSite
        newcode = (np.random.random(numSNPs)*2.).astype(int)
        if np.random.random(1) < probAll:
            outcode = barcode*(np.logical_not(whereN)) + newcode*whereN
        else:
            resolve = whereN & (np.random.random(numSNPs) > probPerSite)
            outcode = barcode*(np.logical_not(resolve)) + newcode*resolve
    return outcode


def mutateBarcode(barcode):
    nSNPs = len(barcode)
    flipmask = np.random.random(nSNPs)
    barcode = (((flipmask < 0.1) * (-1)**(((flipmask*100) % 10) < 0.5)
                                 * (2)**(((flipmask*1000) % 10) < 0.5)
                    + barcode) - 1) % 4 + 1
    return barcode
    

# This function is currently agnostic to information about geography and the reservoir
# In the future I will have to update it so it has access to that info
def simOffspring(strain, allStrains, parentB=np.NaN, ordTime=-1):

    #repeatRange = 16. #4.
    
    barcode = np.array(strain['Barcode'])
    
    reproOption = np.random.random(1)
    mean_COI = getMeanCOI()
    mixProb = mixed_infection_prob(mean_COI)
    
    # Mutation
    # Change a SNP with probability 0.1, and if so, +1 or -1
    #   or +2 or -2 with probabilities of 0.25 each
    # This is just a placeholder. MUST CHANGE THIS
    if reproOption < 0.00001:
        barcode = mutateBarcode(barcode)

    # Outcrossing/recombination
    elif reproOption < mixProb:
        barcode, parentB = outcross(barcode, allStrains['Barcode'].values)
        parentB = parentB[0]

    # Clonal propagation
    elif reproOption < 0.95:
        barcode = clonalProp(barcode)        
    
    # Placeholder (outcrossing with co-infecting strain?)
    else:
        None

    barcode = barcode.tolist()  # convert np array back to list for pandas

    # Generate new dates for future infection by offspring
    # Make sure they occur at least one day after current date
    if ordTime<0:
        date = strain['Date']
        if np.random.random(1) < __scaleThresh:
            date = np.random.exponential(scale=15) + date + 1
        else:
            date = np.random.exponential(scale=365) + date + 1
    else:
        date = ordTime
    
    newBarcode = [{'ID':np.NaN, 'Date':date, 'Barcode':barcode, 
                   'Lat':0, 'Lon':0, 'Complexity':np.NaN, 'Year':np.NaN, 
                   'ParentA':np.NaN, 'ParentB':parentB}]
    
    return newBarcode



def mixBarcode(barcode, allStrains):  # prob should call strain infection
    barcodeA = np.array(barcode)
    allBarcodes = allStrains['Barcode'].values
    i = ( np.random.random(1)*len(allBarcodes) ).astype('int')
    parentB = i
    barcodeB = np.array(allBarcodes[i])[0]
    #
    return (barcodeA != barcodeB)*4 + (barcodeA == barcodeB)*barcodeA



def evolveBarcode(strain, allStrains, parentA, time):
    
    # The following two parameters are related to each other by the reproductive number
    #offspringRate = 0.2  # Fraction of parasites that produce offspring
    #offspringReproNum = 5. # Reproductive number of parasites that produce offspring
    
    if np.random.random(1) < __offspringRate:
        #nNew = np.random.poisson(lam=offspringReproNum)
        rho = __rho__
        offspringReproNum = __R0__/__offspringRate * (rho+(1.-rho)*np.cos(np.pi*time/365.)**2) 
        nNew = np.random.poisson(lam=offspringReproNum)
    else:
        nNew = 0
    
    newBarcodes = []
    
    parents = np.zeros([nNew,2])
    parents[:] = np.NaN
    parents[:,0] = parentA
    parentB = np.NaN
    
    for i in range(nNew):
        newBarcode = simOffspring(strain, allStrains, parentB=parentB)
        newBarcode[0]['ParentA'] = parentA
        newBarcodes += newBarcode
        
        # This is redundant. Remove?
        if parentB is not None:
            parents[i,1] = parentB
    
    return newBarcodes, parents







'''
Create importation instances
Output as dict to match evolveBarcode/simOffspring format
'''
def importations(date, justone=0):

    #importRate = 0.1
    #importNum = 1.
    
    if justone:
        nNew = 1
    elif np.random.random(1) < importRate:
        nNew = np.random.poisson(lam=importNum)
    else:
        nNew = 0
        
    imports = initStrains(nStrain=nNew,tRange=1)
    imports['Date'] = date
    
    return imports.to_dict(orient='records')
    

    

#### Starting to have inconsistent nomenclature. Is it strain or barcode?

def timeStepAgent(strains,time, processed):

    # Remember ID value of current last entry so we can add more IDs later
    lastID = strains['ID'].values[-1]

    # Find entries that match current step's timestamp
    # Round down fractional days
    currentEntries = np.where(np.floor(strains['Date'].values) == time)
    currentStrains = strains.loc[currentEntries]
    
    # Keep a list of new barcodes (to be appended to 'strains' later)
    # Each new barcode entry is actually a dict
    #   - will be converted to pandas row upon appending
    newBarcodeList = []
    
    for i in currentStrains['ID'].values:
        if verbose > 5:
            print(i)
        newBarcodes, parents = evolveBarcode( currentStrains.loc[i], strains, i, time)
        newBarcodeList += newBarcodes
        
        # Keep track of parents of each new entry - use this as a tree
        # Currently assigning values to parents in suboptimal way
        parents[:,0] = i

    # For a certain probability, include importation
    newBarcodeList += importations(time)
    
    nNewEntries = len(newBarcodeList)
    
    # Old code for generating bogus barcodes
    #barcode = strains.loc[-1,'Barcode'].values #strains['Barcode'].values[-1]
    #newBarcodeList = [{'Date': time, 'Barcode': barcode, 'Lat': 3., 'Lon': 4.}] * nNewEntries
        
    # Add new offspring/barcodes to list of entries
    # This becomes a history of all strains, making a phylogenetic tree
    if nNewEntries > 0:
        newBarcodeDF = pandas.DataFrame.from_dict(newBarcodeList)
        newBarcodeDF['ID'] = np.arange(lastID,lastID+nNewEntries) + 1
        strains = strains.append(newBarcodeDF[defaultColumns()], ignore_index=True)
    
    # Update time and list of processed entries
    time += 1
    processed[currentEntries] = 1
    processed = np.array(processed.tolist()+[0]*nNewEntries)
    
    return strains, time, processed
    

    

'''
Agent based model for evolution
'''
def timeEvolveAgent(strains, nSteps=2000):
    
    processed = np.zeros(len(strains)) 
    time = tStart  # Start date
    step = 0
    stop = 0
    finalstrains = strains.copy()

    if verbose > 1:
        print('Running timeEvolve()')

    while not stop:

        finalstrains, time, processed = timeStepAgent(finalstrains,time,processed)
        
        # Keep making new parasites until:
        # 1 - we reach the end date
        # 2 - we run out of parasite parents to process, or
        # 3 - we reach the total step limit
        if time >= tEnd:
            stop = 1
            if verbose >=1:
                print('Reached end date.')
        if np.sum(processed) == len(processed):
            stop = 1
            if verbose >=1:
                print('All barcodes processed (all strains died out before end date).')
        if step >= nSteps:
            stop = 1
            if verbose >=1:
                print('Reached max # of steps.')
        
        if verbose > 10:
            print(time)
        
        step += 1

        if verbose > 1:
            if int(step % (nSteps*0.1))==0:
                print(':', end='', flush=True)
            if int(step % (nSteps*0.01))==0:
                print('.', end='', flush=True)
    if verbose > 1:
        print('')
        
    if verbose > 5:
        print(processed,len(processed),len(finalstrains))
        
    return finalstrains






'''
Kill off a fraction of the current strains
'''
def trimReservoir(reservoir, dailyDeaths):
    
    deaths = np.random.poisson(lam=dailyDeaths)
    nEntries = len(reservoir)
    
    # Keep the first (nEntries-deaths) number of random indices
    indices = np.random.permutation(nEntries)[deaths:]
    
    return reservoir.loc[indices].reset_index(drop=True)



'''
Function to advance simulation one time step forward
'''
def timeStep(strains,time, reservoir):

    # Params
    #dailyNew = 3.    # Avg. no. of new parasites to generate each day
    #dailyDeaths = 3. # For now makes sense to make these two equal
                      # In the future this will be seasonal
    #dateStep = 4     # was 1
    
    # Remember ID value of current last entry so we can add more IDs later
    lastID = strains['ID'].values[-1]
    
    # Keep a list of new barcodes (to be appended to 'strains' later)
    # Each new barcode entry is actually a dict
    #   - will be converted to pandas row upon appending
    newBarcodeList = []
    
    # Use seasonal modulation based on PNAS appendix
    rho = __rho__
    dailyNew = dailyDeaths*__R0__*(rho+(1.-rho)*np.cos(np.pi*time/365.)**2)  ### this is new 
    nNew = np.random.poisson(lam=dailyNew)
    global __dailyNewList ###
    __dailyNewList += [nNew]
    
    for i in range(nNew):
        
        # Pick a random parent from the reservoir
        parentAIndex = ( np.random.random(1)*len(reservoir) ).astype('int')[0]
        #parentAIndex= reservoir['ID'].values[tempIndex]
        #print(tempIndex,reservoir['ID'].values,parentAIndex)
        parentA = reservoir.loc[parentAIndex]
        
        # Simulate offspring, link to parent IDs, and append to list
        newBarcode = simOffspring(parentA, reservoir, ordTime=time)
        newBarcode[0]['ParentA'] = parentAIndex
        #newBarcode[0]['Date'] = time
        newBarcodeList += newBarcode
        
    # Add any importations
    newBarcodeList += importations(time) #, justone=True)
    
    nNewEntries = len(newBarcodeList)
                    
    # Add new offspring/barcodes to list of entries
    # This becomes a history of all strains, making a phylogenetic tree
    if nNewEntries > 0:
        newBarcodeDF = pandas.DataFrame.from_dict(newBarcodeList)
        newBarcodeDF['ID'] = np.arange(lastID,lastID+nNewEntries) + 1
        strains = strains.append(newBarcodeDF[defaultColumns()], ignore_index=True)
        
        # Also add new barcodes to reservoir
        # This becomes a probabilistic representation of the frequency of each strain
        reservoir = reservoir.append(newBarcodeDF[defaultColumns()],
                                     ignore_index=True, sort=False)
    
    # Kill off some entries in the reservoir
    reservoir = trimReservoir(reservoir, dailyDeaths)
    
    # Update time
    time += dateStep
    
    return strains, time, reservoir



'''
Wall-clock based model for evolution
'''
def timeEvolve(strains, nSteps=600):
    
    #processed = np.zeros(len(strains)) 
    time = tStart  # Start date
    step = 0
    
    stop = 0
    
    # At first, the history of all strains ever existing (allStrains)
    # starts off identical to the current reservoir of viable strains (reservoir)
    # Maybe replace reservoir with a masking array?
    allStrains = strains.copy()
    reservoir = strains.copy()

    if verbose > 1:
        print('Running timeEvolve()')
    for i in range(nSteps):

        allStrains, time, reservoir = timeStep(allStrains,time,reservoir)
        
        global __resSize
        __resSize += [len(reservoir)] ###
        
        # Stop simulation if # of strains becomes too large
        if (len(allStrains) > 50000) or (len(reservoir) > 10000):
            if verbose >=1:
                print('Strain list reached limit.')
            break
        # Stop simulation if no more strains left in reservoir
        if len(reservoir) == 0:
            if verbose >=1:
                print('All strains have died out.')
            break
        # Stop simulation if reach end of time range
        if time > tEnd:
            if verbose >=1:
                print('Reached time limit.')
            break

        if verbose > 1:
            if int(i % (nSteps*0.1))==0:
                print(':', end='', flush=True)
            if int(i % (nSteps*0.01))==0:
                print('.', end='', flush=True)
    if verbose > 1:
        print('')
                        
    if verbose > 5:
        print(len(reservoir),len(allStrains), time)
        
    return allStrains






'''
Functions for Time Step - Reservoir Version
'''

def getRain(time, rho):
    return (rho+(1.-rho)*np.cos(np.pi*(time-100)/365.)**2)


def getR0_old(time):
    global __rho__, __R0__, tStart, tEnd
    rho = __rho__
    span = tEnd - tStart
    div1 = 0.2 #0.3333
    div2 = 0.6 #0.6667
    R0 = __R0[0]*((time-tStart)<(span*div1)) + __R0[2]*((time-tStart)>(span*div2)) + \
         __R0[1]*(((time-tStart)>=(span*div1)) & ((time-tStart)<=(span*div2)))
    return R0*getRain(time,rho)

    
def getR0(time):
    global __rho__, __R0__, tStart, tEnd
    rho = __rho__
    span = tEnd - tStart
    # Set divs globally
    global div1, div2, div3, div4, extendYears
    if extendYears==1:
        R0 = __R0[0]*((time-tStart)<(span*div1)) + __R0[3]*((time-tStart)>(span*div4)) + \
             __R0[2]*(((time-tStart)>=(span*div3)) & ((time-tStart)<=(span*div4))) + \
             __R0[1]*(((time-tStart)>=(span*div2)) & ((time-tStart)<=(span*div3))) + \
             (__R0[0] + (__R0[1]-__R0[0])*(time-span*div1-tStart)/(div2-div1)/span) \
               *(((time-tStart)>=(span*div1)) & ((time-tStart)<(span*div2)))
    else:
        R0 = __R0[0]*((time-tStart)<(span*div1)) + __R0[2]*((time-tStart)>(span*div3)) + \
             __R0[1]*(((time-tStart)>=(span*div2)) & ((time-tStart)<=(span*div3))) + \
             (__R0[0] + (__R0[1]-__R0[0])*(time-span*div1-tStart)/(div2-div1)/span) \
               *(((time-tStart)>=(span*div1)) & ((time-tStart)<(span*div2)))
    return R0 * getRain(time,rho) * max(0.0, 1. - getMeanCOI()/5.)


def timeStepReservoir(strains,time, reservoir):

    # Params
    #dailyNew = 3.    # Avg. no. of new parasites to generate each day
    #dailyDeaths = 3. # For now makes sense to make these two equal
                      # In the future this will be seasonal
    #dateStep = 4     # was 1
    
    # Remember ID value of current last entry so we can add more IDs later
    lastID = strains['ID'].values[-1]
    
    # Keep a list of new barcodes (to be appended to 'strains' later)
    # Each new barcode entry is actually a dict
    #   - will be converted to pandas row upon appending
    newBarcodeList = []
    
    # Use seasonal modulation based on PNAS appendix
    rho = __rho__
    dailyDeaths = __deathRate*len(reservoir)
    dailyNew = dailyDeaths*getR0(time)
    nNew = np.random.poisson(lam=dailyNew)
    global __dailyNewList ###
    __dailyNewList += [nNew]
    
    for i in range(nNew):
        
        # Pick a random parent from the reservoir
        parentAIndex = ( np.random.random(1)*len(reservoir) ).astype('int')[0]
        #parentAIndex= reservoir['ID'].values[tempIndex]
        #print(tempIndex,reservoir['ID'].values,parentAIndex)
        parentA = reservoir.loc[parentAIndex]
        
        # Simulate offspring, link to parent IDs, and append to list
        newBarcode = simOffspring(parentA, reservoir, ordTime=time)
        newBarcode[0]['ParentA'] = parentAIndex

        # Mix with another strain if in host with complex infection
        mean_COI = getMeanCOI()
        mixProb = mixed_infection_prob(mean_COI)
        if np.random.random(1) < mixProb*.5:  ### Doing this to be safe but may be wrong
            newBarcode[0]['Barcode'] = mixBarcode(newBarcode[0]['Barcode'], reservoir)
        newBarcodeList += newBarcode
        
    # Add any importations
    newBarcodeList += importations(time) #, justone=True)
    
    nNewEntries = len(newBarcodeList)
                    
    # Add new offspring/barcodes to list of entries
    # This becomes a history of all strains, making a phylogenetic tree
    if nNewEntries > 0:
        newBarcodeDF = pandas.DataFrame.from_dict(newBarcodeList)
        newBarcodeDF['ID'] = np.arange(lastID,lastID+nNewEntries) + 1
        strains = strains.append(newBarcodeDF[defaultColumns()], ignore_index=True)
        
        # Also add new barcodes to reservoir
        # This becomes a probabilistic representation of the frequency of each strain
        reservoir = reservoir.append(newBarcodeDF[defaultColumns()],
                                     ignore_index=True, sort=False)
    
    # Kill off some entries in the reservoir
    reservoir = trimReservoir(reservoir, dailyDeaths)
    
    # Update time
    time += dateStep
    
    return strains, time, reservoir




def setImportRate():
    global importRate
    importRate = 1. - (1.-__importRatePerDay)**dateStep
    return 1


def setDeathRate():
    global __deathRate
    __deathRate = 1. - (1.-__deathRatePerDay)**dateStep
    return 1


'''
Evolve barcodes by sampling from reservoir explicitly
I.e. - not based on indexing through parasite list or by strictly going off of wall clock
'''
def timeEvolveReservoir(strains, nSteps=600):

    global tStart, tEnd
    time = tStart  # Start date
    step = 0
    
    stop = 0  # stop flag
    
    # History of strains starts off with one dummy entry
    # Reservoir is initiated with 'strains'
    # Build history by picking from reservoir
    allStrains = strains.loc[0:2]
    reservoir = strains.copy()
    
    setDeathRate()
    setImportRate()

    global __resSize, __dates
    __resSize += [len(reservoir)]
    __dates += [time]


    if verbose > 1:
        print('Running timeEvolveReservoir()')
    if verbose > 2:
        print('tStart: %d,  tEnd: %d'%(tStart,tEnd))
    for i in range(nSteps):

        allStrains, time, reservoir = timeStepReservoir(allStrains,time,reservoir)
        
        __resSize += [len(reservoir)] ###
        __dates += [time]
        
        # Stop simulation if # of strains becomes too large
        if (len(allStrains) > historyMax) or (__resSize[-1] > reservoirMax):
            if verbose >=1:
                print('Strain list reached limit.')
            break
        # Stop simulation if no more strains left in reservoir
        if len(reservoir) == 0:
            if verbose >=1:
                print('All strains have died out.')
            break
        # Stop simulation if reach end of time range
        if time > tEnd:
            if verbose >=1:
                print('Reached time limit.')
            break

        if verbose > 1:
            if int(i % (nSteps*0.1))==0:
                print(':', end='', flush=True)
            if int(i % (nSteps*0.01))==0:
                print('.', end='', flush=True)
    if verbose > 1:
        print('')

                        
    if verbose > 5:
        print(len(reservoir),len(allStrains), time)
        
    return allStrains



def resetHistory():
    global __dailyNewList,__resSize,__dates
    __dailyNewList = []
    __resSize = []
    __dates = []
    return 1






'''
Use this to make sure part of model have correct dynamics
'''
def componentTest(nsteps=500, agentbased=1, strainNum=1, simOutput=1):

    settings = []
    
    # initialize parasite strains
    strains = initStrains(nStrain=initStrainNumber)
    barcodes = bc.getBarcode(strains)
    nSNPs = bc.nSNPs
    if strainNum==1:
        for i in range(nSNPs):
            barcodes[:,i] = barcodes[0,i]
    else:
        for i in range(nSNPs):
            barcodes[int(initStrainNumber*.5):,i] = barcodes[int(initStrainNumber*.5),i]
            barcodes[:int(initStrainNumber*.5),i] = barcodes[0,i]
    strains['Barcode'] = barcodes.tolist()

    resetHistory()

    # generate phylogenetic tree
    # for now set total number of steps
    # maybe change to just time period later?
    if agentbased:
        # Evolve/simulate a phylogeny with agent-based model
        strainsEvolved = timeEvolveAgent(strains, nSteps=nsteps)
    else:
        # Simulate phylogeny with "wall-clock" model
        strainsEvolved = timeEvolveReservoir(strains, nSteps=nsteps)

    toDateTime(strainsEvolved)
    if simOutput:
        strainsEvolved['Year_orig'] = strainsEvolved['Year']
        strainsEvolved['Year'] = strainsEvolved['Date'].dt.year

    if verbose:
        print('# of entries:',len(strainsEvolved))

    return strainsEvolved, strains, settings



'''
Run sim
'''
def runSim(nsteps=500, agentbased=1, simOutput=1):
    
    # Should eventually fill this with run params
    settings = []
    
    # initialize parasite strains
    strains = initStrains(nStrain=initStrainNumber)
    resetHistory()
    
    # generate phylogenetic tree
    # for now set total number of steps
    # maybe change to just time period later?
    if agentbased:
        # Evolve/simulate a phylogeny with agent-based model
        strainsEvolved = timeEvolveAgent(strains, nSteps=nsteps)
    else:
        # Simulate phylogeny with "wall-clock" model
        strainsEvolved = timeEvolveReservoir(strains, nSteps=nsteps)

    toDateTime(strainsEvolved)
    if simOutput:
        strainsEvolved['Year_orig'] = strainsEvolved['Year']
        strainsEvolved['Year'] = strainsEvolved['Date'].dt.year

    if verbose:
        print('# of entries:',len(strainsEvolved))

    return strainsEvolved, strains, settings
    
            
    

    
if __name__ == '__main__':
    print('Hello')
