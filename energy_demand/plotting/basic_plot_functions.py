"""Basic plotting functions
"""
import math
import numpy as np

from scipy.interpolate import interp1d
from scipy.interpolate import spline

from energy_demand.technologies import diffusion_technologies
#matplotlib.use('Agg') # Used to make it work in linux

def export_legend(legend, filename="legend.png"):
    """Export legend as seperate file
    """
    fig = legend.figure
    fig.canvas.draw()
    bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)

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
    interpol_kind : str
        Kind of interpolation, i.e. quadratic or cubic

    Note:
    ------
    - needs at least 4 entries in lists
    - https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
    - The smoothing prevents negative values by setting them to zero
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
            kind=interpol_kind) 

        x_smooth = np.linspace(
            min_x_val,
            max_x_val,
            num=num,
            endpoint=True)
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

    # Prevent smoothing to go into negative values and replace negative values with zero

    # Get position of last negative entry
    try:
        pos_zero = int(np.argwhere(y_smooth < 0)[-1])
        y_smooth[:pos_zero] = 0
    except IndexError:
        pass

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
