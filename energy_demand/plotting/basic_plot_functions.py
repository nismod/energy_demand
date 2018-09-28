"""Basic plotting functions
"""
import math
import numpy as np
import matplotlib.pyplot as plt
import pylab
from scipy.interpolate import interp1d
from scipy.interpolate import spline

from energy_demand.technologies import diffusion_technologies
#matplotlib.use('Agg') # Used to make it work in linux

def cm2inch(*tupl):
    """Convert input cm to inches (width, hight)
    """
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

def simple_smooth(x_list, y_list, num=500, spider=False, interpol_kind='quadratic'):

    nr_x_values = len(x_list)
    min_x_val = min(x_list)
    max_x_val = max(x_list)

    x_values = np.linspace(min_x_val, max_x_val, num=nr_x_values, endpoint=True)

    f2 = interp1d(x_values, y_list, kind=interpol_kind)

    smoothed_data_x = np.linspace(
        min_x_val,
        max_x_val,
        num=num,
        endpoint=True)

    smoothed_data_y = f2(smoothed_data_x)

    return smoothed_data_x, smoothed_data_y

def smooth_data(
        x_list,
        y_list,
        num=500,
        spider=False,
        interpol_kind='quadratic'
    ):
    """Smooth data

    x_list : list
        List with x values
    y_list : list
        List with y values
    num : int
        New number of interpolation points
    spider : bool
        Criteria whether spider plot or not

    

    Note:
    ------
    - needs at least 4 entries in lists
    - https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html

    """

    if spider:

        min_x_val = min(x_list)
        max_x_val = math.pi * 2 #max is tow pi

        x_values = np.linspace(
            min_x_val,
            max_x_val,
            num=len(x_list),
            endpoint=True)

        f2 = interp1d(
            x_values,
            y_list,
            kind='quadratic') #quadratic cubic

        x_smooth = np.linspace(
            min_x_val,
            max_x_val,
            num=num,
            endpoint=True)

        #y_smooth = f2(x_smooth)

    else:
        # Smooth x data
        x_smooth = np.linspace(
            min(x_list),
            max(x_list),
            num=num)

        f2 = interp1d(
            x_list,
            y_list,
            kind=interpol_kind)

    # smooth
    y_smooth = f2(x_smooth)

    return x_smooth, y_smooth

def smooth_line(
        input_x_line_data,
        input_y_line_data,
        nr_line_points=1000
    ):
    """https://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot

    nr_line_points : int
        represents number of points to make between input_line_data.min and T.max
    """
    input_x_line_data = np.array(input_x_line_data)
    input_y_line_data = np.array(input_y_line_data)

    smooth_x_line_data = np.linspace(
        input_x_line_data.min(),
        input_x_line_data.max(),
        nr_line_points) 

    smooth_y_line_data = spline(
        input_x_line_data,
        input_y_line_data,
        smooth_x_line_data)

    return smooth_x_line_data, smooth_y_line_data

def plotout_sigmoid_tech_diff(
        L_value,
        technology,
        xdata,
        ydata,
        fit_parameter,
        plot_crit=False,
        close_window_crit=True
    ):
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
    timer = fig.canvas.new_timer(interval=555)
    timer.add_callback(close_event)

    fig.set_size_inches(12, 8)
    pylab.plot(xdata, ydata, 'o', label='base year and future market share')
    pylab.plot(x, y, label='fit')

    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')

    pylab.xlabel('Time')
    pylab.ylabel('Market share of technology on energy service')
    pylab.title("Sigmoid diffusion of technology {}".format(technology))

    if plot_crit:
        if close_window_crit:
            pylab.show()
        else:
            timer.start()
            pylab.show()
            pass
    else:
        pass

def plot_xy(y_values):

    x_values = range(len(y_values))

    plt.plot(x_values, y_values, 'ro')
    plt.show()
