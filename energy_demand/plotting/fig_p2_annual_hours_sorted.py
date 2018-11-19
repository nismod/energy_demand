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

from energy_demand.plotting import result_mapping
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def run(
        data_input,
        regions,
        _to_plot,
        fueltype_str,
        path_shapefile,
        fig_name
    ):
    """
    """
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    # Figure related
    fig = plt.figure() #(figsize = cm2inch(10,10))
    ax = fig.add_subplot(111)
    period_h = range(8760)

    for sim_yr_to_plot in simulation_yrs_to_plot:

        # ---Collect data for every weather year
        weather_yrs_data_regional = defaultdict(dict)
        weather_yrs_data_total = []
        for weather_yr, data_weather_yr in data_input.items():

            # Weather year specific data for every region
            regions_fuel = data_weather_yr[sim_yr_to_plot][fueltype_int]

            # Total fuel
            national_fuel = np.sum(regions_fuel, axis=0)

            for region_nr, region_name in enumerate(regions):
                try:
                    weather_yrs_data_regional[region_name].append(regions_fuel[region_nr])
                except (KeyError, AttributeError):
                    weather_yrs_data_regional[region_name] = [regions_fuel[region_nr]]
            try:
                weather_yrs_data_total.append(national_fuel)
            except:
                weather_yrs_data_total = [national_fuel]

        # ---Collect data for every weather year

        # Convert regional data to dataframe
        national_fuel_array = np.array(weather_yrs_data_total)

        df = pd.DataFrame(
            national_fuel_array,
            columns=range(8760))

        # Calculate regional statistics
        mean_data = df.mean(axis=0)

        mean_data = mean_data.sort_values(ascending=False)

        # Reorder df according to ordering of mean values
        ordering_of_hours_index = list(mean_data.index)

        df = df[ordering_of_hours_index]

        #std_dev = df.std(axis=0) #standard deviation across every hour
        # Calculate quantiles
        quantile_95 = 0.95
        quantile_05 = 0.05

        df_q_95 = df.quantile(quantile_95)
        df_q_05 = df.quantile(quantile_05)

        #Transpose for plotting purposes
        df = df.T
        df_q_95 = df_q_95.T
        df_q_05 = df_q_05.T

        # ---------------
        # Smoothing lines
        # ---------------
        try:
            period_h_smoothed, df_q_95_smoothed = basic_plot_functions.smooth_data(period_h, df_q_95, num=40000)
            period_h_smoothed, df_q_05_smoothed = basic_plot_functions.smooth_data(period_h, df_q_05, num=40000)
            period_h_smoothed, mean_data_smoothed = basic_plot_functions.smooth_data(period_h, mean_data, num=40000)
        except:
            period_h_smoothed = period_h
            df_q_95_smoothed = df_q_95
            df_q_05_smoothed = df_q_05
            mean_data_smoothed = mean_data

        plt.plot(period_h_smoothed, mean_data_smoothed, color='tomato', linestyle='-', linewidth=2, label="average")
        #plt.plot(period_h_smoothed, df_q_05_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.05")
        #plt.plot(period_h_smoothed, df_q_95_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.95")

        # -----------------
        # Uncertainty range
        # -----------------
        plt.fill_between(
            period_h_smoothed, #x
            df_q_95_smoothed,  #y1
            df_q_05_smoothed,  #y2
            alpha=.40,
            facecolor="grey",
            label="uncertainty band")

        plt.legend(
            prop={
                'family':'arial',
                'size': 10},
            loc='best',
            frameon=False,
            shadow=True)

        plt.xlabel("Load duration curve")
        plt.ylabel("energy demand")

        plt.xlim(0, 8760)
        plt.show()

        print("--")
