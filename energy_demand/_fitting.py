import numpy as np
import pylab
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

import numpy as np
import pylab
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt





def svenplot(L, xdata, ydata):
    """Fit sigmoid curve based on two points on the diffusion curve

    Parameters
    ----------
    L : float
        The sigmoids curve maximum value (max consumption )

    def sigmoid(x, x0, k):
        y = L/ (1 + np.exp(-k*(x-x0)))
        return y


    popt, pcov = curve_fit(sigmoid, xdata, ydata,p0=[2030, 0.5])
    print (popt)

    x = np.linspace(2000, 2100, 50)
    y = sigmoid(x, *popt)

    fig = plt.figure()
    fig.set_size_inches(12,8)
    pylab.plot(xdata, ydata, 'o', label='data')
    pylab.plot(x,y, label='fit')
    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')
    pylab.show()

    return popt

xdata = np.array([2020, 2030])
ydata = np.array([0.00001, 0.60])
L = 0.8

out = svenplot(L, xdata, ydata)





'''
import numpy as np
import pylab
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def svenplot(L, xdata, ydata):


    def sigmoid(x, x0, k):
        y = L/ (1 + np.exp(-k*(x-x0)))
        return y


    popt, pcov = curve_fit(sigmoid, xdata, ydata,p0=[2030, 0.5])
    print (popt)

    x = np.linspace(2000, 2100, 50)
    y = sigmoid(x, *popt)

    fig = plt.figure()
    fig.set_size_inches(12,8)
    pylab.plot(xdata, ydata, 'o', label='data')
    pylab.plot(x,y, label='fit')
    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')
    pylab.show()

    return popt

xdata = np.array([2010, 2050])
ydata = np.array([0.00001, 0.03])
L = 0.8

out = svenplot(L, xdata, ydata)

'''