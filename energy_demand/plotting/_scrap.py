import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from energy_demand.plotting import validation_enduses


rows = [{'year': 2015,
    'hour': 0,
    'residential_non_heat': 10,
    'residential_heat': 30,
    'service_non_heat': 40,
    'service_heat': 50,
    'industry_non_heat': 60,
    'industry_heat': 70},
    {'year': 2015,
    'hour': 1,
    'residential_non_heat': 23,
    'residential_heat': 32,
    'service_non_heat': 43,
    'service_heat': 54,
    'industry_non_heat': 63,
    'industry_heat': 40},
    {'year': 2015,
    'hour': 2,
    'residential_non_heat': 63,
    'residential_heat': 62,
    'service_non_heat': 63,
    'service_heat': 64,
    'industry_non_heat': 63,
    'industry_heat': 60},
    ]

col_names = [
    'year',
    'hour',
    'residential_non_heat',
    'residential_heat',
    'service_non_heat',
    'service_heat',
    'industry_non_heat',
    'industry_heat']

my_df = pd.DataFrame(rows, columns=col_names)

validation_enduses.plot_dataframe_function(
    my_df,
    'hour',
    ['residential_non_heat', 'residential_heat'],
    'line')
