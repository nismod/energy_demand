"""Plot peak and total demand for 
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def run(
    data_input,
    fueltype_str,
    fig_name
    ):
    """Plot peak demand and total demand over time in same plot
    """
    # Select period and fueltype
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    # -----------------------------------------------------------
    # Modelled years
    # -----------------------------------------------------------
    #columns = period_h # hours in 8760 hours

    # List of selected data for every weather year (which is then converted to array)
    weather_yrs_total_demand = {}
    weather_yrs_peak_demand = {}

    print("Weather yrs: " + str(list(data_input.keys())), flush=True)

    # Iterate weather years
    for weather_yr, data_weather_yr in data_input.items():

        # Iterate simulation years
        for sim_yr in data_weather_yr.keys():

            data_input_fueltype = data_weather_yr[sim_yr][fueltype_int]     # Select fueltype

            # sum annualy
            sum_y = np.sum(data_input_fueltype)

            # Get peak
            peak_h = np.max(data_input_fueltype.reshape(8760))

            try:
                weather_yrs_total_demand[sim_yr].append(sum_y)
                weather_yrs_peak_demand[sim_yr].append(peak_h)
            except:
                weather_yrs_total_demand[sim_yr] = [sum_y]
                weather_yrs_peak_demand[sim_yr] = [peak_h]

    columns = list(weather_yrs_total_demand.keys())

    # Convert to array
    weather_yrs_total_demand = np.array(
        list(weather_yrs_total_demand.values()))
    weather_yrs_peak_demand = np.array(
        list(weather_yrs_peak_demand.values()))

    # Create dataframe
    df_total_demand = pd.DataFrame(weather_yrs_total_demand, columns=columns)
    df_peak = pd.DataFrame(weather_yrs_peak_demand, columns=columns)

    # Calculate quantiles
    quantile_95 = 0.95
    quantile_05 = 0.05

    df_total_demand_q_95 = df_total_demand.quantile(quantile_95)
    df_total_demand_q_05 = df_total_demand.quantile(quantile_05)

    #Transpose for plotting purposes
    df_total_demand = df_total_demand.T
    df_total_demand_q_95 = df_total_demand_q_95.T
    df_total_demand_q_05 = df_total_demand_q_05.T

    df_peak = df_peak.T

    fig = plt.figure() #(figsize = cm2inch(10,10))
    
    ax = fig.add_subplot(111)

    # ---------------
    # Smoothing lines
    # ---------------
    try:
        period_h_smoothed, df_total_demand_q_95_smoothed = basic_plot_functions.smooth_data(columns, df_total_demand_q_95, num=40000)
        period_h_smoothed, df_total_demand_q_05_smoothed = basic_plot_functions.smooth_data(columns, df_total_demand_q_05, num=40000)
    except:
        period_h_smoothed = columns
        df_total_demand_q_95_smoothed = df_total_demand_q_95
        df_total_demand_q_05_smoothed = df_total_demand_q_05

    plt.plot(period_h_smoothed, df_total_demand_q_05_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.05")
    plt.plot(period_h_smoothed, df_total_demand_q_95_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.95")

    # plot peak
    plt.plot(columns, df_peak, color='black', linestyle='--', linewidth=0.5, label="0.95")

    # -----------------
    # Uncertainty range
    # -----------------
    plt.fill_between(
        period_h_smoothed, #x
        df_total_demand_q_95_smoothed,  #y1
        df_total_demand_q_05_smoothed,  #y2
        alpha=.25,
        facecolor="grey",
        label="uncertainty band")

    plt.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='best',
        #ncol=2,
        #loc='upper center',
        #bbox_to_anchor=(0.5, -0.1),
        frameon=False,
        shadow=True)

    plt.show()

