"""Plot peak and total demand for 
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from energy_demand.basic import conversions
from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions
from energy_demand.read_write import write_data

def run(
        data_input,
        fueltype_str,
        fig_name
    ):
    """Plot peak demand and total demand over time in same plot
    """
    statistics_to_print = []

    # Select period and fueltype
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    # -----------------------------------------------------------
    # Modelled years
    # -----------------------------------------------------------

    # List of selected data for every weather year (which is then converted to array)
    weather_yrs_total_demand = []
    weather_yrs_peak_demand = []

    nr_weather_yrs = list(data_input.keys())
    statistics_to_print.append("_____________________________")
    statistics_to_print.append("Weather years")
    statistics_to_print.append(str(data_input.keys()))

    # Iterate weather years
    for weather_yr, data_weather_yr in data_input.items():

        total_demands = []
        peak_demands = []
        sim_yrs = []
        for sim_yr in data_weather_yr.keys():
            sim_yrs.append(sim_yr)
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

    columns = sim_yrs

    # Convert to array
    weather_yrs_total_demand = np.array(weather_yrs_total_demand)
    weather_yrs_peak_demand = np.array(weather_yrs_peak_demand)

    # Calculate std per simulation year
    std_total_demand = list(np.std(weather_yrs_total_demand, axis=0)) # across columns calculate std
    std_peak_demand = list(np.std(weather_yrs_peak_demand, axis=0)) # across columns calculate std

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
            period_h_smoothed, df_peak_2015_smoothed = basic_plot_functions.smooth_data(columns, df_peak_2015, num=40000)
        except:
            period_h_smoothed = columns
            df_total_demand_q_95_smoothed = df_total_demand_q_95
            df_total_demand_q_05_smoothed = df_total_demand_q_05
            df_peak_q_95_smoothed = df_peak_q_95
            df_peak_q_05_smoothed = df_peak_q_05
            tot_demand_twh_2015_smoothed = tot_demand_twh_2015
            df_peak_2015_smoothed = df_peak_2015
    else:
        try:
            period_h_smoothed, tot_demand_twh_2015_smoothed = basic_plot_functions.smooth_data(columns, tot_demand_twh_2015, num=40000)
            period_h_smoothed, df_peak_2015_smoothed = basic_plot_functions.smooth_data(columns, df_peak_2015, num=40000)
        except:
            period_h_smoothed = columns
            tot_demand_twh_2015_smoothed = tot_demand_twh_2015
            df_peak_2015_smoothed = df_peak_2015
     
    # --------------
    # Two axis figure
    # --------------
    fig, ax1 = plt.subplots(
        figsize=basic_plot_functions.cm2inch(15, 10))

    ax2 = ax1.twinx()

    # Axis label
    ax1.set_xlabel('Years')
    ax2.set_ylabel('Peak hour {} demand (GW)'.format(fueltype_str), color='black')
    ax1.set_ylabel('Total {} demand (TWh)'.format(fueltype_str), color='black')

    # Make the y-axis label, ticks and tick labels match the line color.¨
    color_axis1 = 'lightgrey'
    color_axis2 = 'blue'

    ax1.tick_params('y', colors='black')
    ax2.tick_params('y', colors='black')

    if len(nr_weather_yrs) > 2:

        # -----------------
        # Uncertainty range total demand
        # -----------------
        '''ax1.plot(
            period_h_smoothed,
            df_total_demand_q_05_smoothed,
            color='tomato', linestyle='--', linewidth=0.5, label="0.05_total_demand")'''

        '''ax1.plot(
            period_h_smoothed,
            df_total_demand_q_95_smoothed,
            color=color_axis1, linestyle='--', linewidth=0.5, label="0.95_total_demand")

        ax1.fill_between(
            period_h_smoothed, #x
            df_total_demand_q_95_smoothed,  #y1
            df_total_demand_q_05_smoothed,  #y2
            alpha=.25,
            facecolor=color_axis1,
            label="uncertainty band demand")'''

        # -----------------
        # Uncertainty range peaks
        # -----------------
        ##ax2.plot(period_h_smoothed, df_peak_q_05_smoothed, color=color_axis2, linestyle='--', linewidth=0.5, label="0.05_peak")
        ##ax2.plot(period_h_smoothed, df_peak_q_95_smoothed, color=color_axis2, linestyle='--', linewidth=0.5, label="0.95_peak")
        ax2.plot(
            period_h_smoothed,
            df_peak_2015_smoothed,
            color=color_axis2, linestyle="--", linewidth=0.4)

        # Error bar of bar charts
        ax2.errorbar(columns, df_peak_2015, linewidth=0.5, color='black', yerr=std_peak_demand, linestyle="None")

        # Error bar bar plots
        ax1.errorbar(
            columns, tot_demand_twh_2015, linewidth=0.5, color='black', yerr=std_total_demand, linestyle="None")

        '''ax2.fill_between(
            period_h_smoothed, #x
            df_peak_q_95_smoothed,  #y1
            df_peak_q_05_smoothed,  #y2
            alpha=.25,
            facecolor="blue",
            label="uncertainty band peak")'''

    # Total demand bar plots
    ##ax1.plot(period_h_smoothed, tot_demand_twh_2015_smoothed, color='tomato', linestyle='-', linewidth=2, label="tot_demand_weather_yr_2015")
    ax1.bar(
        columns,
        tot_demand_twh_2015,
        width=2,
        alpha=1,
        align='center',
        color=color_axis1,
        label="total {} demand".format(fueltype_str))

    statistics_to_print.append("_____________________________")
    statistics_to_print.append("total demand per model year")
    statistics_to_print.append(str(tot_demand_twh_2015))

    # Line of peak demand
    #ax2.plot(columns, df_peak, color=color_axis2, linestyle='--', linewidth=0.5, label="peak_0.95")
    ax2.plot(
        period_h_smoothed,
        df_peak_2015_smoothed,
        color=color_axis2, linestyle='-', linewidth=2, label="{} peak demand (base weather yr)".format(fueltype_str))

    statistics_to_print.append("_____________________________")
    statistics_to_print.append("peak demand per model year")
    statistics_to_print.append(str(df_peak_2015))

    # Scatter plots of peak demand
    ax2.scatter(
        columns,
        df_peak_2015,
        marker='o', s=20, color=color_axis2, alpha=1)

    ax1.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='upper center',
        bbox_to_anchor=(0.9, -0.1),
        frameon=False,
        shadow=True)

    ax2.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='upper center',
        bbox_to_anchor=(0.1, -0.1),
        frameon=False,
        shadow=True)

    # More space at bottom
    #fig.subplots_adjust(bottom=0.4)
    fig.tight_layout()

    plt.savefig(fig_name)
    plt.close()

    # Write info to txt
    write_data.write_list_to_txt(
        os.path.join(fig_name.replace(".pdf", ".txt")),
        statistics_to_print)
    print("--")
