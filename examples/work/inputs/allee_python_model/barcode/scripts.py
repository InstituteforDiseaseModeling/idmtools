import os
import warnings
import time

import json
import argparse

import numpy as np
import pandas

import barcode.barcode as bc
import barcode.model as bm
import barcode.modelfit as bmf
import barcode.data as bdata

'''
Wrappers for commands and batch scripts from shell
'''

'''
Function for running fits from command line
'''


def runFits(fname='', customGrid=0, gridFile='',
            agentbased=0, outpath=''):
    # parser = argparse.ArgumentParser(description='Run fits')
    # parser.add_argument('--fname', type=str,
    #                     help='output file name')
    # parser.add_argument('--gridfile', type=str,
    #                     help='input file name for custom grid')
    # parser.add_argument('-cg', '--customgrid', action='store_true',
    #                     help='use custom grid')
    # parser.add_argument('--nsim', type=int,
    #                     help='number of sims to run per sample')
    # parser.add_argument('-ab','--agentbased', action='store_true',
    #                     help='set to agent-based mode')
    # args = parser.parse_args()
    # if args.fname:
    #     fname = args.fname
    # if args.gridfile:
    #     gridFile = args.gridfile
    #     customGrid=1
    # if args.customgrid:
    #     customGrid=1
    # if args.nsim:
    #     bmf.nSims = args.nsim
    # if args.agentbased:
    #     bmf.agentbased = 1
    # else:
    #     bmf.agentbased = 0

    if gridFile:
        customGrid = 1
    if customGrid:
        customGrid = 1
    if agentbased:
        bmf.agentbased = 1
    else:
        bmf.agentbased = 0
    timeTag = str(time.time())
    if fname == '':
        fname = timeTag + '.json'
        npFname = timeTag + '.npy'
        sFname = timeTag + '_settings.json'
    else:
        withoutExt = os.path.splitext(fname)[0]
        fname = withoutExt + '.json'
        npFname = withoutExt + '.npy'
        sFname = withoutExt + '_settings.json'

    print('Starting fit')
    if customGrid:
        setGrid(gridFile)
    samples, logArray, statArray = bmf.fitModel()

    current_path = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_path, '..', 'output')
    if len(outpath) > 0:
        output_path = outpath

    file = os.path.join(output_path, npFname)
    np.save(file, logArray)
    file = os.path.join(output_path, fname)
    bdata.saveFits(file, samples, logArray, statArray)

    file = os.path.join(output_path, sFname)
    bmf.setSettings()
    bmf.saveSettings(file)
    print('End of run')

    return samples, logArray, statArray


def getNewTimeDivs():
    t0 = 732150
    t1 = 735100
    div1 = (t1 - t0) * 0.15 + t0
    div2 = (t1 - t0) * 0.5 + t0
    div3 = (t1 - t0) * 0.75 + t0
    print(div1, div2, div3)
    print(2013 * 365, 2016 * 365)
    t1 = 736385
    print((div1 - t0) / (t1 - t0), (div2 - t0) / (t1 - t0), (div3 - t0) / (t1 - t0), (735100 - t0) / (t1 - t0))
    return 1


### TO DO: probably wanna combine these with fxns in modelfit.py?
def genGrids(fname='', verbose=0):
    N = 10
    nSamps = N * N * N * N
    numR0 = 4

    if numR0 == 3:
        nParams = 7
    elif numR0 == 4:
        nParams = 8
    else:
        nParams = bmf.nParams
    dGrid = np.zeros([nSamps, nParams])  # default grid

    # Set up param values for R_0
    # R_0[0:3]
    rateVals1 = np.reshape(np.repeat(np.reshape(np.arange(N) * 0.3 + 0.3, [1, N]), N * N * N, axis=0),
                           [nSamps])
    rateVals2 = np.repeat(np.arange(N) * 0.3 + 0.3, N)
    rateVals2 = np.reshape(np.repeat(np.reshape(rateVals2, [1, N * N]), N * N, axis=0), [nSamps])
    rateVals3 = np.repeat(np.arange(N) * 0.3 + 0.3, N * N)
    rateVals3 = np.reshape(np.repeat(np.reshape(rateVals3, [1, N * N * N]), N, axis=0), [nSamps])
    # R_0[3] (optional)
    rateVals4 = np.repeat(np.arange(N) * 0.3 + 0.3, N * N * N)

    # Fill param grid
    if numR0 == 3:
        dGrid[:, 0] = rateVals1  # R_0[0,2]
        dGrid[:, 1] = rateVals2  # R_0[1]
        dGrid[:, 2] = rateVals3
        dGrid[:, 3] = 0.18  # rho
        dGrid[:, 4] = np.repeat(np.arange(N) * 0.005 + 0.005, N * N * N)  # deathRatePerDay (previously 0.02)
        dGrid[:, 5] = 0.04  # importRate   (previously 0.03)
        dGrid[:, 6] = 1.  # importNum
    else:
        dGrid[:, 0] = rateVals1  # R_0[0,2]
        dGrid[:, 1] = rateVals2  # R_0[1]
        dGrid[:, 2] = rateVals3
        dGrid[:, 3] = rateVals4
        dGrid[:, 4] = 0.18  # rho
        dGrid[:, 5] = np.repeat(np.arange(N) * 0.005 + 0.005, N * N * N)  # deathRatePerDay (previously 0.02)
        dGrid[:, 6] = 0.04  # importRate   (previously 0.03)
        dGrid[:, 7] = 1.  # importNum

    if verbose > 1:
        print(dGrid)

    current_path = os.path.dirname(os.path.abspath(__file__))
    if fname == '':
        fname = str(time.time())

    nBatch = N * N * N  # 5
    for i in range(nBatch):
        # dGrid[:,3] = float(i)*.01
        bdata.saveJson(os.path.join(current_path,
                                    '..', 'input',
                                    fname + '_' + str(i) + '.json'),
                       dGrid[(i * N):(i * N + N), :].tolist())
    return dGrid


