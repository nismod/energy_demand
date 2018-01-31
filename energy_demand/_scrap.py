import numpy as np
import matplotlib.pyplot as plt
from energy_demand.plotting import plotting_program

def fnx():
    return np.random.randint(5, 50, 10)

y = []
legend_entries = []

color_list = [
    'darkturquoise',
    'orange',
    'firebrick']

color_stackplots = tuple(color_list)

for i in range(3):
    legend_entries.append("dd")
    a = fnx()
    y.append(a)

y = np.row_stack((y))
x = np.arange(10)

fig = plt.figure(
    figsize=plotting_program.cm2inch(8, 8))

ax = fig.add_subplot(1, 1, 1)

ax.stackplot(x, y, colors=color_list)

plt.legend(
    legend_entries,
    ncol=2,
    loc='best',
    frameon=False)

plt.show()
