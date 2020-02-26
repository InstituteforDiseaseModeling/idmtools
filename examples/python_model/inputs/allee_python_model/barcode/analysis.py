import os
import warnings
import time

import numpy as np
import pandas
import scipy

import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import rc

import barcode.barcode as bc
import barcode.unittests as bu




'''
Function for showing fraction of barcodes each year that are repeated.
Makes stacked bar plot.
Inputs:
  dataframe of barcodes (must have haplotype number, name, and year)
  showtable - if 1, prints pivot table as well
  useOrig - if 1, do analysis on orignal Thies dataframe format
          - if not, assume format matches the package's barcode format
Outputs:
  integer boolean
'''

def stackedbars(df0, showtable=0, verbose=0, useOrig=1, yearRange=[2006,2012]):

    df = df0.copy()

    # Generate haplotype IDs if necessary
    if not ('haplotype number' in df.columns):
        relation, _, _ = bc.getRelation(df, fillLowerLeft=1, useAll=0)
        indices, countList, hapIDs = bc.cloneSort(bc.getBarcode(df), relation, 
                                                  option=0, gethaplo=1,fullMatch=1.)
        #print(indices, countList, hapIDs)
        df.loc[indices,'haplotype number'] = hapIDs

    # Put year into right case if necessary
    if not ('year' in df.columns):
        if 'Year' in df.columns:
            df['year'] = df['Year'].values
        else:
            df['year'] = df['Date'].dt.year

    # Get label of some index column we can use to count entries after groupby
    if 'name' in df.columns:
        IDlabel = 'name'
    elif 'ID' in df.columns:
        IDlabel = 'ID'
    else:
        df['ID'] = df.index
        IDlabel = 'ID'

    df.sort_values(by=['haplotype number', 'year'])

    # This seems to be obsolete
    if 1:
        None
    elif useOrig:
        isknown = np.sum( df[ df.columns[range(3,27)] ].isin(['C','G','A','T']), axis=1 )
    else:
        barcodetype = bu.validBarcode(bc.getBarcode(df))
        if barcodetype==2:
            isknown = np.sum( df[ df.columns[range(3,27)] ].isin(['C','G','A','T']), axis=1 )
        elif barcodetype==1:
            isknown = np.sum( df[ df.columns[range(3,27)] ].isin([1,2,3,4]), axis=1 )

    # Count x number of occurrences of each haplotype
    hapgroups = df.groupby('haplotype number')
    hapcount = hapgroups[[IDlabel]].count().rename({IDlabel: "count"}, axis='columns')
    if verbose > 0:
        print('')
        print('# of occurrences of each haplotype:')
        print(df.groupby('haplotype number')[IDlabel].count().loc[0:19])

    # Count number of haplotypes that reoccur x number of times
    if verbose > 0:
        print('')
        print('histogram of haplotype occurrences (frequencies of haplotype counts):')
        print(hapcount.groupby('count')['count'].count())

    # The following is adapted from https://python-graph-gallery.com/13-percent-stacked-barplot/

    # Group data into year and haplotype
    #years = range(2006,2014)
    dfprevalence = df.groupby(['year', 'haplotype number'])[IDlabel].count().reset_index(name='count')
    if verbose > 1:
        print('Prevalece (actually, number of observed cases) of barcodes by year:')
        print(dfprevalence)
    dfpivot = dfprevalence.pivot_table(index='year',columns='haplotype number',values='count', fill_value=0)
     
    # Pivot data to get total number of cases per year
    # Use total number to get percentage breakdown for each year by barcode
    dfpercent = dfpivot.copy()
    years = dfpivot.index.tolist()
    #years = set(years).intersection(yearRange)
    nCols = len(dfpivot.columns)
    totalcases = np.sum( dfpivot[ dfpivot.columns[range(0,nCols)] ].values, axis=1 )
    dfpivot['total'] = totalcases
    for i in years:
        dfpercent.loc[i,dfpivot.columns[range(0,nCols)]] = dfpivot.loc[i,dfpivot.columns[range(0,nCols)]] \
            / dfpivot.loc[i,'total']
    if showtable:
        print('# cases observed for each barcode, by year:')
        print(dfpivot)
     
    #Save current bar height so we can stack bars, set up plot variables, don't plot uniques
    currenttop = dfpercent.loc[:,1].values*0.
    barWidth = 0.85
    haprepeats = hapcount.loc[hapcount['count']>1]

    #Get colors as ints
    colors = np.floor(np.random.random(len(haprepeats))*256*256*256).astype(int)

    #Plot bars of each haplotype one by one
    for i,index in enumerate(haprepeats.index.tolist()):
        # Plot each haplotype, converting hex to correct rgb string format
        currentdata = dfpercent.loc[:,index].values
        plt.bar(years, currentdata, bottom=currenttop, 
                    color='#'+format(colors[i],'06x'), edgecolor='black', width=barWidth) #, label='hap#'+format(index,'03d'))
        currenttop += currentdata
    plt.bar(years, 1-currenttop, bottom=currenttop, 
                    color='#e0e0e0', edgecolor='black', width=barWidth, label='unique barcodes')
     
    # Custom x axis
    plt.xticks(years)
    plt.xlabel('year')

    # Show graphic
    plt.show()

    return dfpivot







