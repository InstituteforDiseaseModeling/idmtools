import os
import warnings
import time

import json
import argparse

import numpy as np
import pandas
# import sys
# dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(dir_path, "barcode"))
import barcode.barcode as bc
import barcode.model as bm
import barcode.modelfit as bmf
import barcode.data as bdata
import barcode.scripts as bs



'''
Wrapper for launching python command without installig package.
This is intended for dtk interfacing
'''


'''
In general scripts should be run after installing the barcode package
and using the recommended command-line syntax.
Otherwise, python will not interpret the directory structure correctly.
This is more of a hack to make this package work with DTK.
'''
if __name__ == "__main__":
    print('Starting run_dtk_sweep script from command line...')
    if 0:
        #bmf.nSims = 3
        #pathname = os.path.dirname(os.path.abspath(__file__))
        #pathname= os.path.abspath(os.path.join(pathname, '..'))
        #samples, logArray, statArray = bs.runFits(fname='shortExampleRun.json',
        #                                          customGrid=1,
        #                                          setPath=pathname)
        None

    else:
        pathname = os.path.dirname(os.path.abspath(__file__))
        pathname = os.path.abspath(os.path.join(pathname, '..'))
        with open("config.json", 'r') as fp:
            config = json.load(fp)
            parameters = config["parameters"]
            print(config)
        
        fname = parameters['fname']
        customGrid = parameters['customGrid']
        outpath = os.path.abspath(os.path.join(pathname,'output'))
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        infile = parameters['infile']

        pathname = os.path.dirname(os.path.abspath(__file__))
        gridfile = os.path.abspath(os.path.join(pathname, 'input',infile))

        nsims = parameters['nsims']
        if nsims > 1:
            bmf.nSims = nsims
        bs.runFits(fname=fname,customGrid=customGrid,gridFile=gridfile,outpath=outpath)

    print('End of script')

