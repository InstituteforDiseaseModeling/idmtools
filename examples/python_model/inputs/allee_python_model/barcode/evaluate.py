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

import barcode.model as bm
import barcode.barcode as bc
import barcode.data as data
import barcode.analysis as ba
import barcode.unittests as bu



'''
Constants and reference variables
'''

verbose = 0

#evalYears = np.arange(2006,2013+1)  # np.arange(2009,2015)
evalYears = np.zeros(1) #np.arange(2006,2016+1)

baseErr = np.zeros(0)

def setYears(year1,year2):
    global evalYears, baseErr
    evalYears = np.arange(year1,year2)
    nYrs = len(evalYears)
    baseErr = np.zeros(0)
    baseErr = np.append(baseErr,np.ones(nYrs)*.04)
    baseErr = np.append(baseErr,np.ones(nYrs)*.04)
    baseErr = np.append(baseErr,np.ones(nYrs)*1.)
    baseErr = np.append(baseErr,np.ones(nYrs)*2.)
    baseErr = np.append(baseErr,np.ones(4)*1.)
    baseErr = np.append(baseErr,7.)
    baseErr = np.append(baseErr,6.)
    return 1

setYears(2006,2016+1)


'''
Likelihood functions
'''
# Obsolete
#def likelihood():
#    return None



'''
Functions for running sets of simulations and evaluating likelihoods
'''

'''
Input:
  barcodeHistory - output of barcode.model.runSim
                   i.e. allStrains/finalStrains
                   bit of a misnomer, but we want the history of all infections
Output:
  stats - array of summary statistics describing complexity of phylogeny
          (borrowed from PNAS paper)
          By index, the statistics are:
    0-7   - fraction of monogenomic infections with unique barcodes, by year
    8-15  - fraction of monogenomic infections with repeated barcodes, by year
    16-23 - number of repeated barcodes repeated exactly twice in a given year, by year
    24-31 - number of repeated barcodes repeated more than twice in a given year, by year
    32 - number of repeated barcodes that persist exactly two years
    33 - ...ditto for exactly three years
    34 - ...ditto for exactly four years
    35 - ...ditto for greater than four years (allowing for missing years within the interval)
    _  - number of repeated barcodes that appear and persist for >=2 years in observation time (???)
    _  - number of repeated barcodes that disappear after persisting for at least two years (???)
'''
def getStats(barcodeHistory, noNANs=1, yearOption=0):

    bHistory = barcodeHistory.copy()
    
    # Make sure year is in right format
    # Might want to plan this better?
    bHistory['Year_orig'] = bHistory['Year']
    if yearOption==1:        
        bHistory['Year'] = bHistory['Date'].dt.year
    
    # Pull out barcode relations from barcode history
    relationM, dij, deltaT = bc.getRelation(bHistory,option=1, fillLowerLeft=1,useAll=1, verbose=2,
                                            timeOption=2) #yearOption) 
    
    # Get uniqueness information
    barcodes = bc.getBarcode(bHistory)
    wN,wX,wCM,wUnique,wRepeat = ba.findClonesSingles(barcodes, relationM, fullMatch=1.)
    
    #indices, countList = bc.cloneSort(barcodes,relationM, fullMatch=1.)
        
    # Evaluate each stat
    fracRepeat = np.sum(wCM & wRepeat)/np.sum(wCM)
    fracUnique = np.sum(wCM & wUnique)/np.sum(wCM)
    fracUniqueYear = fracMonoUnique(bHistory, wCM, wUnique)
    fracRepeatYear = fracMonoRepeat(bHistory, wCM, wRepeat)
    numRepeatYear2 = numRepeatByYear2(bHistory,relationM)
    numRepeatYear = numRepeatByYear(bHistory,relationM)
    numPersist, created, destroyed = numPersisting(bHistory, relationM, deltaT)

    # OBSOLETE - Using 999 as a delimiter for easy viewing
    stats = np.zeros(0)
    stats = np.append(stats,fracUniqueYear)
    #stats = np.append(stats,999)
    stats = np.append(stats,fracRepeatYear)
    #stats = np.append(stats,999)
    stats = np.append(stats,numRepeatYear2)
    #stats = np.append(stats,999)
    stats = np.append(stats,numRepeatYear)
    #stats = np.append(stats,999)
    stats = np.append(stats,numPersist)
    stats = np.append(stats,created)
    stats = np.append(stats,destroyed)

    if noNANs:
        stats[ np.where( stats!=stats ) ] = 0.
    
    return stats


