import numpy as np
from math import pi, ceil

'''
Source articles:
https://radiolamp.net/news/385-sxemy-prostyx-priemnikov-na-odnom-tranzistore.html
https://dzen.ru/a/X-xjuZgBSU7YAML4
'''

#Given:

fmin = 60e6
fmax = 120e6
Cmin = 4e-12
Cmax = 20e-12

L = 1/((2*pi*fmax)**2 * Cmin)
fmin_corr = 1/(2*pi*(L*Cmax)**0.5)

print(f'L: {L*10**6} uH')
print(f"fmin: {fmin_corr /10**6} MHz")
print(f"fmax: {fmax /10**6} MHz")


'''
Coil parameters calculation
Reference:
https://radiostorage.net/1609-raschet-induktivnosti-katushek-odnoslojnyh.html

L = (Dn)^2/(45D+100nd)/10^6

Given:
L - coil inductance, H;
D - coil deiameter, m;
d - wire diameter, m.

Needed to be found:
n - number of windings.

Equation to solve:
10^(4)*D^2*n^2 - 10^(2)*dL*n - 45*DL = 0 

'''
D = 1e-2
d = 1.5e-3
uo = 4*pi*10**(-7)
#coeff = [10**4*D**2, -(10**(2))*d*L, -45*D*L]
coeff = [10*pi*uo*D**2, -40*d*L, -18*D*L]
n_roots = np.roots(coeff)
n = filter(lambda x: x > 0, n_roots)
n = ceil(min(n))
print(f"Number of windings: {n}")

