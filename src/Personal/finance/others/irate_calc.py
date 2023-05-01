import numpy as np

So = 200000
Sn = 4000000
delta = 60000
# poly_coeff = [So, delta, delta,delta,delta,delta,delta,delta,delta,delta,delta,delta,delta,delta,delta-Sn]
# t = np.roots(poly_coeff)

# # Direct task: calculate 
# real_lambda = lambda t0: t0.imag == 0 and t0.real > 1
# irate_month = list(filter(real_lambda, t))
# irate_month = irate_month[0].real - 1
# #irate_year = (1 + irate_month)**(1/12) - 1
# irate_year = irate_month[0].real * 12*100

irate_year = 50
pow_base = (1+irate_year/12/100)
print(pow_base)
S_iter = Sn - delta
n = 1
S_iter = 0
while (Sn - S_iter) > 0:
    S_iter = 0
    for i in range(0, n+1):
        if i == 0:
            S_iter = S_iter + delta
        elif i == n:
            S_iter = S_iter + So*(pow_base**i)
        else:
            S_iter = S_iter + delta*(pow_base**i)
    print(S_iter)
    n = n+1
            

print(n)


