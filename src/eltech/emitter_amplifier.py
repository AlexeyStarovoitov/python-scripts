import math
from scipy import signal 

#Given
fc = 1000
wc = 2*math.pi*fc

#High pass 1st order filter
R = 1e5
C = math.sqrt(2)/wc/R
print("High pass 1st order filter (R given):")
print(f'C: {C*1e9} nF')
print(f'R: {R} Ohm')


#Emitter amplifier calculation

#DC nominal workpoint calculation:
Ucc = 9
phi_t = 25e-3
Uke_sat = 1
Ueo = 0.15*Ucc
Uke_min = 2*Uke_sat
Uko = (Ucc+Ueo+Uke_min)/2
Uk_amp = (Ucc - Ueo - Uke_min)/2
Ik_max = 0.1
Iko = Ik_max/2
Re = Ueo/Iko
Rk = (Ucc - Uko)/Iko
betta = 25









