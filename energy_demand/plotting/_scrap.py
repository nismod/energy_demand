"""Fig 2 figure
"""
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
    [[-5, 1], [-3, 10], [0, 100], [3, 100], [5, 100]]),
                      columns=['diff_av_max', 'b'])

uk_gdf = fig_p2_weather_var.user_defined_bin_classification(
    uk_gdf,
    "diff_av_max",
    bin_values=[-3, 0, 3])
