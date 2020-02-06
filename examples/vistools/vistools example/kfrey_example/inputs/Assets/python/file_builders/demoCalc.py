#********************************************************************************
#
# Steady-state age distribution calculator
#
# Python 3.6.0
#
#********************************************************************************

import numpy               as np
import scipy.sparse        as sp
import scipy.sparse.linalg as la
import scipy.optimize      as opt

from file_builders.demograph_data.mortality  import bEdges   as  mvecX_in

#********************************************************************************

def demoCalc_AgeDist(bval, mvecY, fVec=(12*[1.0])):

  # Control parameters
  max_yr      = 120
  bin_size    =  30
  day_to_year = 365
  
  # Age brackets
  avecY = np.arange(0,max_yr*day_to_year,bin_size)-1

  # Mortality sampling
  mvecX =       [-1] + mvecX_in + [max_yr*day_to_year+1]
  mvecY = [mvecY[0]] + mvecY    + [mvecY[-1]]
  mX    = np.arange(0,max_yr*day_to_year,bin_size)
  mX[0] = 1
  mval  = 1.0 - np.interp(mX,xp=mvecX,fp=mvecY)
  r_n   = mval.size

  # Matrix construction
  BmatRC = (np.zeros(r_n), np.arange(r_n))
  Bmat = sp.csr_matrix(([bval*bin_size]*r_n, BmatRC), shape=(r_n,r_n))
  Mmat = sp.spdiags(mval[:-1]**bin_size, -1, r_n, r_n)
  Dmat = Bmat+Mmat

  # Math
  (gR,popVec) = la.eigs(Dmat,k=1,sigma=1.0)
  gR = np.abs(gR**(float(day_to_year)/float(bin_size)))
  popVec = np.abs(popVec)/np.sum(np.abs(popVec))

  # Apply seasonal forcing
  mVecR = [  -2.0, 30.5, 30.6, 60.5, 60.6, 91.5, 91.6,121.5,
            121.6,152.5,152.6,183.5,183.6,213.5,213.6,244.5,
            245.6,274.5,274.6,305.5,305.6,333.5,335.6,364.5]
  fVec  = np.flipud([val for val in fVec for _ in (0,1)])
  wfVec = np.array([np.mean(np.interp(np.mod(range(val+1,val+31),365),
                           xp=mVecR,fp=fVec)) for val in avecY]).reshape(-1,1)
  popVec = popVec*wfVec/np.sum(popVec*wfVec)

  # Age sampling
  avecY[0] = 0
  avecX = np.clip(np.around(np.cumsum(popVec),decimals=7),0.0, 1.0)
  avecX = np.insert(avecX,0,np.zeros(1))

  return ((gR.tolist())[0],(avecX[:-1]).tolist(),(avecY).tolist())

#end-demoCalc_AgeDist

#********************************************************************************

def demoCalc_GrowTarg(bval, gR_targ=0.0):

  tVal = 1+gR_targ
  boxer = lambda mr,bv: demoCalc_AgeDist(bv,(42*[np.exp(mr)]+12*[1]))[0]-tVal
  s_out = opt.brentq(boxer, a=-20, b=-5, args=(bval))

  return (42*[np.exp(s_out)]+12*[1])

#end-demoCalc_GrowTarg

#********************************************************************************

def demoCalc_SusTarg(ages, probs, sF_targ=0.1):

  tVal  = sF_targ
  boxer = lambda x1: np.sum(np.minimum(np.exp(x1*(ages-0.65)),1.0)*probs)-tVal
  s_out = opt.brentq(boxer, a=-80, b=0)

  return s_out

#end-demoCalc_SusTarg

#********************************************************************************
