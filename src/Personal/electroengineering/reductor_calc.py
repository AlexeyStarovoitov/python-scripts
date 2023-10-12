import math
import pandas as pd
import numpy as np
from enum import Enum

# Given

class GivenParams(Enum):
    ni = 1
    no = 2
    T = 3
    transition_exists=4
    gear_num=5

class GearParams(Enum):
    d=1
    z=2
    m=3
    dw=4
    df=5
    da=6
    bw=7
    betta=8

class TransitionParams(Enum):
    u=1
    aw=2
    ece=3
    exists=4

class ReductorParams(Enum):
    u=1
    Gears=2
    Transitions=3
    ece=4
   
SUBREDUCTOR_NUMBER=3
GEAR_ECE = 0.95
PSY_AB = 0.2

#Given
given_params = {}
given_params[GivenParams.ni] = 500
given_params[GivenParams.no] = 50
given_params[GivenParams.T] = 0
given_params[GivenParams.gear_num] = 5
given_params[GivenParams.transition_exists] = [True, True, False, True]


gear_data = np.zeros(shape=(given_params[GivenParams.gear_num], len(GearParams)), dtype=np.float64)
gears = pd.DataFrame(data = gear_data, index=range(0,given_params[GivenParams.gear_num]), columns=[i for i in GearParams])

transition_data = np.zeros(shape=(given_params[GivenParams.gear_num]-1, len(TransitionParams)), dtype=np.float64)
transitions = pd.DataFrame(data = transition_data, index=range(0,given_params[GivenParams.gear_num]-1), columns=[i for i in TransitionParams])
for i in transitions.index:
    transitions.loc[i, TransitionParams.exists] = given_params[GivenParams.transition_exists][i]



# Part 1 consisting of gears 0-4 calculation

gears_0_2_transition_num = 2
u = given_params[GivenParams.ni]/given_params[GivenParams.no]

u02_geom = math.pow(u, 1/gears_0_2_transition_num)
C01 = 2
u01 = C01*u02_geom
u12 = u/u01
C12 = u12/u02_geom
u34 = u

transitions.loc[0, TransitionParams.u] = u01
transitions.loc[0, TransitionParams.ece] = GEAR_ECE

gears.loc[0, GearParams.z] = 30
gears.loc[1, GearParams.z] = round(gears.loc[0, GearParams.z]*transitions.loc[0, TransitionParams.u], 0)
transitions.loc[0, TransitionParams.u] = gears.loc[1, GearParams.z]/gears.loc[0, GearParams.z]

gears.loc[0, GearParams.betta] = gears.loc[1, GearParams.betta] = 0
gears.loc[0, GearParams.m] = gears.loc[1, GearParams.m] = 4

gears.loc[0, GearParams.d] = gears.loc[0, GearParams.m]*gears.loc[0, GearParams.z]/math.cos(gears.loc[0, GearParams.betta])
gears.loc[0, GearParams.d] = round(gears.loc[0, GearParams.d],0)
gears.loc[1, GearParams.d] = gears.loc[1, GearParams.m]*gears.loc[1, GearParams.z]/math.cos(gears.loc[1, GearParams.betta])
gears.loc[1, GearParams.d] = round(gears.loc[1, GearParams.d],0)
transitions.loc[0, TransitionParams.aw] = (gears.loc[0, GearParams.d]+gears.loc[1, GearParams.d])/2

gears.loc[0, GearParams.da] = gears.loc[0, GearParams.d] + 2*gears.loc[0, GearParams.m]
gears.loc[1, GearParams.da] = gears.loc[1, GearParams.d] + 2*gears.loc[1, GearParams.m]
gears.loc[0, GearParams.df] = gears.loc[0, GearParams.d] - 2.5*gears.loc[0, GearParams.m]
gears.loc[1, GearParams.df] = gears.loc[1, GearParams.d] - 2.5*gears.loc[1, GearParams.m]
gears.loc[0, GearParams.dw] = gears.loc[0, GearParams.d]
gears.loc[1, GearParams.dw] = gears.loc[1, GearParams.d]


gears.loc[0, GearParams.dw] = gears.loc[0, GearParams.d]
gears.loc[1, GearParams.dw] = gears.loc[1, GearParams.d]

gears.loc[0, GearParams.bw] = gears.loc[1, GearParams.bw] = PSY_AB*transitions.loc[0,TransitionParams.aw]


transitions.loc[1, TransitionParams.u] = u12
transitions.loc[1, TransitionParams.ece] = GEAR_ECE


reductor = dict()
reductor[ReductorParams.u] = 
reductor[ReductorParams.Gears] = gears
reductor[ReductorParams.ece] = 0
reductor[ReductorParams.Transitions] = transitions













