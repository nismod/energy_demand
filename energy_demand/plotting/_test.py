import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 
# Dataset
ax = plt.subplot(111)

dataright = np.random.rand(10, 4)
dataleft = dataright * -1
df_right = pd.DataFrame(dataright, columns=['a', 'b', 'c', 'd'])
df_left = pd.DataFrame(dataleft, columns=['a', 'b', 'c', 'd'])


# plot WORKDS
#labels_minus = list(df_left.values)
#labels_plus = list(df_right.values)
#labels = labels_minus + labels_plus

'''
df_right.plot(kind='barh', stacked=True, width=1.0)
df_left.plot(kind='barh',stacked=True, width=1.0)'''


fig, ax = plt.subplots(ncols=1, sharey=True)

##ax.invert_xaxis()
##ax.yaxis.tick_right()
#ax.set_yticklabels(labels)
# Add vertical line
ax.axvline(linewidth=1, color='black')

df_right.plot(kind='barh', legend=True, ax=ax, width=1.0, stacked=True)
df_left.plot(kind='barh', legend=True, ax=ax, width=1.0, stacked=True)
plt.show()

#raise Exception

#https://stackoverflow.com/questions/44049132/python-pandas-plotting-two-barh-side-by-side
#df = pd.DataFrame()

#df_1[target_cols].plot(kind='barh', x='LABEL', stacked=True, legend=False)
#df_2[target_cols].plot(kind='barh', x='LABEL', stacked=True).invert_xaxis()

#x_axis = [list(df_right.index)]
#print(x_axis)
#print("...")
#print(np.array([5., 30., 45., 22.]))
##plt.barh(np.arange(4), np.array([5., 30., 45., 22.]), color = 'r')
#plt.barh(x_axis, df_right, color = 'r', stacked='True')
#plt.barh(x_axis, df_right, color='r', stacked=True)
#plt.barh(x_axis, df_left, color='b', stacked=True)

#plt.show()#
#print("..")

'''
import numpy as np
import matplotlib.pyplot as plt

women_pop = np.array([5., 30., 45., 22.])
men_pop     = np.array( [5., 25., 50., 20.])
X = np.arange(4)

plt.barh(X, women_pop, color = 'r')
plt.barh(X, -men_pop, color = 'b')
plt.show()
'''