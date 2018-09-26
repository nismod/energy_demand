"""Plot stacked enduses for each submodel
"""
import numpy as np
import matplotlib.pyplot as plt
#from scipy.stats import mstats
import pandas as pd

from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def sum_all_enduses_fueltype(
        data_enduses,
        fueltype_str=False,
        period_d=False
    ):
    """Sum across all enduses and fueltypes

    """

    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    y_values_enduse_yrs = {}
    for year in data_enduses.keys():
        for enduse in data_enduses[year].keys():

            # Sum across all fueltypes for every hour
            tot_across_fueltypes = data_enduses[year][enduse]

            try:
                y_values_enduse_yrs[year] += tot_across_fueltypes
            except KeyError:
                y_values_enduse_yrs[year] = tot_across_fueltypes

    return y_values_enduse_yrs

def run(
        data_input,
        simulation_yr_to_plot,
        period_h,
        fueltype_str,
        fig_name
    ):
    """Plots stacked energy demand

    https://stackoverflow.com/questions/18313322/plotting-quantiles-median-and-spread-using-scipy-and-matplotlib

    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.quantile.html

    # Create 10 columns with 100 rows of random data
    rd = np.random.randn(100, 10)
    # Calculate the quantiles column wise
    quantiles = mstats.mquantiles(rd, axis=0)
    # Plot it
    labels = ['25%', '50%', '75%']
    for i, q in enumerate(quantiles):
        plt.plot(q, label=labels[i])
    plt.legend()
    """
    # Select period and fueltype
    fueltype_int = tech_related.get_fueltype_int(fueltype_str)

    # -----------------------------------------------------------
    # Iterate overall weather_yrs and store data in dataframe
    # (columns = timestep, rows: value of year)
    # -----------------------------------------------------------
    columns = period_h # hours in 8760 hours

    # List of selected data for every weather year (which is then converted to array)
    weather_yrs_data = []

    print("Weather yrs: " + str(list(data_input.keys())), flush=True)

    for weather_yr, data_weather_yr in data_input.items():

        # Weather year specific data
        data_input_fueltype = data_weather_yr[simulation_yr_to_plot][fueltype_int]     # Select fueltype
        data_input_reshape = data_input_fueltype.reshape(8760)  # reshape
        data_input_selection_hrs = data_input_reshape[period_h] # select period

        weather_yrs_data.append(data_input_selection_hrs)

    weather_yrs_data = np.array(weather_yrs_data)

    # Create dataframe
    df = pd.DataFrame(weather_yrs_data, columns=columns)

    # Calculate quantiles
    quantile_95 = 0.95
    quantile_05 = 0.05

    df_q_95 = df.quantile(quantile_95)
    df_q_05 = df.quantile(quantile_05)

    #Transpose for plotting purposes
    df = df.T
    df_q_95 = df_q_95.T
    df_q_05 = df_q_05.T

    fig = plt.figure() #(figsize = cm2inch(10,10))
    ax = fig.add_subplot(111)


    # 2015 weather year
    data_2015 = data_weather_yr[2015][fueltype_int].reshape(8760)[period_h]

    # ---------------
    # Smoothing lines
    # ---------------
    try:
        period_h_smoothed, df_q_95_smoothed = basic_plot_functions.smooth_data(period_h, df_q_95, num=40000)
        period_h_smoothed, df_q_05_smoothed = basic_plot_functions.smooth_data(period_h, df_q_05, num=40000)
        period_h_smoothed, data_2015_smoothed = basic_plot_functions.smooth_data(period_h, data_2015, num=40000)
    except:
        period_h_smoothed = period_h
        df_q_95_smoothed = df_q_95
        df_q_05_smoothed = df_q_05
        data_2015_smoothed = data_2015

    plt.plot(period_h_smoothed, data_2015_smoothed, color='tomato', linestyle='-', linewidth=2, label="2015 weather_yr")
    plt.plot(period_h_smoothed, df_q_05_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.05")
    plt.plot(period_h_smoothed, df_q_95_smoothed, color='black', linestyle='--', linewidth=0.5, label="0.95")

    # -----------------
    # Uncertainty range
    # -----------------
    plt.fill_between(
        period_h_smoothed, #x
        df_q_95_smoothed,  #y1
        df_q_05_smoothed,  #y2
        alpha=.25,
        facecolor="grey",
        label="uncertainty band")

    plt.legend(
        #legend_entries,
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

    '''#x_data = np.array(years_simulated)
    # Add every values 
    y_value_arrays = []
    legend_entries = []

    # Try smoothing line
    try:
        x_data_smoothed, y_value_arrays_smoothed = basic_plot_functions.smooth_data(
            x_data, y_value_arrays, num=40000)
    except:
        x_data_smoothed = x_data
        y_value_arrays_smoothed = y_value_arrays


    '''

    '''# Convert to stacked
    y_stacked = np.row_stack((y_value_arrays_smoothed))

    # Set figure size
    fig = plt.figure(
        figsize=basic_plot_functions.cm2inch(8, 8))

    ax = fig.add_subplot(1, 1, 1)

    # ----------
    # Stack plot
    # ----------
    color_stackplots = color_list[:len(enduses)]

    ax.stackplot(
        x_data_smoothed,
        y_stacked,
        alpha=0.8,
        colors=color_stackplots)

    if plot_legend:
        plt.legend(
            legend_entries,
            prop={
                'family':'arial',
                'size': 5},
            ncol=2,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.1),
            frameon=False,
            shadow=True)

    # -------
    # Axis
    # -------
    year_interval = 10
    major_ticks = np.arange(
        years_simulated[0],
        years_simulated[-1] + year_interval,
        year_interval)

    plt.xticks(major_ticks, major_ticks)

    #plt.ylim(ymax=500)
    #yticks = [100, 200, 300, 400, 500]
    #plt.yticks(yticks, yticks)
    # -------
    # Labels
    # -------
    plt.ylabel("TWh", fontsize=10)
    plt.xlabel("Year", fontsize=10)
    #plt.title("ED whole UK", fontsize=10)

    # Tight layout
    fig.tight_layout()

    plt.margins(x=0)
    plt.savefig(fig_name)
    plt.close()'''
