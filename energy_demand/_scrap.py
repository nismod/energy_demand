
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