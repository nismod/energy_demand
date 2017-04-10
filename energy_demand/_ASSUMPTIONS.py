import numpy as np
from random import randint
def eff_h(input):
    out = np.zeros((365,24))

    for i in range(365):
        for j in range(24):
            out[i][j] = input
    return out

def get_heatpump_eff(data_external, m, b, t_base=15.5):
        """ Calculate efficiency according to temperatur difference of base year """
        temp_h_y2015 = data_external
        
        out = np.zeros((365,24))

        for i, day in enumerate(temp_h_y2015): #TODO: do not take base year but meteorological year !!
            for j, h_temp in enumerate(day):

                if t_base < h_temp:
                    h_diff = 0
                else:
                    if h_temp < 0: #below zero temp
                        h_diff = t_base + abs(h_temp)
                    else:
                        h_diff = abs(t_base - h_temp)

                out[i][j] = m * h_diff + b

        return out


temp = np.zeros((365,24))
for i, d in enumerate(temp):
    temp[i] = [4, 33, -5, 4, 4, 5, 6, 6, 6, 7, 8, 9, 10, 9, 8, 7, 7, 7, 6, 5, 4, 3, 2, 1]


tot_fuel = 1000 #tons of fouel

#verbreitung
gas_share = 0.5
hp_share = 0.5



shape = np.zeros(365,1)
for i in shape:
    shape[i] = randint(0,1000)
for i in shape_gas_d:
    shape[i] = shape[i] / np.sum(shape)



hp_eff = get_heatpump_eff(temp, -0.05, 2)
hp_eff = eff_h(0.5)

gas_eff = eff_h(0.5)

tot_f = (gas_share / np.sum(gas_eff)) + (hp_share / np.sum(hp_eff))
print(gas_eff[0])
print(hp_eff[0])
print("Anteil gas: " + str(tot_fuel * (1 / tot_f) * (gas_share / np.sum(gas_eff))))
print("Anteil hp: " + str(tot_fuel *(1 / tot_f) * (hp_share / np.sum(hp_eff))))
