"""Plot local and regional figure
"""
import numpy as np
import matplotlib.pyplot as plt
#from scipy.stats import mstats
import pandas as pd
from scipy import stats

from energy_demand.technologies import tech_related
from energy_demand.plotting import basic_plot_functions

def run(
        data_input,
        weather_yr,
        fueltype_str,
        simulation_yr_to_plot,
        period_h,
        validation_elec_2015,
        non_regional_elec_2015,
        fig_name
    ):
    """
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
    weather_yrs_full_year = []

    for station_id, data_weather_yr in data_input[weather_yr].items():

        # Weather year specific data
        data_input_fueltype = data_weather_yr[simulation_yr_to_plot][fueltype_int]     # Select fueltype
        data_input_reshape = data_input_fueltype.reshape(8760)  # reshape
        data_input_selection_hrs = data_input_reshape[period_h] # select period

        weather_yrs_data.append(data_input_selection_hrs)
        weather_yrs_full_year.append(data_input_reshape)

    weather_yrs_data = np.array(weather_yrs_data)

    # Create dataframe
    df = pd.DataFrame(weather_yrs_data, columns=columns)

    df_full_year = pd.DataFrame(weather_yrs_full_year, columns=range(8760))

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
    #data_2015 = data_weather_yr[2015][fueltype_int].reshape(8760)[period_h]

    # ---------------
    # Smoothing lines
    # ---------------
    try:
        period_h_smoothed, df_q_95_smoothed = basic_plot_functions.smooth_data(period_h, df_q_95, num=40000)
        period_h_smoothed, df_q_05_smoothed = basic_plot_functions.smooth_data(period_h, df_q_05, num=40000)
        #period_h_smoothed, data_2015_smoothed = basic_plot_functions.smooth_data(period_h, data_2015, num=40000)
    except:
        period_h_smoothed = period_h
        df_q_95_smoothed = df_q_95
        df_q_05_smoothed = df_q_05
        #data_2015_smoothed = data_2015

    #plt.plot(period_h_smoothed, data_2015_smoothed, color='tomato', linestyle='-', linewidth=2, label="2015 weather_yr")
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

    # -----------------
    # Validation data
    # -----------------
    validation_2015 = validation_elec_2015.reshape(8760)[period_h] 

    try:
        period_h_smoothed, validation_2015_smoothed = basic_plot_functions.smooth_data(period_h, validation_2015, num=40000)
    except:
        period_h_smoothed = period_h
        validation_2015_smoothed = validation_2015

    plt.plot(
        period_h_smoothed,
        validation_2015_smoothed,
        color='green', linestyle='--', linewidth=3, label="validation 2015")

    # -----------------
    # All weather stations are used for this data
    # -----------------
    all_weather_stations_2015 = non_regional_elec_2015.reshape(8760)[period_h] 
    
    try:
        period_h_smoothed, all_weather_stations_2015_smoothed = basic_plot_functions.smooth_data(
            period_h, all_weather_stations_2015, num=40000)
    except:
        period_h_smoothed = period_h
        all_weather_stations_2015_smoothed = all_weather_stations_2015

    # -----------
    # statistics
    # -----------
    # Calculate mean of all all single station runs
    mean_all_single_runs = df_full_year.mean(axis=0).tolist()
    mean_all_single_runs = np.array(mean_all_single_runs)

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        validation_2015,
        all_weather_stations_2015)
    slope, intercept, r_value2, p_value, std_err = stats.linregress(
        validation_2015,
        mean_all_single_runs)
    print("R_Value_all_stations: " + str(r_value))
    print("R_Value_single_stations: " + str(r_value2))
    plt.title("R_value: all stations: {} mean_single_weather_stations: {} ".format(
        round(r_value, 2),
        round(r_value2, 2))
    # Calculate absolute differences
    '''y_diff_abs_all_stations = list(abs(validation_2015 - all_weather_stations_2015))
    y_diff_abs_single_stations = list(abs(validation_2015 - mean_all_single_runs))

    # Calculate difference in percent
    y_diff_p_all_stations = list((100 / validation_2015) * all_weather_stations_2015 - 100)
    y_diff_p_single_stations  = list((100 / validation_2015) * mean_all_single_runs - 100)

    # Statistics calculations
    standard_dev_real_modelled_all_stations = np.std(y_diff_p_all_stations)       # Differences in %
    standard_dev_real_modelled_abs_all_stations = np.std(y_diff_abs_all_stations) # Absolute differences 
    
    standard_dev_real_modelled_single_stations = np.std(y_diff_p_single_stations)       # Differences in %
    standard_dev_real_modelled_abs_single_stations = np.std(y_diff_abs_single_stations) # Absolute differences 

    print("ALL: Standard deviation given as percentage: " + str(standard_dev_real_modelled_all_stations ))
    print("ALL: Standard deviation given as GW:         " + str(standard_dev_real_modelled_abs_all_stations ))
    print("SINGLE: Standard deviation given as percentage: " + str(standard_dev_real_modelled_single_stations ))
    print("SINGLE: Standard deviation given as GW:         " + str(standard_dev_real_modelled_abs_single_stations ))
    plt.title("to all_station: {}  {} {}  {}".format(
        round(standard_dev_real_modelled_all_stations, 2),
        round(standard_dev_real_modelled_abs_all_stations, 2),
        round(standard_dev_real_modelled_single_stations, 2),
        round(standard_dev_real_modelled_abs_single_stations, 2)))'''

    plt.plot(
        period_h_smoothed,
        all_weather_stations_2015_smoothed,
        color='blue',
        linestyle='--',
        linewidth=1,
        label="all weather stations 2015")

    plt.legend(
        prop={
            'family':'arial',
            'size': 10},
        loc='best',
        frameon=False,
        shadow=True)

    plt.show()

    plt.savefig(fig_name)
    plt.close()