'''
Function for examining distribution and path of clone through time and space
'''
def trackClone(df0, relation0, dij0, dt0, clusterID=0,
               linkthresh=0.88, graphthresh=0.6, relationthresh=0.6,clustermin=0,maxGraph=50,
               wholerange=1, senegal=1, fromL2=1, clusterthresh=0):

    sBarcode = bc.getBarcode(df0)

    # Make sure matrix is symmetric about diagonal
    relationFull = np.maximum(relation0,relation0.transpose())
    if fromL2:
        relationFull = relationFull*relationFull * 24.

    # Group entries by clones and sort by number of clones in each group
    indices,countList = bc.cloneSort(sBarcode,relationFull,1)

    # Look at all entries that are related to some clone group by some threshold clusterthresh
    #clusterID = 0
    if clusterthresh > 0:
        None
    elif fromL2:
        if senegal:
            clusterthresh = 21
        else:
            clusterthresh = 19
    else:
        clusterthresh = 0.85
    wRelated = relationFull[indices[clusterID],:] > clusterthresh

    if senegal:
        allyears = [2008,2009,2011,2012,2013,2014,2015,2016]
    else:
        allyears = [2008,2009,2010,2011,2012,2013,2014,2015,2016]
        graphthresh = 0.8
    
    x = showyear(allyears, df0[wRelated], relation0[wRelated,:][:,wRelated], 
                    dij0[wRelated,:][:,wRelated], dt0[wRelated,:][:,wRelated],
                    linkthresh=linkthresh, graphthresh=graphthresh, relationthresh=relationthresh,
                    clustermin=clustermin, maxGraph=maxGraph, 
                    wholerange=wholerange, senegal=senegal)
    return 1




'''
Function for showing relationships between delta_ij, delta_t, and barcodes by year 
Could potentially generalize for slices on other params
Inputs:
  years - list of years to be used in analysis
  dfSenegal - dataframe of barcodes and metadata
  relation0 - relation matrix corresponding to dataframe
  dij0 - Geo. distance matrix
  dt0 - delta_t matrix
  linkthresh - threshold on distance metric for drawing an edge between two barcodes
  graphthresh - threshold on distance metric for including a comparison in network graph
                (not necessarily drawn in as an edge in the graph - allows one to include
                similar barcodes in a plot without linking them, in case they are weakly related)
  relationtresh - threshold on distance metric values to be included in scatter plots
  clustermin - minimum cluster size for plotting
  maxGraph - maximum number of entries to be included in plot of graph (avoids N^2 issues)
  senegal - option to specify data source
    1 - Senegal data
    0 - Zambia data
Outputs:
  integer
'''

# TO DO - rewrite so it's not Senegal centric?