def printStats(stats):
    global evalYears
    nYrs = len(evalYears)
    print('Fraction Unique Per Year:',stats[0:nYrs])
    print('Fraction Repeat Per Year:',stats[nYrs:(2*nYrs)])
    print('# repeated exactly twice, per Year:',stats[(2*nYrs):(3*nYrs)])
    print('# repeated > twice, per Year:',stats[(3*nYrs):(4*nYrs)])
    print('# barcodes persisting for x years:',stats[4*nYrs:(4*nYrs+4)])
    print('# persisting barcodes created:',stats[4*nYrs+4])
    print('# persisting barcodes destroyed:',stats[4*nYrs+5])
    return 1


'''Fraction of monogenetic infection that are unique, by Year'''    
def fracMonoUnique(bHistory, wCM, wUnique):
    global evalYears
    years = evalYears
    fracByYear = np.zeros(len(years))
    
    for i,year in enumerate(years):
        inyear = bHistory['Year'].values == year
        fracByYear[i] = np.sum(wCM & wUnique & inyear)/np.sum(wCM & inyear)
        
    return fracByYear
    

'''Fraction of monogenetic infection that are repeats, by Year'''    
def fracMonoRepeat(bHistory, wCM, wRepeat):
    global evalYears
    years = evalYears
    fracByYear = np.zeros(len(years))
    
    for i,year in enumerate(years):
        inyear = bHistory['Year'].values == year
        fracByYear[i] = np.sum(wCM & wRepeat & inyear)/np.sum(wCM & inyear)
        
    return fracByYear



def trimByYear(bHistory, relation0):
    return None
    

def numRepeatByYear20(bHistory, relation0, fullMatch=1):
    global evalYears
    years = evalYears
    wMatchN = np.sum(relation0==fullMatch, axis=1) == 2
    repeatByYear = np.zeros(len(years))
    
    for i,year in enumerate(years):
        inyear = bHistory['Year'].values == year
        repeatByYear[i] = np.sum(wMatchN & inyear)
        
    return repeatByYear


def numRepeatByYear0(bHistory, relation0, fullMatch=1):
    global evalYears
    years = evalYears
    wMatchN = np.sum(relation0==fullMatch, axis=1) > 2
    repeatByYear = np.zeros(len(years))
    
    for i,year in enumerate(years):
        inyear = bHistory['Year'].values == year
        repeatByYear[i] = np.sum(wMatchN & inyear)
        
    return repeatByYear


'''Number of barcodes repeated exactly twice, per year'''
def numRepeatByYear2(bHistory, relation0, fullMatch=1):
    global evalYears
    years = evalYears
    repeatByYear = np.zeros(len(years))
    
    for i,year in enumerate(years):

        # Find entries occurring in year of interest
        inyear = (bHistory['Year'].values == year)
        if np.sum(inyear)==0:
            repeatByYear[i] = 0
        else:
            tempRelation = relation0[:,inyear][inyear,:]
            indices,_ = bc.cloneSort(bHistory.loc[inyear],tempRelation, option=1, fullMatch=1.)
            ###print(tempRelation[:12,:12])
            ###print(indices,countList)

            # Only do fullmatch comparisons on pairs of entries both occurring in year
            wMatchN = np.sum(tempRelation==fullMatch, axis=1) == 2
            repeatByYear[i] = np.sum(wMatchN[indices])
        
    return repeatByYear


'''Number of barcodes repeated more than twice, per year'''
def numRepeatByYear(bHistory, relation0, fullMatch=1):
    global evalYears
    years = evalYears
    repeatByYear = np.zeros(len(years))
    
    for i,year in enumerate(years):
        
        # Find entries occurring in year of interest
        inyear = (bHistory['Year'].values == year)
        if np.sum(inyear)==0:
            repeatByYear[i] = 0
        else:
            tempRelation = relation0[:,inyear][inyear,:]
            indices,_ = bc.cloneSort(bHistory.loc[inyear],tempRelation,option=1, fullMatch=1.)

            # Only do fullmatch comparisons on pairs of entries both occurring in year
            wMatchN = np.sum(tempRelation==fullMatch, axis=1) > 2
            repeatByYear[i] = np.sum(wMatchN[indices])
        
    return repeatByYear



