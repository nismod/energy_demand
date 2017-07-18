import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def boxplots_month():


    fig = plt.figure()
    ax = fig.add_subplot(111)

    x1 = np.random.normal(0,1,50)
    x2 = np.random.normal(1,1,50)
    x3 = np.random.normal(2,1,50)

    ax.boxplot([x1,x2,x3])
    plt.show()


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