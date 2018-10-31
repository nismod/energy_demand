"""Fig 2 figure
"""

import numpy as np


a = np.ones((3,3))

calc_lf_y(a)

def calc_lf_y(fuel_yh):
    """Calculate the yearly load factor for every fueltype
    by dividing the yearly average load by the peak hourly
    load in a year.

    Arguments
    ---------
    fuel_yh : array (fueltypes, 365, 24) or (fueltypes, 8760)
        Yh fuel

    Returns
    -------
    load_factor_y : array
        Yearly load factors as percentage (100% = 100)

    Note
    -----
        LECTRICAL AND PRODUCTION LOAD FACTORS
        ## Load factor = average load / maximum load in given time period
        Load factor = average load / peak load    # * meausred hours
        https://en.wikipedia.org/wiki/Load_factor_(electrical)

        https://circuitglobe.com/load-factor.html
    """
    if fuel_yh.shape[1] == 365:
        fuel_yh_8760 = fuel_yh.reshape(fuel_yh.shape[0], 8760)
    else:
        fuel_yh_8760 = fuel_yh

    # Get total sum per fueltype
    tot_load_y = np.sum(fuel_yh_8760, axis=1)

    # Calculate maximum hour in every day of a year
    max_load_h = np.max(fuel_yh_8760, axis=1)

    # Caclualte yearly load factor for every fueltype
    with np.errstate(divide='ignore', invalid='ignore'):
        load_factor_y = tot_load_y / (max_load_h * 8760)
    load_factor_y[np.isnan(load_factor_y)] = 0

    return load_factor_y * 100










import numpy as np
import matplotlib.pyplot as plt
#from scipy.stats import mstats
import pandas as pd
import geopandas as gpd
from scipy import stats
from shapely.geometry import Point
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.colors import Normalize

from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

from energy_demand.plotting import fig_p2_weather_var

uk_gdf = pd.DataFrame(np.array(
    [
        [-5, 1],
        [-3, 10],
        [0, 100],
        [3, 100],
        [5, 100]]),

    columns=['diff_av_max', 'b'])

uk_gdf = fig_p2_weather_var.user_defined_bin_classification(
    uk_gdf,
    "diff_av_max",
    bin_values=[-3, 0, 3])