def numPersisting0(bHistory, relation0, deltaT, fullMatch=1):

    # Get only the delta_ts that correspond to repeats
    # and pick the maximum time between repeats
    maxPersist = np.max((relation0 == fullMatch) * np.abs(deltaT), axis=1)
    ###print(relation0 == fullMatch) ###
    ###print(np.abs(deltaT)) ###
    ###print(maxPersist[:600]) ###
    # Convert to years
    maxPersist = np.ceil(maxPersist.astype('float')/365.)
    ###print(maxPersist[:600]) ###

    numPersist = np.zeros(4)
    for i,years in enumerate(range(2,5)):
        numPersist[i] = np.sum(maxPersist==years)
    numPersist[3] = np.sum(maxPersist>4.)
            
    return numPersist



'''Total number of barcodes that persist for x years, as a function of x'''
def numPersisting(bHistory, relation0, deltaT, fullMatch=1):

    # For each barcode:
    # Get only the delta_ts that correspond to repeats
    # and pick the maximum time between repeats
    maxPersist = np.nanmax((relation0 == fullMatch) * np.abs(deltaT), axis=1)
    # Convert to years
    maxPersist = maxPersist.astype('float')/365. #np.ceil(maxPersist.astype('float')/365.)

    # Now only pick one max time per repeated barcodes (strains)
    indices,countList = bc.cloneSort(bHistory,relation0,option=0, fullMatch=1.)
    
    counter = 0
    stop = 0
    persistList = []
    created = 0
    destroyed = 0
    while stop==0:
        thisStrain = indices[counter:(counter+countList[counter])]
        persistList += [np.max(maxPersist[thisStrain])]
        counter += countList[counter]
        # Check if strain was created or destroyed during the 'survey'
        sYears = bHistory['Year'].values[thisStrain]
        if np.max(sYears)>evalYears[0]:
            created += 1
        if np.max(sYears)<evalYears[-1]:
            destroyed += 1
        # Stop when we hit first unique strain
        if countList[counter]==1:
            stop = 1
    
    ### print(indices,countList,persistList,maxPersist)
    
    # Do histogram of persist times
    try:
        numPersist,bins = np.histogram(np.array(persistList),bins=range(1,10))
    except ValueError:
        global verbose
        if verbose > 1:
            print('PersistList probably has NaN or Inf error:')
            print(np.array(persistList))
            if verbose > 2:
                print(maxPersist)
                print(deltaT)
                print(bc.getDatesOrYear(bHistory,option=2))
                print(bHistory)
        numPersist = np.zeros(6) #The 6 doesn't mean anything
    
    # Combine all persist #s greather than 4 to one bin
    numPersist[3] = np.sum(numPersist[3:])
    
    return numPersist[:4], created, destroyed





'''
Old version of simple test simulation
(obsolete)
'''
def simpleRun(nsteps=400, agentbased=0, seed=3, clusterID=2):

    if 1:
        np.random.seed(seed)
        strainsEvolved, strains, settings = bm.runSim(nsteps=nsteps, agentbased=agentbased)
            # Good seeds for agentbased: 3, 4
            # Good seeds for wallclock: 3

    print('# of entries:',len(strainsEvolved),'\n')
    bm.toDateTime(strainsEvolved)

    if 1:
        relationM, _, _ = bc.getRelation(strainsEvolved,option=1, useAll=1)

        if 0:
            relationM2 = relationM*relationM*24.
            indices,countlist,haplolist = bc.cloneSort(strainsEvolved['Barcode'].values,
                                                       relationM2, option=1, gethaplo=1)
            print('Indices:\n',indices,'\nCounts per strain:\n',countlist,'\n')

            strainsEvolved.loc[indices,'haplotype number'] = haplolist
            strainsEvolved['year'] = (strainsEvolved['Date'].values/100.).astype('int')
            strainsEvolved['name'] = strainsEvolved['ID'].values
            if 0:
                print(strainsEvolved['Barcode'])
                print('')
                print(dfS['Barcode'])
                print('')

    if 1:
        sBarcode = bc.getBarcode(strainsEvolved)

        dates = strainsEvolved['Date']
        minDate = 733694. 
        maxDate = 733777. 
        dates = (dates - minDate)/(maxDate-minDate)*(2015.-2008.) + 2008

        x = ba.occurrences(sBarcode, relationM, dates, clusterID=clusterID)
        
    return strainsEvolved

    

    
if __name__ == '__main__':
    print('Hello')