def showyear(years, df0, relation0, dij0, dt0, 
            linkthresh=0.9, graphthresh=0.8, relationthresh=0.2,clustermin=1,maxGraph=300, senegal=0,
            wholerange=1, autoplot=0 ):

    t0 = time.time()
    senYears = df0['Year'].values
    inyear = senYears < 0
    for i in range(len(years)):
        inyear = np.logical_or(inyear, senYears==years[i])
    nSamps = len(senYears[inyear])
    if nSamps==0:
        warnings.warn('No entries in selected years', RuntimeWarning)
        return 0
    print(time.time() - t0)

    df = df0.loc[inyear]
    
    relationS = relation0[inyear,:][:,inyear]
    dijS = dij0[inyear,:][:,inyear]
    deltat = dt0[inyear,:][:,inyear]
    #dfS['Date'].values.astype('datetime64[h]').astype(int)
    #dfS['Date'].apply(lambda x: x.toordinal()).values
    #ordDates = df['Date'].apply(lambda x: x.toordinal()).values #df0['Date'].values
    ordDates = bc.getDatesOrYear(df, option=1)
    if senegal:
        minDate = 733694. #min(senDates[senYears==2008]) Hardcode this so it works with whatever subset of df0
        maxDate = 736637. #max(senDates)                 Maybe it's better to restructre per subset?
    else:
        minDate = min(ordDates)
        maxDate = max(ordDates)
    dates = (ordDates-minDate)/(maxDate-minDate)
        
    plt.figure(num=None, figsize=(14, 21), dpi=80)

    # Pick out nodes that match at least with one other node
    # This is more stringent than the histograms below will be because we want the clusters to be readable
    clustermin = 1
    ismatch = np.sum(relationS>=graphthresh, axis=1) > clustermin
    nGraph = min([maxGraph,nSamps])
    relationmatches = relationS[ismatch,:][:,ismatch][:nGraph,:nGraph]
    relationmatches[np.where(relationmatches < linkthresh)] = 0. #np.nan
    
    # Convert matrix to graph
    G = nx.convert_matrix.from_numpy_matrix(relationmatches, parallel_edges=False)

    # Extract edges to analyze later
    edgelist = list(G.edges(data=True)) #G.edges
    edgeDF = pandas.DataFrame(edgelist)
    edgeDF[2] = edgeDF[2].apply(lambda x: x['weight'])
    edgeweights = edgeDF[2].values

    # Extract edges to analyze later
    nodelist = list(G.nodes(data=True)) 
    nodeDF = pandas.DataFrame(nodelist)
    nodes = nodeDF[0].values # this is redundant but I'm trying to be safe
    nodeweights = dates[nodes]

    # Plot graph
    plt.subplot(321)
    plt.title('Clustering of barcodes, by similarity metric')
    pos = nx.spring_layout(G)
    nx.draw(G,pos,node_color=nodeweights*(2016.5-2007.5)+2007.5, cmap=plt.cm.rainbow, vmin=2007.5, vmax=2016.5, 
            edge_color=edgeweights, width=1, edge_cmap=plt.cm.BuPu, with_labels=False,
            edge_vmin=graphthresh, edge_vmax=1., node_size=150, alpha=0.5)  # node_color='#A0CBE2'

    
    # Use more relaxed constraint for picking out barcode pairs to use in scatter plots
    # Default is relationthresh = 0.2, as set in function header above
    indices = np.where(relationS > relationthresh)

    # Scatterplot of distance vs barcode similarity
    plt.subplot(324)
    if wholerange:
        plotrange = [[0.,1],[0,.1]]
    else:
        plotrange = [[relationthresh,1],[0,.06]]
    hdata, xedge, yedge, himage = plt.hist2d(relationS[indices], dijS[indices], 
                                             bins=[40,50], range=plotrange, cmax=200*len(years))
    plt.title('Histogram of scatterplot')
    plt.ylabel('distance')
    plt.xlabel('barcode similarity')
    plt.colorbar()

    # 2D histogram of distance vs barcode similarity, increased contrast on color bar
    plt.subplot(323)
    if wholerange:
        plotrange = [[0.,1],[0,1]]
    else:
        plotrange = [[relationthresh,1],[0,1]]
    hdata, xedge, yedge, himage = plt.hist2d(relationS[indices], dijS[indices], 
                                             bins=[40,100], range=plotrange, cmax=600*len(years))
    plt.title('Histogram of scatterplot')
    plt.ylabel('distance')
    plt.xlabel('barcode similarity')
    plt.colorbar()

    
    # Plot locations of barcodes with GPS entires, zoomed in on central cluster
    # Show lines connecting probably transmission parent-child pairs
    #
    # Set up plot variables and colormap lookup table
    plt.subplot(322)
    sLon = df['Lon'].values
    sLat = df['Lat'].values
    if autoplot:
        plt.xlim(min(df['Lon']),max(df['Lon'])) 
        plt.ylim(min(df['Lat']),max(df['Lat'])) 
        #plt.xlim(min(df0['Long']),max(df0['Long'])) 
        #plt.ylim(min(df0['Lat']),max(df0['Lat'])) 
    elif senegal:
        plt.xlim(-16.96,-16.89)
        plt.ylim(14.74,14.84)
    else:
        plt.xlim(26.,29.)
        plt.ylim(-18.,-16.)
    nTable = 100
    clookup = plt.cm.get_cmap('rainbow',nTable)
    # Other good cmaps: rainbow, viridis, plasma,cividis
    # 
    # Find edges with new criteria:
    #graphthresh = 0.9
    clustermin = 8
    ismatch = np.sum(relationS>=graphthresh*1.125, axis=1) > clustermin
    relationmatches = relationS[ismatch,:][:,ismatch] #[:100,:100]
    relationmatches[np.where(relationmatches < graphthresh)] = 0. #np.nan
    G = nx.convert_matrix.from_numpy_matrix(relationmatches, parallel_edges=False)
    edgelist = list(G.edges(data=True)) 
    #
    # Plot edges on map
    for i,j,k in edgelist:
        if k['weight'] > 0.97:
            plt.plot(sLon[[i,j]], sLat[[i,j]], 'k-', alpha=(30.*(k['weight']-.97))**2, #0.5, 
                     color=mcolors.rgb2hex(clookup( int(min(dates[ismatch][i],dates[ismatch][j])*nTable) )[:3])) 
    # Plot barcode nodes on top
    plt.scatter(sLon,sLat, s=100., c=dates*(2016.5-2007.5)+2007.5, cmap=plt.cm.rainbow, alpha=0.3,vmin=2008,vmax=2016)
    plt.title('Location of barcode samples: Showing links to probable parent')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    cb = plt.colorbar()
    cb.set_label('time, normalized')
    
    # Plot scatter in delta_t and delta_ij (x and y), compared to barcode similarity (colorbar)
    plt.subplot(325)
    #
    w = np.where(relationS[indices] > 0.85)[0]
    indicesw = (indices[0][w],indices[1][w])
    #print(np.min(relationS),np.max(relationS)) ###
    #
    # Set plot bounds
    if wholerange:
        plt.xlim(0.,100.)
        vmin = 0.6
    else:
        plt.xlim(0.,10.) #np.max(deltat[indicesw]))
        vmin = relationthresh
    plt.ylim(0.,0.2)
    plt.scatter(deltat[indicesw],dijS[indicesw], s=50., c=relationS[indicesw], cmap=plt.cm.BuPu, 
                alpha=.2, vmin=vmin,vmax=1.) #, vmin=0.6,vmax=1.)
    cb = plt.colorbar()
    cb.set_label('barcode similarity')
    #
    w = np.where(relationS[indices] <= 0.85)[0]
    indicesw = (indices[0][w],indices[1][w])
    plt.scatter(deltat[indicesw],dijS[indicesw], s=50., c=relationS[indicesw], cmap=plt.cm.BuPu, 
                alpha=.02, vmin=vmin,vmax=1.)
    #
    plt.title('Scatter of case linkages by time, distance, and barcode')
    plt.ylabel('distance')
    plt.xlabel('delta_time')
    plt.show()

    return 1




