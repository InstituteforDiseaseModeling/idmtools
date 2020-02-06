#********************************************************************************
#
# Python 3.6.0
#
#********************************************************************************

import numpy    as np
import pandas   as pd

#********************************************************************************

CNFG_ALTS    = dict()
DEMO_ALTS    = list()

CONFIG       = dict()
DEMOGRAPHICS = dict()
NODE_CODE    = dict()

SIA_LIST     = list()
SIA_RECORD   = np.zeros(0)

REP_COUNTER  = dict()

df           = pd.DataFrame()
neighbors    = dict()
province     = dict()
region       = dict()
riskmap      = False

#********************************************************************************
