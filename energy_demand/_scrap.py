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