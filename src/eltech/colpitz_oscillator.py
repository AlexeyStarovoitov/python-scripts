import numpy as np
import pandas as pd


Us = 8
Uce_m = 8
Ic_max = 0.8
he = 250
Ube_max = 5
Ube_nom = 0.7

k_strength = 1.2
k_us_be_min = Us/Ube_max
R1 = 1000
R2max = R1/(k_us_be_min-1)
R2 = R2max/k_strength
Ub = Us*R2/(R1+R2)

Ib_max = Ic_max/he
Rob = (Ub-Ube_nom)/Ib_max


print(f"R1: {R1}")
print(f"R2: {R2}")
print(f"Rob: {Rob}")


