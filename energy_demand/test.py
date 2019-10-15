import matplotlib.pyplot as plt
import numpy as np

data_a = [[1,2,5], [5,7,2,2,5], [7,2,5]]
data_b = [[6,4,2], [1,2,5,3,2], [2,3,5,1]]

ticks = ['A', 'B', 'C']

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)

plt.figure()

fig = plt.figure() #width, height
ax = fig.add_subplot(1, 1, 1)


'''
boxprops=dict(linestyle='-', linewidth=0.25, color='black', facecolor=color, alpha=1.0),
meanprops=dict(linestyle='--', linewidth=0, color='green', alpha=1.0),
capprops=dict(linewidth=0.6, color=color, alpha=1.0),
whiskerprops=dict(linewidth=0.6, color=color, markeredgecolor=color, alpha=1.0),
flierprops=dict(linewidth=0.6, color=color, markeredgecolor=color, alpha=1.0),
medianprops=dict(linewidth=0, color=color, alpha=1.0)'''
color_1 = '#377eb8' # orange
color_2 = '#ff7f00' # blue

bpl = ax.boxplot(
    data_a,
    positions=np.array(range(len(data_a)))*2.0-0.4,
    sym='',
    widths=0.6, 
    whis='range',
    patch_artist=True ,
    boxprops=dict(linewidth=0.6, linestyle='-', color='black', facecolor=color_1, alpha=1.0),
    meanprops=dict(linestyle='--', linewidth=0, color='green', alpha=1.0),
    capprops=dict(linewidth=0.6, color=color_1, alpha=1.0),
    whiskerprops=dict(linewidth=1, color=color_1, markeredgecolor=color_1, alpha=1.0),
    flierprops=dict(linewidth=0.6, color=color_1, markeredgecolor=color_1, alpha=1.0),
    medianprops=dict(linewidth=0, color=color_1, alpha=1.0)
    )

for box in bpl['boxes']:
    box.set(hatch = '//') # change hatch

bpr = ax.boxplot(
    data_b,
    positions=np.array(range(len(data_b)))*2.0+0.4,
    sym='',
    widths=0.6, 
    whis='range',
    patch_artist=True,
    boxprops=dict(linewidth=0.6, linestyle='-', color='black', facecolor=color_2, alpha=1.0),
    meanprops=dict(linestyle='--', linewidth=0, color='green', alpha=1.0),
    capprops=dict(linewidth=0.6, color=color_2, alpha=1.0),
    whiskerprops=dict(linewidth=1, color=color_2, markeredgecolor=color_2, alpha=1.0),
    flierprops=dict(linewidth=0.6, color=color_2, markeredgecolor=color_2, alpha=1.0),
    medianprops=dict(linewidth=0, color=color_2, alpha=1.0)
    )

for box in bpr['boxes']:
    box.set(hatch = '..') # change hatch


'''def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)'''

#set_box_color(bpl, '#377eb8') 
#set_box_color(bpr, '#ff7f00')
# draw temporary red and blue lines and use them to create a legend

plt.legend()

plt.xticks(range(0, len(ticks) * 2, 2), ticks)
plt.xlim(-2, len(ticks)*2)
plt.ylim(0, 8)
plt.tight_layout()
plt.show()
plt.savefig('boxcompare.png')