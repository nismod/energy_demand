import numpy as np
import matplotlib.pyplot as plt
import pylab
from energy_demand.technologies import diffusion_technologies

def cm2inch(*tupl):
    """Convert input cm to inches
    """
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

def plotout_sigmoid_tech_diff(L_value, technology, enduse, xdata, ydata, fit_parameter, close_window_crit=True):
    """Plot sigmoid diffusion
    """
    def close_event():
        """Timer to close window automatically
        """
        plt.close()

    x = np.linspace(1990, 2110, 300)
    y = diffusion_technologies.sigmoid_function(x, L_value, *fit_parameter)

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
