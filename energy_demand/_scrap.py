
'''
1. Calculate fraction without fuel switch (assumption about internal shift between technologies)
2. Caclulate fuel switches: I. Amount of new fuel sigmoid
                            II. Update shares of technologies witihn fuel shares of existing technology (save fuels of internal fuel switches)
                            III. Calc Fuel of each technology: Share & eff 

                            Total fuel = (shareA* effA) + (shareB * effB) + fuelswtichesFuelTechA + fuelsWitch TechB

                            IV. Update cy technology shares including switch

          '''

import numpy as np
import matplotlib.pyplot as plt



a = [1,1,1,1,1]
b = [2,2,2,2,2]

y = np.row_stack((a,b))
x = [1,2,3,4,5]

#bin = np.arange(5) 
#plt.xlim([0,bin.size])

fig, ax = plt.subplots()
ax.stackplot(x, y)
plt.show()
