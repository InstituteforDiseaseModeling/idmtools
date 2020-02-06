#*******************************************************************************
#
# General build options for simulations
#
# Python 3.6.0
#
#*******************************************************************************

import numpy as np

#*******************************************************************************

def genBuilder():

  revParams = { 'locFlag':                         False ,
                'iterMax':                             1 ,

                'pNames':                     ['param1'] ,
                'pLogs':                         [False] ,
                'pRanges':                   [[0.0,1.0]] ,

                'progName':         'Release_2p21_v1-03' ,
                'pyinproc_ver':                   'NONE' ,
                'disease':                     'MEASLES' ,
                
                'repNames':                           [] ,
                'repNMFR':                             0 ,
                'repStart':                         2000 , 

                'nSampOpt':                            0 ,
                'nSampRand':                          25 ,
                
                'qPriority':                           5 ,
                'qTarget':                'EMOD_32cores' ,
                'qCluster':                   'Belegost' ,

                'bldName':                   'BUCHAREST' ,
                'bldDepth':                            1 , 
               
                'runYears':                 [1900, 1901] ,
                'agentRat':                            1 ,
                'exInfect':                            0 ,

                'dataSets':                          [ ] }

  return revParams

#end-genBuilder


#*******************************************************************************

def dtkBuilder(pDic = {}):

  np.random.seed(100000*pDic['iter'] + pDic['simIdx'])

  revParams = { 'genAlts':
                { 'exInfect':                             0.05  ,
                  'exInfectPow':                          1.00  ,
                  'network_coeff':                        2e-4  } ,

                'cnfgAlts':
                { 'Run_Number':                      pDic['simIdx']+3   , 
                  'Base_Infectivity':                             0.360 ,
                  'Incubation_Period_Gaussian_Mean':              2.4   ,
                  'Infectious_Period_Gaussian_Mean':              7.0   ,
                  'Enable_Infectivity_Dispersion':                0     ,
                  'Enable_Vital_Dynamics':                        0     ,
                  'Enable_Initial_Susceptibility_Distribution':   0     ,
                  'Enable_Natural_Mortality':                     0     ,
                  'Enable_Maternal_Protection':                   0     ,
                  'Age_Initialization_Distribution_Type' :
                                                   'DISTRIBUTION_OFF'   ,
                  'Enable_Python_InProcess':                      0     ,
                  'Enable_Spatial_Output':                        1     ,
                  'Spatial_Output_Channels':     ['Disease_Deaths']     ,
                  'Enable_Default_Reporting':                     1     ,
                  'Individual_Sampling_Type':           'TRACK_ALL'     ,
                  'Enable_Disease_Mortality':                     1     ,
                  'Mortality_Time_Course':        'DAILY_MORTALITY'     ,
                  'Base_Mortality':                             2*0.041 ,
                  'Enable_Termination_On_Zero_Total_Infectivity': 0     } ,
                
               
                'demoAlts':
                [ # Heterogeneity
                  { 'LocName' :                        'BUCHAREST' ,
                    'VarName' :    'InfectivityReservoirStartTime' ,
                    'ModType' :                          'REPLACE' ,
                    'Value'   :                                130 } ,
                  # Heterogeneity
                  { 'LocName' :                        'BUCHAREST' ,
                    'VarName' :      'InfectivityReservoirEndTime' ,
                    'ModType' :                          'REPLACE' ,
                    'Value'   :                                365 } ,
                ]
              }

  
  return revParams

#end-DTKBuilder

#*******************************************************************************