'''
Function for finding uniques, repeats, etc.
'''
def findClonesSingles(barcode, relation0, nX=1, fullMatch=24):
    
    barcodetype = bu.validBarcode(barcode)
    
    # Find instances of Ns, Xs, uniques, repeated etc
    if barcodetype==2:
        wN = np.sum(barcode=='N', axis=1) >= nX   # Ns
        wX = np.sum(barcode=='X', axis=1) >= nX   # Xs
    elif barcodetype==1:
        wN = np.sum(barcode==3, axis=1) >= nX     # Ns
        wX = np.sum(barcode==4, axis=1) >= nX     # Xs
    wCM = np.logical_not(wN) & np.logical_not(wX) # Complete and monogenetic barcode samples

    wSingle = np.sum(relation0==fullMatch, axis=1) == 1  # single-occurrence barcodes
    wClone = np.sum(relation0==fullMatch, axis=1) > 1    # clones

    return wN, wX, wCM, wSingle, wClone
    


'''
Function for plotting instances of a clone and its relatives vs time
'''
def occurrences(barcode, relation0, dates, clusterID=0, relationMetric=1):
    
    relationFull = np.maximum(relation0,relation0.transpose())
    if relationMetric==0:
        relationFull = relationFull*24.
    elif relationMetric==1:
        relationFull = relationFull*relationFull*24.
    else:
        None

    indices,countList = bc.cloneSort(barcode,relationFull,1)
    #print(indices[:10],countList[:10])
    #clusterID = 10

    wN, wX, wCM, wSingle, wClone = findClonesSingles(barcode, relation0)

    # Sort relation matrix into order matching cloneSort output
    # Convert barcode metric values as necessary
    clusterMatches = relationFull[indices[clusterID]]
    clusterTag = clusterMatches*0

    # Get instances of barcodes matching or similar to clones
    clusterTag[np.where((clusterMatches > 20) & wN & np.logical_not(wX))] = 7
    clusterTag[np.where((clusterMatches > 20) & wX & np.logical_not(wN))] = 6
    clusterTag[np.where((clusterMatches > 20) & wX & wN)] = 5
    clusterTag[np.where((clusterMatches == 23) & wCM)] = 4
    clusterTag[np.where((clusterMatches == 22) & wCM)] = 3
    clusterTag[np.where((clusterMatches == 21) & wCM)] = 2
    clusterTag[np.where(clusterMatches == 24)] = 8

    # Plot each match type on separate rows of graph
    plt.figure(figsize=[14,6])
    plt.ylim(1,9)
    plt.xlim(2008,2015)
    plt.plot(dates,clusterTag,'ro',alpha=.3)
    
    ylabels = ['3 off','2 off','1off','>1 Ns and Xs','>1 Xs','>1 Ns','clones']
    plt.yticks(np.arange(2,9),ylabels)
    plt.show()
    
    return 1




