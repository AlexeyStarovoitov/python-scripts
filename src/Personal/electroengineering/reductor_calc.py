import math
import pandas as pd
import numpy as np
from enum import Enum
import copy

# Given

class GivenParams(Enum):
    ni = 1
    no = 2
    k = 3

class GearParams(Enum):
    d=1
    z=2
    m=3
    dw=4
    df=5
    da=6
    bw=7
    betta=8
    alpha=9
    x = 10
    b1 = 11
    b2 = 12

class TransitionParams(Enum):
    u=1
    aw=2
    ece=3

class ReductorParams(Enum):
    u=1
    Gears=2
    Transitions=3
    ece=4
   

GEAR_ECE = 0.95
PSY_AB = 0.05
ALPHA = 20
BETTA = 0
SUBREDUCTOR_NUMBER = 2
NOMINAL_DIMENSIONS_FILENAME = "normal_dimensions.txt"
REDUCTOR_RESULT_PARAMETERS_FILENAME = "reductor_parameters.txt"
Z0 = 20
K_DEG2RAD = math.pi/180
DIMENSION_TOLERANCE=2
M0 = 1
X0 = 0
DELTA_B = 5
NI=100
NO = 25

#Given
reductor_given_params = []

for i in range(SUBREDUCTOR_NUMBER):
    given_params = {}
    given_params[GivenParams.ni] = NI
    given_params[GivenParams.no] = NO
    given_params[GivenParams.k] = 2 if i == 0 else 1
    reductor_given_params.append(given_params)

nominal_dimensions = np.loadtxt(fname=NOMINAL_DIMENSIONS_FILENAME, delimiter=",", dtype=int)

def dimension_alignment(d):
    d = int(round(d, 0))
    
    for nd in nominal_dimensions:
        if nd == d:
            return nd
    
    for nd in nominal_dimensions:
        if abs(nd-d) <= DIMENSION_TOLERANCE:
            return  nd
    
    return d


def gears_init(gears, i):
    gears.loc[i, GearParams.z] = Z0
    gears.loc[i, GearParams.m] = M0
    gears.loc[i, GearParams.alpha] = ALPHA
    gears.loc[i, GearParams.betta] = BETTA
    gears.loc[i, GearParams.x] = X0

def gears_calculate_params(gears, i):
    gears.loc[i, GearParams.d] = gears.loc[i, GearParams.m]*math.pi*gears.loc[i, GearParams.z]
    gears.loc[i, GearParams.d] = dimension_alignment(gears.loc[i, GearParams.d])
    xm = gears.loc[i, GearParams.m]*gears.loc[i, GearParams.x]
    gears.loc[i, GearParams.dw] = gears.loc[i, GearParams.d] - xm
    gears.loc[i, GearParams.da] = gears.loc[i, GearParams.d] + 2*xm + 2*gears.loc[i, GearParams.m]
    gears.loc[i, GearParams.df] = gears.loc[i, GearParams.d] + 2*xm - 2.5*gears.loc[i, GearParams.m]

def reductor_parameters_calculation(ni, no, k):

    gear_data = np.zeros(shape=(k+1, len(GearParams)), dtype=np.float64)
    gears = pd.DataFrame(data = gear_data, index=range(0,k+1), columns=[i for i in GearParams])

    transition_data = np.zeros(shape=(k, len(TransitionParams)), dtype=np.float64)
    transitions = pd.DataFrame(data = transition_data, index=range(0,k), columns=[i for i in TransitionParams])
    

    u = ni/no
    u_geom = math.pow(u, 1/k)
    
    c = []
    for i in range(k):
        c.append(k-i)
    
    u_trans = []
    for i in range(k):
        u_trans.append(c[i]*u_geom if i != (k-1) else u/np.prod(u_trans))
        
        if i == 0: 
            gears_init(gears, i)
            gears_calculate_params(gears, i)
        
        gears_init(gears, i+1)
        gears.loc[i+1, GearParams.z] = int(round(u_trans[i]*gears.loc[i, GearParams.z], 0))
        u_trans[i] = gears.loc[i+1, GearParams.z] / gears.loc[i, GearParams.z]
        gears_calculate_params(gears, i+1)

        transitions.loc[i, TransitionParams.u] = u_trans[i]
        transitions.loc[i, TransitionParams.ece] = GEAR_ECE
        transitions.loc[i, TransitionParams.aw] = (gears.loc[i, GearParams.d] + gears.loc[i+1, GearParams.d])/2

        if i == 0: 
            gears.loc[i, GearParams.bw] = int(round(PSY_AB* transitions.loc[i, TransitionParams.aw],0))
            gears.loc[i, GearParams.bw] = dimension_alignment(gears.loc[i, GearParams.bw])
            gears.loc[i, GearParams.b1] = dimension_alignment(gears.loc[i, GearParams.bw])
            gears.loc[i, GearParams.b2] = dimension_alignment(gears.loc[i, GearParams.b1]) + DELTA_B


        gears.loc[i+1, GearParams.bw] = gears.loc[i, GearParams.bw]
        gears.loc[i+1, GearParams.b1] = gears.loc[i, GearParams.b1]
        gears.loc[i+1, GearParams.b2] = gears.loc[i, GearParams.b2]
    
    return (np.prod(u_trans), gears, transitions)


        
if __name__ == "__main__":
    
    reductor = []
    for given_params in reductor_given_params:
        sub_reductor = dict()
        (sub_reductor[ReductorParams.u], sub_reductor[ReductorParams.Gears], sub_reductor[ReductorParams.Transitions]) = reductor_parameters_calculation(given_params[GivenParams.ni], given_params[GivenParams.no], given_params[GivenParams.k])
        eces = [sub_reductor[ReductorParams.Transitions].loc[i,TransitionParams.ece] for i in sub_reductor[ReductorParams.Transitions].index]
        sub_reductor[ReductorParams.ece] = np.prod(eces)

        reductor.append(sub_reductor)
    
    with open(REDUCTOR_RESULT_PARAMETERS_FILENAME, "w") as f:
        f.write("Reductor calculation results:\n")
        for i in range(len(reductor)):
            f.write(f"Subreductor {i}:\n")
            f.write("Given:\n")
            f.write(str(reductor_given_params[i]))
            f.write("Results:\n")
            f.write(f"Gears:\n{reductor[i][ReductorParams.Gears].to_string()}\n")
            f.write(f"Transitions:\n{reductor[i][ReductorParams.Transitions].to_string()}\n")
            f.write(f"Efficiency: {100*reductor[i][ReductorParams.ece]}%\n")
            f.write("\n")
        f.close()

    

    

    
    


















