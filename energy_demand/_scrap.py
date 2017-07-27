import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import numpy as np
import matplotlib.pyplot as plt

x = [0,5,9,10,15]
y = [0,1,2,3,4]
plt.plot(x,y)
#plt.xticks(np.arange(min(x), max(x)+1, 1.0))
plt.yticks(range(0, 10, 2))
plt.ylim(0, 10)

plt.show()

'''

array_dh = np.random.rand(24)



def plot_load_profile_dh(array_dh):

    hours = range(1, 25)
    x_values = []
    for hour in hours:
        x_values.append(hour - 0.5)

    plt.plot(x_values, list(array_dh), color='green') #'ro', markersize=1,
    #plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')
    plt.axis('tight')
    #fig, ax = ax.set_xlim(ymin=0)
    #ax.set_ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.xticks(np.arange(0, 24, 4.0))
    plt.show()

plot_load_profile_dh(array_dh)


'''

def boxplots_month():


    x_labels_ticks = ['A', ' B']

    norm = np.random.normal(1, 1, 500)
    norm2 = np.random.normal(1, 1, 500)

    data = [norm, norm2]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.canvas.set_window_title('A Boxplot Example')
    plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

    bp = plt.boxplot(data, notch=0, sym='+', vert=1, whis=1.5)
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')

    # Add a horizontal grid to the plot, but make it very light in color so we can use it for reading data values but not be distracting
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

    # Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    ax1.set_title('Comparison of deviation according to hour')
    ax1.set_xlabel('Hours')
    ax1.set_ylabel('GWh')

    # Now fill the boxes with desired colors
    boxColors = ['darkkhaki', 'royalblue']

    numBoxes = len(data)

    medians = list(range(numBoxes))
    for i in range(numBoxes):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        boxCoords = list(zip(boxX, boxY))

        # Alternate between Dark Khaki and Royal Blue

        boxPolygon = Polygon(boxCoords, facecolor=boxColors[i])
        ax1.add_patch(boxPolygon)

        # Now draw the median lines back over what we just filled in
        med = bp['medians'][i]
        medianX = []
        medianY = []
        for j in range(2):
            medianX.append(med.get_xdata()[j])
            medianY.append(med.get_ydata()[j])
            plt.plot(medianX, medianY, 'k')
            medians[i] = medianY[0]

        # Finally, overplot the sample averages, with horizontal alignment in the center of each box
        plt.plot([np.average(med.get_xdata())], [np.average(data[i])], color='w', marker='*', markeredgecolor='k')

    # Set the axes ranges and axes labels
    ax1.set_xlim(0.5, numBoxes + 0.5)
    top = 40
    bottom = -5
    ax1.set_ylim(bottom, top)
    xtickNames = plt.setp(ax1, xticklabels=np.repeat(x_labels_ticks, 2))
    plt.setp(xtickNames, rotation=0, fontsize=8)

    # Due to the Y-axis scale being different across samples, it can be
    # hard to compare differences in medians across the samples. Add upper
    # X-axis tick labels with the sample medians to aid in comparison
    # (just use two decimal places of precision)
    pos = np.arange(numBoxes) + 1
    upperLabels = [str(np.round(s, 2)) for s in medians]
    weights = ['bold', 'semibold']
    for tick, label in zip(range(numBoxes), ax1.get_xticklabels()):
        k = tick % 2
        ax1.text(pos[tick], top - (top*0.05), upperLabels[tick],
                horizontalalignment='center', size='x-small', weight=weights[k],
                color=boxColors[k])

    # Finally, add a basic legend
    plt.figtext(0.80, 0.08, 'test', backgroundcolor=boxColors[0], color='black', weight='roman', size='x-small')

    plt.show()

boxplots_month()

'''

'''