'''
Function for making cluster analysis plots
'''
def clusters(dfT0, relationT, dfS0, relationS,
             clusterID=0, useSpatial=0, verbose=0):

    dfS = dfS0.copy()
    sBarcode = bc.getBarcode(dfS)
    #sLatLon = dfS[['Lat','Lon']].values
    #senDates = dfS['Date'].values

    dfT = dfT0.copy()
    tBarcode = bc.getBarcode(dfT)

    barcodetype = bu.validBarcode(tBarcode)

    # Find samples matching clustering criteria
    wN, wX, wCM, wSingle, wClone = findClonesSingles(tBarcode, relationT)
    wR1 = np.random.random(len(wN)) > 0.5
    wR2 = np.logical_not(wR1)

    print('This is our prior on how often we expect Ns and Xs to match with certain types of barcodes...')
    print('Number of complete + monogenetic samples that are unique:',np.sum(wCM & wSingle))
    print('Number of complete + monogenetic samples that are repeated:',np.sum(wCM & wClone))
    fracUnique = np.sum(wCM & wSingle)/np.sum(wCM)
    fracRepeat = np.sum(wCM & wClone)/np.sum(wCM)
    print('Fraction that is unique:',fracUnique)
    print('Fraction that is repeated:',fracRepeat,'\n')

    # Initialize fill-comparison matrices
    nPoints = 20
    thresh = np.zeros(nPoints)
    totalSVTx = np.zeros([nPoints,4]) # [# tested, # barcodes matched with, # without matches, # without any matches]
    totalCVTx = np.zeros([nPoints,4]) # [# tested, # barcodes matched with, # without matches, # ?]
    totalUx = np.zeros([nPoints,2])
    totalSVTn = np.zeros([nPoints,4]) # [# tested, # barcodes matched with, # without matches, # without any matches]
    totalCVTn = np.zeros([nPoints,4]) # [# tested, # barcodes matched with, # without matches, # ?]
    totalUn = np.zeros([nPoints,2])
    totalU = np.zeros([nPoints,2])
    for i in range(1,nPoints):
        thresh[i] = 24-i #np.sqrt(float(24-i)/24.)
        if verbose > 0:
            print('Silly metric threshold:',thresh[i])
        #
        # Find samples that match X/N criteria
        nX = i
        if barcodetype==2:
            wN = np.sum(tBarcode=='N', axis=1) == nX  # Ns
            wX = np.sum(tBarcode=='X', axis=1) == nX  # Xs
        else:
            wN = np.sum(tBarcode==3, axis=1) == nX  # Ns
            wX = np.sum(tBarcode==4, axis=1) == nX  # Xs
        #
        # Do fill comparisons on Xs
        # SingleVsThresh+CloneVsThresh is a fakeout - it just means no constraint on uniqueness
        # in this case it was and-ed with wCM so it means all samples that are wCM
        SingleVsThresh = np.sum(relationT[(wX & wSingle),:][:,(wSingle & wCM)]>(thresh[i]-.001), axis=1)
        CloneVsThresh = np.sum(relationT[(wX & wSingle),:][:,(wClone & wCM)]>(thresh[i]-.001), axis=1)
        UniqueVsThresh = np.sum(relationT[(wCM & wSingle),:][:,(wX & wSingle)] >(thresh[i]-.001), axis=1)
        if (len(SingleVsThresh) > 0) and (verbose > 1):
            print(SingleVsThresh)
            print(CloneVsThresh)
        totalSVTx[i,:] = [len(SingleVsThresh),np.sum(SingleVsThresh),np.sum(SingleVsThresh==0),
                         np.sum((SingleVsThresh+CloneVsThresh)==0)]
        totalCVTx[i,:] = [len(CloneVsThresh),np.sum(CloneVsThresh),np.sum(CloneVsThresh==0),np.sum(CloneVsThresh==1)]
        totalUx[i,:] = [len(UniqueVsThresh),np.sum(UniqueVsThresh>=1)]
        #
        # Do fill comparisons on Ns
        SingleVsThresh = np.sum(relationT[(wN & wSingle),:][:,(wSingle & wCM)]>thresh[i]-.001, axis=1)
        CloneVsThresh = np.sum(relationT[(wN & wSingle),:][:,(wClone & wCM)]>thresh[i]-.001, axis=1)
        UniqueVsThresh = np.sum(relationT[(wCM & wSingle),:][:,(wN  & wSingle)] > thresh[i]-.001, axis=1)
        totalSVTn[i,:] = [len(SingleVsThresh),np.sum(SingleVsThresh),np.sum(SingleVsThresh==0),
                         np.sum((SingleVsThresh+CloneVsThresh)==0)]
        totalCVTn[i,:] = [len(CloneVsThresh),np.sum(CloneVsThresh),np.sum(CloneVsThresh==0),np.sum(CloneVsThresh==1)]
        totalUn[i,:] = [len(UniqueVsThresh),np.sum(UniqueVsThresh>=1)]

        # Divide complete+monogenetic barcodes into two random halves (wR1, wR2)
        # See how many unique barcodes 
        UniqueVsThresh1 = np.sum(relationT[(wCM & wSingle & wR1),:][:,(wR2 & wCM)] >(thresh[i]-.001), axis=1)
        UniqueVsThresh2 = np.sum(relationT[(wCM & wSingle & wR2),:][:,(wR1 & wCM)] >(thresh[i]-.001), axis=1)
        totalU[i,:] = [len(UniqueVsThresh2),np.sum(UniqueVsThresh2==0)]

    if verbose > 0:
        print('')
    if verbose > 2:
        print('Fraction that join a cluster vs threshold:')
        print('Fraction that are no longer unique after filling in another barcode:')
        print('How related are barcodes to highly-repeated clones:','\n')

    #np.sum( np.sum(tBarcode=='X', axis=1) > 2 )

    plt.plot(totalSVTx[:,3]/np.maximum(totalSVTx[:,0],1.), label='barcodes with Xs')
    plt.plot(totalSVTn[:,3]/np.maximum(totalSVTn[:,0],1.), label='barcodes with Ns')
    if 1:
        #relationFull = np.maximum(relationT,relationT.transpose())
        #hist1 = np.histogram(24-relationT[indices[i],:],bins=25,range=xrange)
        #hist2 = np.histogram(24-relationT[indices[i],wCM],bins=25,range=xrange)
        plt.plot(totalU[:,1]/np.maximum(totalU[:,0],1.),'k', label='barcodes with no X/N')
    plt.plot([0,20],[fracUnique,fracUnique],'k:', label='freq. of uniques in rest of pop.')
    plt.title('Fraction of unique barcodes that remain unique up to x SNPs')
    plt.xlabel('# of missing positions')
    plt.legend(bbox_to_anchor=(1, 0.1),loc=4)
    plt.show()

    plt.figure(figsize=(14,6))
    plt.subplot(121)
    plt.plot(totalUx[:,1]/len(UniqueVsThresh), label='matches barcodes with Xs')
    plt.title('Fraction of unique barcodes that become clusters vs threshold')
    plt.xlabel('# of missing positions')

    plt.subplot(122)
    totalgone = np.cumsum(totalUx[:,1])
    plt.plot(1.-totalgone/len(UniqueVsThresh), label='matches narcodes with Xs')
    plt.ylim(0.,1.)
    plt.title('Fraction of unique barcodes remaining unique')
    plt.xlabel('# of missing positions')

    plt.show()

    scipy.special.gamma(5)


    # How related are barcodes to large clone clusters?

    # How frequently do samples occur at some genetic distance from a large cluster?
    relationFull = np.maximum(relationT,relationT.transpose())
    indices,countList = bc.cloneSort(tBarcode,relationFull,1)
    xrange = (0,25)
    #clusterID = 0
    plt.hist(24-relationFull[indices[clusterID],:],bins=25, range=xrange)
    plt.title('Abundance of samples at some genetic distance from clone cluster')
    plt.xlabel('Barcode distance from clone')
    plt.show()

    # Check that cloneSort worked correctly:
    print(len(indices), countList[:20])
    print(relationFull[indices[:60],:][:,indices])

    # What if we only look at complete and monogetic samples?
    # Plot previous histogram first for comparison
    plt.hist(24-relationFull[indices[clusterID],:],bins=25,alpha=.3, range=xrange)
    # Plot new histogram
    plt.hist(24-relationFull[indices[clusterID],wCM],bins=25,range=xrange)
    plt.title('Abundance of samples some distance from cluster - only C+M')
    plt.xlabel('Barcode distance from clone')
    plt.show()

    nClust = 30
    histgData = np.zeros([nClust,3])
    for i in range(nClust):
        hist = np.histogram(24-relationFull[indices[i],:],bins=25,range=xrange)
        histgData[i,0:2] = hist[0][0:2]
        hist = np.histogram(24-relationFull[indices[i],wCM],bins=25,range=xrange)
        histgData[i,2] = hist[0][1]
        
    print('Fraction of near matches that have X or N:',1-np.sum(histgData[:,2])/np.sum(histgData[:,1]))
    print('')

    # Plot instances of barcodes matching or similar to clones
    occurrences(tBarcode,relationT, bc.getDatesOrYear(dfT, option=3),
                clusterID=clusterID, relationMetric=3)

    return 1