def genGrids0(fname=''):
    N = 10
    nSamps = N * N
    dGrid = np.zeros([nSamps, bmf.nParams])  # default grid
    rateVals1 = np.reshape(np.repeat(np.reshape(np.arange(N) * 0.1 + 1.3, [1, N]), N, axis=0),
                           [nSamps])
    rateVals2 = np.repeat(np.arange(N) * 0.1 + 1.3, N)
    dGrid[:, 0] = rateVals1  # R_0[0,2]
    dGrid[:, 1] = rateVals2  # R_0[1]
    dGrid[:, 2] = 0.18  # rho
    dGrid[:, 3] = 0.02  # deathRatePerDay
    dGrid[:, 4] = 0.04  # importRate   (previously 0.03)
    dGrid[:, 5] = 1.  # importNum

    current_path = os.path.dirname(os.path.abspath(__file__))
    if fname == '':
        fname = str(time.time())

    nBatch = 5
    for i in range(nBatch):
        dGrid[:, 3] = float(i) * .01
        bdata.saveJson(os.path.join(current_path,
                                    '..', 'input',
                                    fname + '_' + str(i) + '.json'),
                       dGrid.tolist())
    return 1


def setGrid(gridFile=''):
    if gridFile != '':
        print('Using custom grid...')
        bmf.__grid__ = bdata.getGrid(gridFile)
        bmf.nSamps = len(bmf.__grid__)
    else:
        bmf.__grid__ = np.zeros([2, bmf.nParams])
        bmf.__grid__[:, 0] = 1.9
        bmf.__grid__[:, 1] = 1.4
        bmf.__grid__[:, 2] = 1.9
        bmf.__grid__[:, 3] = 0.02  # 0.01
        bmf.__grid__[:, 4] = 0.02  # np.repeat(np.arange(N)*0.05, N)
        bmf.__grid__[:, 5] = 0.03
        bmf.__grid__[:, 6] = 1.
        bmf.nSamps = len(bmf.__grid__)
    return 1


def readBatch(path, fname, maxRuns=100, sampsPerRun=10):
    dirlist = [x[0] for x in os.walk(path)]
    outputs = []
    # outputDF = pandas.DataFrame(index=range(maxRuns),columns=['samples','logLArray','statArray','file'])
    outputDF = pandas.DataFrame(index=range(maxRuns * sampsPerRun),
                                columns=['samples', 'logLArray', 'statArray'])
    print(len(outputDF))

    for directory in dirlist:
        file = os.path.join(directory, fname)
        if os.path.isfile(file):
            #
            config = bdata.readJson(os.path.join(directory, 'config.json'))
            infile = config['config'][0]['infile']
            runNum = int(infile.split('.')[-2].split('_')[-1])
            # print(runNum)
            #
            data = bdata.readJson(file)
            outputs += [data]
            tempDF = pandas.DataFrame.from_dict(data)
            # print(tempDF)
            # print(outputDF.loc[(runNum*10):((runNum+1)*10)])
            # print(runNum*sampsPerRun,(runNum+1)*sampsPerRun)
            outputDF.loc[(runNum * sampsPerRun):((runNum + 1) * sampsPerRun - 1)] = tempDF.values
            # outputDF.loc[(runNum*10):((runNum+1)*10),['file']] = runNum

    return outputs, outputDF
