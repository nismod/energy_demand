
import numpy as np
import matplotlib.pyplot as plt


def fnx():
    return np.random.randint(5, 50, 10)

y = np.row_stack((fnx(), fnx(), fnx()))
x = np.arange(10)

y1, y2, y3 = fnx(), fnx(), fnx()
'''
fig, ax = plt.subplots()
ax.stackplot(x, y)
plt.show()
'''
fig, ax = plt.subplots()

ax.stackplot(x, y1, y2, y3)
plt.show()


'''import numpy as NP
from matplotlib import pyplot as PLT

# just create some random data
fnx = lambda : NP.random.randint(3, 10, 10)
y = NP.row_stack([fnx(), fnx(), fnx()])   
# this call to 'cumsum' (cumulative sum), passing in your y data, 
# is necessary to avoid having to manually order the datasets
x = NP.arange(10) 
y_stack = NP.cumsum(y, axis=0)   # a 3x10 array

fig = PLT.figure()
ax1 = fig.add_subplot(111)



ax1.fill_between(x, 0, y_stack[0,:], facecolor="green", alpha=1)
ax1.fill_between(x, y_stack[0,:], y_stack[1,:], facecolor="red", alpha=.4)
ax1.fill_between(x, y_stack[1,:], y_stack[2,:], facecolor="#6E5160")

PLT.show()

'''
# IF technology swich fraction is received, technology share within a fuel may be faster
fuel_type_p_by = {'lighting': {0 : 0.0,
                                1 : 0.2,
                                2 : 0.3,
                                3 : 0.5,
                                4 : 0.0,
                                5 : 0.0,
                                6 : 0.5
}}

fuel_type_p_ey = {'lighting': {0 : 0.0,
                                1 : 0.2,
                                2 : 0.3,
                                3 : 0.2,
                                4 : 0.0,
                                5 : 0.0,
                                6 : 0.3
}}
#ASsumption all technologies within one fuel are replaced to the same extent
# Or always take technology with lowest efficiency? 
assump_dict['tech_install'] = {'lighting': {7: 'boilerA'}}
assump_dict['tech_replace'] = {'lighting': {2: 'boilerB'}}
existing stock = {'lighting': 
                                        {0: 'boiler_B',
                                        1: 'boiler_B',
                                        2: 'boiler_B', # Minus fuel. Thus beeing replaced: Calc av end_use replacement eff
                                        3: 'boiler_B',
                                        4: 'boiler_B',
                                        5: 'boiler_B',
                                        6: 'boiler_B',
                                        7: 
                                        },
                            }

#Replacing fraction of fueltype 2 for enduse lighting with boilerA and boiler NEw
assump_dict['tech_install'] = {'lighting': {
                                        0: {},
                                        1: {},
                                        2: {'boilerA': 0.1, 'boilerNEWFUEL': 0.9}}, # share of fuel to switch till enduse, percentage of technologes to use 
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },
                                      }


    tech_replacement_dict = {
                            'lighting': {
                                        0: {},
                                        1: {},
                                        2: {'boilerA': 0.9, 'boilerb': 0.5}}, # Replace 
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },
                                      }

                                          technologies_enduse_by = {
                              'lighting': {
                                        0: {},
                                        1: {},
                                        2: {'boilerA': 0.5, 'boilerb': 0.5}, #As in old model
                                        3: {},
                                        4: {},
                                        5: {},
                                        6: {},
                                        7: {}
                                      },

1. Calculate fraction without fuel switch (assumption about internal shift between technologies)
2. Caclulate fuel switches: I. Amount of new fuel sigmoid
                            II. Update shares of technologies witihn fuel shares of existing technology (save fuels of internal fuel switches)
                            III. Calc Fuel of each technology: Share & eff 

                            Total fuel = (shareA* effA) + (shareB * effB) + fuelswtichesFuelTechA + fuelsWitch TechB

                            IV. Update cy technology shares including switch