'''
Show where and when there is a higher prevalence of Ns and Xs
'''
def whereXN(df0, relation0, autoplot=0, senegal=1, plotX=1, plotN=1,
            debugplot=0):
    
    # Get barcodes and GPS data
    sBarcode = bc.getBarcode(df0)
    sLat = df0['Lat'].values
    sLon = df0['Lon'].values
    
    # Get dates
    sDates = bc.getDatesOrYear(df0, option=1)
    minDate = 733694. 
    maxDate = 736637. 
    sDates = (sDates - minDate)/(maxDate-minDate)*(2015-2008) + 2008

    # Find Ns and Xs
    wN, wX, wCM, wSingle, wClone = findClonesSingles(sBarcode, relation0)
    
    # Set range of GPS coordinates and times to plot
    if autoplot:
        plotrange = [[min(sLon),max(sLon)],
                     [min(sLat),max(sLat)]]
        xrange = (min(sDates),max(sDates))
    elif senegal:
        plotrange = [[-16.96,-16.89],[14.74,14.84]]
        xrange = (2008,2015)
    else:
        plotrange = [[26.,29.],[-18.,-16.]]
        xrange = (2010,2014)

    # Select what kind of barcodes to plot
    if plotX:
        if plotN:
            toplot = wN|wX
            titletag = 'Xs or Ns'
        else:
            toplot = wX
            titletag = 'Xs'
    elif plotN:
        toplot = wN
        titletag = 'Ns'
    else:
        toplot = wCM
        titletag = 'No Xs nor Ns'
    
    # Plot locations of Ns and Xs
    # Only plot entries with valid GPS coords
    wLL = (sLat==sLat) & (sLon==sLon)
    plt.scatter(sLon[toplot&wLL],sLat[toplot&wLL], s=100., c=sDates[toplot&wLL], 
                cmap=plt.cm.rainbow, alpha=0.3,vmin=2008,vmax=2015)
    plt.title('Location of barcode samples with '+titletag)
    plt.xlim(plotrange[0][0],plotrange[0][1])
    plt.ylim(plotrange[1][0],plotrange[1][1])
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    cb = plt.colorbar()
    cb.set_label('time, normalized')

    plt.figure(figsize=(14,6))

    # What fraction of samples in a region have Xs and Ns?
    plt.subplot(121)
    histXN = np.histogram2d(sLon[toplot&wLL], sLat[toplot&wLL], bins=40, range=plotrange)
    histAll = np.histogram2d(sLon[wLL], sLat[wLL], bins=40, range=plotrange)
    plt.imshow((histXN[0].astype(float)/np.maximum(histAll[0],1.).astype(float)).transpose(),origin='lower')
    cb = plt.colorbar()
    cb.set_label('fraction that have '+titletag)

    # How many Xs and Ns total per region?
    plt.subplot(122)
    hdata, xedge, yedge, himage = plt.hist2d(sLon[toplot&wLL], sLat[toplot&wLL], 
                                            bins=[40,40], range=plotrange) #, cmax=200*len(years))
    #plt.xlabel('Longitude')
    #plt.ylabel('Latitude')
    cb = plt.colorbar()
    cb.set_label('total counts')
    plt.show()


    # What if we only look at complete and monogetic samples?
    # Plot previous histogram first for comparison
    if debugplot:
        nbins = 250
        plt.figure(figsize=(14,6))
    else:
        nbins = 50
    plt.hist(sDates,bins=nbins,alpha=.3, range=xrange)
    
    # Plot new histogram
    plt.hist(sDates[toplot],bins=nbins,range=xrange)
    plt.title('Fraction of samples that have '+titletag)
    plt.xlabel('Year')
    plt.show()

    if debugplot:
        hist1, xbins = np.histogram(sDates,bins=nbins,range=xrange)
        hist2, xbins = np.histogram(sDates[toplot],bins=nbins,range=xrange)

        plt.figure(figsize=(14,6))
        plt.plot(xbins[:-1],hist2.astype(float)/hist1.astype(float))
        plt.ylim(0,1.)
        plt.show()

    
    return 1




def seasonalTrends(df,relationM):

    dates = bc.getDatesOrYear(df,option=1)
    print(dates[0] % 365., df['Date'].values[0])
    barcodes = bc.getBarcode(df)
    wN, wX, wCM, wSingle, wClone = findClonesSingles(barcodes, relationM)

    plt.hist(((dates-120) % 365.),bins=48,range=[0,365], alpha=0.3)
    plt.hist(((dates[wN]-120) % 365.),bins=48,range=[0,365])
    plt.show()

    xrange=(0,365)
    hist1, xbins = np.histogram(((dates-120) % 365.),bins=24,range=xrange)
    hist2, xbins = np.histogram(((dates[wN]-120) % 365.),bins=24,range=xrange)

    #print(hist1)
    plt.plot(np.arange(0,12,0.5),hist2.astype(float)/hist1.astype(float))
    plt.show()

    return 1




if __name__ == '__main__':
    print('Hello')
