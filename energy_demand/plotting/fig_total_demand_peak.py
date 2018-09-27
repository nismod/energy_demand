"""Plot peak and total demand for 
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from energy_demand.basic import conversions
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

    # List of selected data for every weather year (which is then converted to array)
    weather_yrs_total_demand = []
    weather_yrs_peak_demand = []

    nr_weather_yrs = list(data_input.keys())

    print("Weather yrs: " + str(nr_weather_yrs), flush=True)

    # Iterate weather years
    for weather_yr, data_weather_yr in data_input.items():

        total_demands = []
        peak_demands = []
        simulation_yrs = []
        for sim_yr in data_weather_yr.keys():
            simulation_yrs.append(sim_yr)
            data_input_fueltype = data_weather_yr[sim_yr][fueltype_int]     # Select fueltype

            # sum total annual demand and convert gwh to twh
            sum_gwh_y = np.sum(data_input_fueltype)
            sum_thw_y = conversions.gwh_to_twh(sum_gwh_y)

            # Get peak
            peak_h = np.max(data_input_fueltype.reshape(8760))

            total_demands.append(sum_thw_y)
            peak_demands.append(peak_h)

        weather_yrs_total_demand.append(total_demands)
        weather_yrs_peak_demand.append(peak_demands)

    columns = simulation_yrs

    # Convert to array
    weather_yrs_total_demand = np.array(weather_yrs_total_demand)
    weather_yrs_peak_demand = np.array(weather_yrs_peak_demand)

    # Create dataframe
    if len(nr_weather_yrs) > 2:

        # Create dataframes
        df_total_demand = pd.DataFrame(weather_yrs_total_demand, columns=columns)
        df_peak = pd.DataFrame(weather_yrs_peak_demand, columns=columns)

        # Calculate quantiles
        quantile_95 = 0.95
        quantile_05 = 0.05

        # Calculate quantiles
        df_total_demand_q_95 = df_total_demand.quantile(quantile_95)
        df_total_demand_q_05 = df_total_demand.quantile(quantile_05)
        df_peak_q_95 = df_peak.quantile(quantile_95)
        df_peak_q_05 = df_peak.quantile(quantile_05)

        # convert to list
        df_total_demand_q_95 = df_total_demand_q_95.tolist()
        df_total_demand_q_05 = df_total_demand_q_05.tolist()
        df_peak_q_95 = df_peak_q_95.tolist()
        df_peak_q_05 = df_peak_q_05.tolist()
        #df_peak = df_peak.T #All indivdiual values
    else:
        #df_total_demand = weather_yrs_total_demand
        #df_peak = weather_yrs_peak_demand
        pass

    # -------------------
    # Base year data (2015)
    # -------------------
    # total demand
    tot_demand_twh_2015 = []
    for sim_yr, data_sim_yr in data_input[2015].items():
        gwh_2015_y = np.sum(data_sim_yr[fueltype_int])
        twh_2015_y = conversions.gwh_to_twh(gwh_2015_y)
        tot_demand_twh_2015.append(twh_2015_y)

    # peak
    df_peak_2015 = []
    for sim_yr, data_sim_yr in data_input[2015].items():
        peak_gwh_2015_y = np.max(data_sim_yr[fueltype_int])
        df_peak_2015.append(peak_gwh_2015_y)

    # ---------------
    # Smoothing lines
    # ---------------
    if len(nr_weather_yrs) > 2:
        try:
            period_h_smoothed, tot_demand_twh_2015_smoothed = basic_plot_functions.smooth_data(columns, tot_demand_twh_2015, num=40000)
            period_h_smoothed, df_total_demand_q_95_smoothed = basic_plot_functions.smooth_data(list(columns), df_total_demand_q_95, num=40000)
            period_h_smoothed, df_total_demand_q_05_smoothed = basic_plot_functions.smooth_data(columns, df_total_demand_q_05, num=40000)
            period_h_smoothed, df_peak_q_95_smoothed = basic_plot_functions.smooth_data(list(columns), df_peak_q_95, num=40000)
            period_h_smoothed, df_peak_q_05_smoothed = basic_plot_functions.smooth_data(columns, df_peak_q_05, num=40000)
        except:
            period_h_smoothed = columns
            df_total_demand_q_95_smoothed = df_total_demand_q_95
            df_total_demand_q_05_smoothed = df_total_demand_q_05
            df_peak_q_95_smoothed = df_peak_q_95
            df_peak_q_05_smoothed = df_peak_q_05
            tot_demand_twh_2015_smoothed = tot_demand_twh_2015
    else:
        try:
            period_h_smoothed, tot_demand_twh_2015_smoothed = basic_plot_functions.smooth_data(columns, tot_demand_twh_2015, num=40000)
        except:
            period_h_smoothed = columns
            tot_demand_twh_2015_smoothed = tot_demand_twh_2015

    # --------------
    # Two axis figure
    # --------------
    fig, ax1 = plt.subplots() #figsize=basic_plot_functions.cm2inch(10,10))
    ax2 = ax1.twinx()

    # Axis label
    ax1.set_xlabel('years')
    ax2.set_ylabel('Peak hour demand (GW)', color='blue')
    ax1.set_ylabel('Total demand (TWh)', color='tomato')
    
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.tick_params('y', colors='tomato')
    ax2.tick_params('y', colors='blue')
    
    if len(nr_weather_yrs) > 2:
        
        # -----------------
        # Uncertainty range total demand
        # -----------------
        ax1.plot(period_h_smoothed, df_total_demand_q_05_smoothed, color='tomato', linestyle='--', linewidth=0.5, label="0.05_total_demand")
        ax1.plot(period_h_smoothed, df_total_demand_q_95_smoothed, color='tomato', linestyle='--', linewidth=0.5, label="0.95_total_demand")
        ax1.fill_between(
            period_h_smoothed, #x
            df_total_demand_q_95_smoothed,  #y1
            df_total_demand_q_05_smoothed,  #y2
            alpha=.25,
            facecolor="tomato",
            label="uncertainty band demand")
        
        # -----------------
        # Uncertainty range peaks
        # -----------------
        ax2.plot(period_h_smoothed, df_peak_q_05_smoothed, color='blue', linestyle='--', linewidth=0.5, label="0.05_peak")
        ax2.plot(period_h_smoothed, df_peak_q_95_smoothed, color='blue', linestyle='--', linewidth=0.5, label="0.95_peak")
        ax2.fill_between(
            period_h_smoothed, #x
            df_peak_q_95_smoothed,  #y1
            df_peak_q_05_smoothed,  #y2
            alpha=.25,
            facecolor="blue",
            label="uncertainty band peak")

    # Plot weather year total demand
    ax1.plot(period_h_smoothed, tot_demand_twh_2015_smoothed, color='tomato', linestyle='-', linewidth=2, label="tot_demand_weather_yr_2015")

    # plot peak (all values)
    #ax2.plot(columns, df_peak, color='blue', linestyle='--', linewidth=0.5, label="peak_0.95")
    ax2.plot(columns, df_peak_2015, color='blue', linestyle='-', linewidth=2, label="peak_weather_yr_2015")

    ax1.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='right',
        frameon=False,
        shadow=True)
    ax2.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='left',
        frameon=False,
        shadow=True)
    plt.show()
