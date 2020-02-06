#********************************************************************************
#
# Builds a config.json file to be used as input to the DTK.
#
# Python 3.6.0
#
#********************************************************************************

from io                                     import StringIO   as fstream

from file_builders.writeFlat                import writeDict

from genParams                              import dataDic   as gParam
from simParams                              import dataDic   as pDic

import global_data

#********************************************************************************

def cnfgBuilder():

  cnfgAlts = global_data.CNFG_ALTS

  runYears = gParam['runYears']
  disease  = gParam['disease']


  # Create string buffer
  pDat = fstream()

  # Configuration dictionary
  param_set  = {}


  
  # ***** Generic simulation *****

  # Simulation name; comment field;
  param_set['Config_Name'] = 'kfrey001'
  
  # Simulation type 
  param_set['Simulation_Type'] = 'GENERIC_SIM'

  # Random numbers: seed and generator type
  # Integer: [0, MAX_INT]
  param_set['Run_Number'] = 3
  # Enumerated: "USE_PSEUDO_DES", "USE_LINEAR_CONGRUENTIAL", "USE_AES_COUNTER"
  param_set['Random_Number_Generator_Type']    = 'USE_PSEUDO_DES'
  # Enumerated: "ONE_PER_CORE", "ONE_PER_NODE"
  param_set['Random_Number_Generator_Policy']  = 'ONE_PER_CORE'


  # Timing parameters; implied days 
  # Float: [0.0, 1.0e6]
  param_set['Start_Time']           = 365.0*(runYears[0]-1900)+1
  param_set['Simulation_Duration']  = 365.0*(runYears[1]-runYears[0]+1)
  param_set['Simulation_Timestep']  =   1.0 

  # Termination predicates
  param_set['Enable_Termination_On_Zero_Total_Infectivity'] =  1
  param_set['Minimum_End_Time']                             =  0.0 

  # New stuff
  param_set['Enable_Easy_Way']             =     0
  param_set['Dispersion_Factor']           =     0.0
  param_set['Enable_Old_Way']              =     0
  param_set['Enable_Python_InProcess']     =     1
  param_set['Python_InProcess_Time']       =   list(range(365*(runYears[0]-1900+1), 365*(runYears[1]-1900+2),365))
  param_set['Enable_Vaccinate_Anyway']     =     0

  # Float [   0.0, 250.0]
  if(disease == 'MEASLES'):
    param_set['Maternal_Silent_Boosting_Duration']    =  75.0
  elif(disease == 'RUBELLA'):
    param_set['Maternal_Silent_Boosting_Duration']    =   0.0
  elif(disease == 'INFLUENZA'):
    param_set['Maternal_Silent_Boosting_Duration']    =   0.0
  else:
    raise Exception('Bad disease name: {:s}'.format(disease))
  #end-if
  


  # ***** Parallel computing *****

  # Number of cores
  # Integer: [1, X]
  param_set['Num_Cores'] = 1  

  # Supporting filename
  param_set['Load_Balance_Filename'] = '' 


  # ***** Serialization type *****
  param_set['Serialization_Type'] = 'NONE' 


  # ***** Strain Tracking *****
  param_set['Enable_Strain_Tracking'] = 0



  # ***** Infectivity Descriptions *****
  # Infection skipping
  param_set['Enable_Skipping']      = 0

  # Daily infectiousness contribution
  param_set['Enable_Infectivity_Dispersion']   = 1
  # Float [0.0, 1.0e3]
  if(disease == 'MEASLES'):
    param_set['Base_Infectivity']              = 1.75
  elif(disease == 'RUBELLA'):
    param_set['Base_Infectivity']              = 0.80
  elif(disease == 'INFLUENZA'):
    param_set['Base_Infectivity']              = 0.40
  else:
    raise Exception('Bad disease name: {:s}'.format(disease))
  #end-if

  # Integer [0, MAX_INT]
  param_set['Infection_Updates_Per_Timestep'] = 1


  # Infectivity Multipliers
  # Boolean: 0/1
  param_set['Enable_Infectivity_Scaling']               = 1
  if(param_set['Enable_Infectivity_Scaling']):
    param_set['Enable_Infectivity_Scaling_Boxcar']      = 0
    param_set['Enable_Infectivity_Scaling_Climate']     = 0
    param_set['Enable_Infectivity_Scaling_Density']     = 0
    param_set['Enable_Infectivity_Scaling_Exponential'] = 0
    param_set['Enable_Infectivity_Scaling_Sinusoid']    = 0
  #end-if
    

  # Infectivity Addition
  # Boolean: 0/1
  param_set['Enable_Infectivity_Reservoir'] = 1


  # Incubation descriptions 
  param_set['Incubation_Period_Distribution'] = 'GAUSSIAN_DISTRIBUTION'

  if(disease == 'MEASLES'):
    param_set['Incubation_Period_Gaussian_Mean']    = 10.0
    param_set['Incubation_Period_Gaussian_Std_Dev'] =  2.0
  elif(disease == 'RUBELLA'):
    param_set['Incubation_Period_Gaussian_Mean']    = 17.0
    param_set['Incubation_Period_Gaussian_Std_Dev'] =  2.0
  elif(disease == 'INFLUENZA'):
    param_set['Incubation_Period_Gaussian_Mean']    =  1.0
    param_set['Incubation_Period_Gaussian_Std_Dev'] =  0.3
  else:
    raise Exception('Bad disease name: {:s}'.format(disease))
  #end-if


  # Infection descriptions 
  param_set['Infectious_Period_Distribution'] = 'GAUSSIAN_DISTRIBUTION'
  
  if(disease == 'MEASLES'):
    param_set['Infectious_Period_Gaussian_Mean']    =  8.0
    param_set['Infectious_Period_Gaussian_Std_Dev'] =  2.0
    param_set['Symptomatic_Infectious_Offset']      =  4.0
  elif(disease == 'RUBELLA'):
    param_set['Infectious_Period_Gaussian_Mean']    =  6.0
    param_set['Infectious_Period_Gaussian_Std_Dev'] =  2.0
    param_set['Symptomatic_Infectious_Offset']      =  3.0
  elif(disease == 'INFLUENZA'):
    param_set['Infectious_Period_Gaussian_Mean']    =  5.0
    param_set['Infectious_Period_Gaussian_Std_Dev'] =  1.7
    param_set['Symptomatic_Infectious_Offset']      =  1.0
  else:
    raise Exception('Bad disease name: {:s}'.format(disease))
  #end-if

    
  # Enable multiple infections; REQUIRED
  # Boolean: 0/1
  param_set['Enable_Superinfection']     = 0
  # Integer [0, 1000]
  param_set['Max_Individual_Infections'] = 1 



  # ***** Mortality Descriptions *****

  # Disease death; REQUIRED
  # Boolean: 0/1
  param_set['Enable_Disease_Mortality'] = 0
  
  if(param_set['Enable_Disease_Mortality']):
    # Enumerated: "DAILY_MORTALITY", "MORTALITY_AFTER_INFECTIOUS"
    param_set['Mortality_Time_Course']    = 'DAILY_MORTALITY'
    # Parameters for Infectious -> Disease Death
    # Float: [0.0, 1e3]
    param_set['Base_Mortality']           = 0.0 
  #end-if


  # ***** Immunity Descriptions *****

  # Boolean: 0/1
  param_set['Enable_Immunity']            = 1

  if(param_set['Enable_Immunity']):
    # Immunity factors
    # Multiplier for post-infection suscesptibility
    # Float: [0.0  1.0]   0.0 = Normal Immunity
    param_set['Post_Infection_Acquisition_Multiplier']  = 0.0
    param_set['Post_Infection_Transmission_Multiplier'] = 0.0  
    param_set['Post_Infection_Mortality_Multiplier']    = 0.0 

    # Boolean: 0/1
    param_set['Enable_Immune_Decay']          = 0
    
    if(param_set['Enable_Immune_Decay']): 
      # Time span until eligible Recovered -> Susceptible transitions
      # Float: [0.0, 1.0e5]
      param_set['Acquisition_Blocking_Immunity_Duration_Before_Decay']  = 0.0
      param_set['Transmission_Blocking_Immunity_Duration_Before_Decay'] = 0.0 
      param_set['Mortality_Blocking_Immunity_Duration_Before_Decay']    = 0.0
      
      # Rate for Recovered -> Susceptible transitions
      # Float: [0.0, 1.0e3]
      param_set['Acquisition_Blocking_Immunity_Decay_Rate']  = 1.0e-3
      param_set['Mortality_Blocking_Immunity_Decay_Rate']    = 1.0e-3  
      param_set['Transmission_Blocking_Immunity_Decay_Rate'] = 1.0e-3
    #end-if
  #end-if



  # ***** Rate of Sample parameters *****
  
  # Enumerated: "TRACK_ALL", "FIXED_SAMPLING",
  #             "ADAPTED_SAMPLING_BY_IMMUNE_STATE"
  #             "ADAPTED_SAMPLING_BY_POPULATION_SIZE",
  #             "ADAPTED_SAMPLING_BY_AGE_GROUP",
  #             "ADAPTED_SAMPLING_BY_AGE_GROUP_AND_POP_SIZE",
  param_set['Individual_Sampling_Type'] = 'ADAPTED_SAMPLING_BY_IMMUNE_STATE'  
    
  if(param_set['Individual_Sampling_Type'] == 'ADAPTED_SAMPLING_BY_IMMUNE_STATE'):
    # Float: (0.0, 1.0]
    param_set['Base_Individual_Sample_Rate']       =  1.0  
    # Float: (0.0, 1.0]
    param_set['Relative_Sample_Rate_Immune']       =  1.0e-2
    # Float: [0.0, 1.0]
    param_set['Immune_Threshold_For_Downsampling'] =  1.0e-5
    # Float: [0.0, 1.0]
    param_set['Immune_Downsample_Min_Age']         =  0.0
    # Float: [1.0, MAX_FLOAT]
    param_set['Immune_Downsample_Min_Agents']      = 20.0
  #end-if



  # ***** Reporting / Output Parameters *****

  # Custom reporter filename
  param_set['Custom_Reports_Filename']       = 'dllc.json'
  
  # Boolean: 0/1
  param_set['Enable_Default_Reporting']              = 0
  param_set['Enable_Demographics_Reporting']         = 0
  param_set['Enable_Property_Output']                = 0
  param_set['Enable_Spatial_Output']                 = 0
  param_set['Report_Event_Recorder']                 = 0
  param_set['Report_Coordinator_Event_Recorder']     = 0
  param_set['Report_Node_Event_Recorder']            = 0
  param_set['Report_Surveillance_Event_Recorder']    = 0



  # ***** Logging Parameters *****
  
  # Enumerated: "ERROR", "WARNING", "INFO", "DEBUG", "VALID"
  #   Default is INFO for all
  #param_set['logLevel_Memory'] = 'DEBUG'



  # ***** Intervention parameters *****

  # Functionality flag
  # Boolean: 0/1
  param_set['Enable_Interventions'] = 1  

  if(param_set['Enable_Interventions']):
    # Supporting filename
    param_set['Campaign_Filename'] = 'camp.json'
  #end-if



  # ***** Demographic parameters *****
  
  # Filenames; >=1 REQUIRED
  param_set['Demographics_Filenames']       = ['demo.json']  

  # Boolean: 0/1                   
  param_set['Enable_Demographics_Builtin']  = 0
  
  # Size of Node (Degrees Lat/Long)
  # Float: [4.167e-3, 90.0]
  param_set['Node_Grid_Size']               = 4.167e-3
  
  # Enumerated: "USE_INPUT_FILE", "FIXED_SCALING"
  param_set['Population_Scale_Type']        = 'USE_INPUT_FILE'

  # Enumerated: "DISTRIBUTION_OFF", "DISTRIBUTION_SIMPLE",
  #             "DISTRIBUTION_COMPLEX"
  param_set['Age_Initialization_Distribution_Type'] = 'DISTRIBUTION_COMPLEX'

  # Boolean: 0/1
  param_set['Enable_Vital_Dynamics'] = 1

  if(param_set['Enable_Vital_Dynamics']):
    # Boolean: 0/1    
    param_set['Enable_Birth']        = 1

    if(param_set['Enable_Birth']):
      # Float: [0.0 MAX_FLOAT]
      param_set['x_Birth']           = 1.0

      # Boolean: 0/1  
      param_set['Enable_Maternal_Protection'] = 1
  
      if(param_set['Enable_Maternal_Protection']):
        # Susceptibility type and distribution
        param_set['Susceptibility_Type'] = 'BINARY'
        param_set['Maternal_Protection_Type'] = 'SIGMOID'
    
        # BASE *= 1/(1+EXP((HALFMAXAGE-AGE_IN_DAYS)/STEEPFAC))
        if(disease == 'MEASLES'):
          param_set['Maternal_Sigmoid_SteepFac']    =  50.0
          param_set['Maternal_Sigmoid_HalfMaxAge']  = 150.0
          param_set['Maternal_Sigmoid_SusInit']     =   0.0
        elif(disease == 'RUBELLA'):
          param_set['Maternal_Sigmoid_SteepFac']    =  30.0
          param_set['Maternal_Sigmoid_HalfMaxAge']  =  90.0
          param_set['Maternal_Sigmoid_SusInit']     =   0.0
        elif(disease == 'INFLUENZA'):
          param_set['Maternal_Sigmoid_SteepFac']    =   1.0
          param_set['Maternal_Sigmoid_HalfMaxAge']  =- 90.0
          param_set['Maternal_Sigmoid_SusInit']     =   0.0
        else:
          raise Exception('Bad disease name: {:s}'.format(disease))
        #end-if
      #end-if

      # Enumerated: "NONE", "FIXED_BIRTH_RATE", "POPULATION_DEP_RATE",
      #             "DEMOGRAPHIC_DEP_RATE", "INDIVIDUAL_PREGNANCIES"
      #             "INDIVIDUAL_PREGNANCIES_BY_URBAN_AND_AGE"
      #             "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR"
      param_set['Birth_Rate_Dependence'] = 'POPULATION_DEP_RATE' 

      # Enumerated: "NONE", "SINUSOIDAL_FUNCTION_OF_TIME",
      #             "ANNUAL_BOXCAR_FUNCTION"                                 
      param_set['Birth_Rate_Time_Dependence'] = 'NONE'
    #end-if

    # Boolean: 0/1  
    param_set['Enable_Natural_Mortality'] = 1
  
    if(param_set['Enable_Natural_Mortality']):
      # Enumerated: "NONDISEASE_MORTALITY_OFF",
      #             "NONDISEASE_MORTALITY_BY_AGE_AND_GENDER",
      #             "NONDISEASE_MORTALITY_BY_YEAR_AND_AGE_FOR_EACH_GENDER"
      param_set['Death_Rate_Dependence'] = 'NONDISEASE_MORTALITY_BY_AGE_AND_GENDER'

      # Float: [0.0 MAX_FLOAT]
      param_set['x_Other_Mortality'] = 1.0
    #end-if

    param_set['Enable_Demographics_Birth']                   = 0
    param_set['Enable_Demographics_Gender']                  = 0
    param_set['Enable_Maternal_Infection_Transmission']      = 0
    param_set['Enable_Heterogeneous_Intranode_Transmission'] = 0
    param_set['Enable_Initial_Prevalence']                   = 0
    
    param_set['Enable_Initial_Susceptibility_Distribution']  = 1

    if(param_set['Enable_Initial_Susceptibility_Distribution']):
      # Initial immunity distribution
      # Enumerated: "DISTRIBUTION_OFF", "DISTRIBUTION_SIMPLE", 
      #             "DISTRIBUTION_COMPLEX"
      param_set['Susceptibility_Initialization_Distribution_Type'] = \
                                           'DISTRIBUTION_COMPLEX'
    #end-if
  #end-if



  #  ***** Migration / Spatial parameters *****
  
  # Migration types
  # Enumerated: "NO_MIGRATION", "FIXED_RATE_MIGRATION",
  param_set['Migration_Model'] = 'NO_MIGRATION'


    
  # ********************************
  
  # Update parameter dictionary 
  for keyval in cnfgAlts:
    param_set[keyval] = cnfgAlts[keyval]
  #end-if

  # Easy way simplifications
  if(param_set['Enable_Easy_Way']):
    param_set['Incubation_Period_Gaussian_Std_Dev'] =  0.001
    param_set['Infectious_Period_Gaussian_Std_Dev'] =  0.001
  #end-if

  # Archive global parameters
  global_data.CONFIG = param_set

  # End file construction
  writeDict(pDat, {'parameters': param_set})
  pDatStr = pDat.getvalue()
    
  return pDatStr

#end-cnfgBuilder

#********************************************************************************
