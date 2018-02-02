import numpy as np
import matplotlib.pyplot as plt
from energy_demand.plotting import plotting_program

def fnx():
    return np.random.randint(5, 50, 10)

x = range(3)
y = []
legend_entries = []

color_list = [
    'darkturquoise',
    'orange',
    'firebrick']

color_stackplots = tuple(color_list)

values = [
    [10, 5, 20],
    [20, 5, 0],
    [30, 5, 37]
]
for i in range(3):
    legend_entries.append("dd")
    #a = fnx()
    #y.append(a)
    y.append(values[i])

#y = np.row_stack((y))
y = np.row_stack((y))

fig = plt.figure(
    figsize=plotting_program.cm2inch(8, 8))
ax = fig.add_subplot(1, 1, 1)
ax.stackplot(
    x,
    y,
    colors=color_list)
plt.legend(
    legend_entries,
    ncol=2,
    loc='best',
    frameon=False)
plt.show()

#---
'''

y = np.row_stack((y))
#y = np.vstack((y))

fig = plt.figure(
    figsize=plotting_program.cm2inch(8, 8))
ax = fig.add_subplot(1, 1, 1)
ax.stackplot(
    x,
    y,
    colors=color_list)
plt.legend(
    legend_entries,
    ncol=2,
    loc='best',
    frameon=False)
plt.show()'''

{'boiler_solid_fuel': 0.0, 'boiler_gas': 0.94056417189048047, 'boiler_electricity': 0.022000203705589881, 'heat_pumps_electricity': 0.93401790757321823, 'district_heating_electricity': 0.0, 'boiler_oil': 0.043981888721191888, 'boiler_biomass': 0.0, 'boiler_hydrogen': 0.0, 'heat_pumps_hydrogen': 0.0}
... calculate sigmoid for techs defined in switch
ddf
{'boiler_solid_fuel': 0.0, 'boiler_gas': 0.94056417189048047, 'boiler_electricity': 0.022000203705589881, 'heat_pumps_electricity': 0.93401790757321823, 'district_heating_electricity': 0.0, 'boiler_oil': 0.043981888721191888, 'boiler_biomass': 0.0, 'boiler_hydrogen': 0.0, 'heat_pumps_hydrogen': 0.0}
{'heat_pumps_electricity': 0.84096149038417023, 'boiler_gas': 0.093056417189048002, 'boiler_solid_fuel': 0.0, 'boiler_electricity': 0.022000203705589881, 'district_heating_electricity': 0.0, 'boiler_oil': 0.043981888721191888, 'boiler_biomass': 0.0, 'boiler_hydrogen': 0.0, 'heat_pumps_hydrogen': 0.0}
base year shares
{'boiler_solid_fuel': 0.0, 'boiler_gas': 0.93056417189048046, 'boiler_electricity': 0.022000203705589871, 'heat_pumps_electricity': 0.0034537356827378041, 'district_heating_electricity': 0.0, 'boiler_oil': 0.043981888721191867, 'boiler_biomass': 0.0, 'boiler_hydrogen': 0.0, 'heat_pumps_hydrogen': 0.0}
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
==================================  ss_space_heating   ========================================
INSTALLddddddddddED TECH: ['heat_pumps_electricity', 'boiler_gas', 'boiler_solid_fuel', 'boiler_electricity', 'district_heating_electricity', 'boiler_oil', 'boiler_biomass', 'boiler_hydrogen', 'heat_pumps_hydrogen']
... create sigmoid diffusion parameters %s heat_pumps_electricity
... create sigmoid diffusion heat_pumps_electricity - [ 2015.  2050.] - [ 0.00345374  0.84096149] - 0.001 - l_val: 0.9340179075732182 - 0.003453735682737804 - 0.8409614903841702
Fit parameters: %s %s %s [ 40.11924681   0.2227907 ] [ 2015.  2050.] [ 0.00345374  0.84096149]
 ... Fitting  %s: Midpoint: %s steepness: %s heat_pumps_electricity 40.1192468078 0.222790700281
... plot sigmoid diffusion heat_pumps_electricity 0.9340179075732182 [ 2015.  2050.] [ 0.00345374  0.84096149] 0.003453735682737804 0.8409614903841702
... create sigmoid diffusion parameters %s boiler_gas
... create sigmoid diffusion boiler_gas - [ 2015.  2050.] - [ 0.93056417  0.09305642] - 0.001 - l_val: 0.9405641718904805 - 0.9305641718904805 - 0.093056417189048
Fit parameters: %s %s %s [ 38.53235667  -0.19263714] [ 2015.  2050.] [ 0.93056417  0.09305642]
 ... Fitting  %s: Midpoint: %s steepness: %s boiler_gas 38.5323566661 -0.192637142552
... plot sigmoid diffusion boiler_gas 0.9405641718904805 [ 2015.  2050.] [ 0.93056417  0.09305642] 0.9305641718904805 0.093056417189048
... create sigmoid diffusion parameters %s boiler_solid_fuel
... create sigmoid diffusion boiler_solid_fuel - [ 2015.  2050.] - [ 0.001  0.001] - 0.001 - l_val: 0.0 - 0.001 - 0.001
  0.001 0.001 0.001 0.0
... tech is constand and does not need fitting %s boiler_solid_fuel
... create sigmoid diffusion parameters %s boiler_electricity
... create sigmoid diffusion boiler_electricity - [ 2015.  2050.] - [ 0.0220002  0.0220002] - 0.001 - l_val: 0.02200020370558988 - 0.02200020370558987 - 0.02200020370558988
  0.02200020370558987 0.001 0.02200020370558988 0.02200020370558988
... tech is constand and does not need fitting %s boiler_electricity
... create sigmoid diffusion parameters %s district_heating_electricity
... create sigmoid diffusion district_heating_electricity - [ 2015.  2050.] - [ 0.001  0.001] - 0.001 - l_val: 0.0 - 0.001 - 0.001
  0.001 0.001 0.001 0.0
... tech is constand and does not need fitting %s district_heating_electricity
... create sigmoid diffusion parameters %s boiler_oil
... create sigmoid diffusion boiler_oil - [ 2015.  2050.] - [ 0.04398189  0.04398189] - 0.001 - l_val: 0.04398188872119189 - 0.04398188872119187 - 0.04398188872119189
  0.04398188872119187 0.001 0.04398188872119189 0.04398188872119189
... tech is constand and does not need fitting %s boiler_oil
... create sigmoid diffusion parameters %s boiler_biomass
... create sigmoid diffusion boiler_biomass - [ 2015.  2050.] - [ 0.001  0.001] - 0.