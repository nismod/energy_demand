import numpy as np
import matplotlib.pyplot as plt
import pylab
def sigmoid_function(x, L, midpoint, steepness):
    """Sigmoid function

    Paramters
    ---------
    x : float
        X-Value
    L : float
        The durv'es maximum value
    midpoint : float
        The midpoint x-value of the sigmoid's midpoint
    k : dict
        The steepness of the curve

    Return
    ------
    y : float
        Y-Value

    Notes
    -----
    This function is used for fitting and plotting

    """
    y = L / (1 + np.exp(-steepness * ((x - 2000) - midpoint)))
    return y

def plotout_sigmoid_tech_diff(L_values, technology, enduse, xdata, ydata, fit_parameter, close_window_crit=True):
    """Plot sigmoid diffusion
    """
    def close_event():
        """Timer to close window automatically
        """
        plt.close()

    L = L_values[enduse][technology]
    x = np.linspace(2015, 2100, 100)
    y = sigmoid_function(x, L, *fit_parameter)

    fig = plt.figure()

    #creating a timer object and setting an interval
    timer = fig.canvas.new_timer(interval = 1500)
    timer.add_callback(close_event)

    fig.set_size_inches(12, 8)
    pylab.plot(xdata, ydata, 'o', label='base year and future market share')
    pylab.plot(x, y, label='fit')

    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')

    pylab.xlabel('Time')
    pylab.ylabel('Market share of technology on energy service')
    pylab.title("Sigmoid diffusion of technology  {}  in enduse {}".format(technology, enduse))

    if close_window_crit:
        timer.start()
    else:
        pass
    pylab.show()
