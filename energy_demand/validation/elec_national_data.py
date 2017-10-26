"""This scripts reads the national electricity data for the base year"""
import os
import sys
import csv
import logging
import numpy as np
import matplotlib.pyplot as plt
from energy_demand.basic import date_handling
from energy_demand.basic import conversions
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions
from collections import defaultdict

def get_month_from_string(month_string):
    """Convert string month to int month with Jan == 1

    Argument
    --------
    month_string : str
        Month given as a string
    
    Returns
    --------
    month : int
        Month as an integer (jan = 1, dez = 12)
    """
    if month_string == 'Jan':
        month = 1
    elif month_string == 'Feb':
        month = 2
    elif month_string == 'Mar':
        month = 3
    elif month_string == 'Apr':
        month = 4
    elif month_string == 'May':
        month = 5
    elif month_string == 'Jun':
        month = 6
    elif month_string == 'Jul':
        month = 7
    elif month_string == 'Aug':
        month = 8
    elif month_string == 'Sep':
        month = 9
    elif month_string == 'Oct':
        month = 10
    elif month_string == 'Nov':
        month = 11
    elif month_string == 'Dec':
        month = 12
    else:
        sys.exit("Could not convert string month to int month")

    return int(month)

def read_raw_elec_2015_data(path_to_csv):
    """Read in national electricity values provided in MW and convert to GWh

    Note
    -----
    Half hourly measurements are aggregated to hourly values

    Necessary data preparation: On 29 March and 25 Octobre 
    there are 46 and 48 values because of the changing of the clocks
    The 25 Octobre value is omitted, the 29 March hour interpolated in the csv file
    """
    year = 2015

    elec_data_INDO = np.zeros((365, 24), dtype=float)
    elec_data_ITSDO = np.zeros((365, 24), dtype=float)

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') 
        _headings = next(read_lines) # Skip first row

        hour = 0
        counter_half_hour = 0

        for line in read_lines:
            month = get_month_from_string(line[0].split("-")[1])
            day = int(line[0].split("-")[0])

            # Get yearday
            yearday = date_handling.date_to_yearday(year, month, day)

            if counter_half_hour == 1:
                counter_half_hour = 0

                # Sum value of first and second half hour
                hour_elec_demand_INDO = half_hour_demand_INDO + float(line[2]) # INDO - National Demand
                hour_elec_demand_ITSDO = half_hour_demand_ITSDO + float(line[4]) # ITSDO - Transmission System Demand

                # Convert MW to GWH (input is MW aggregated for two half
                # hourly measurements, therfore divide by 0.5)
                hour_elec_demand_gwh_INDO = conversions.mw_to_gwh(hour_elec_demand_INDO, 0.5)
                hour_elec_demand_gwh_ITSDO = conversions.mw_to_gwh(hour_elec_demand_ITSDO, 0.5)

                # Add to array
                #logging.debug(" sdf  {}  {}  {}  ".format(yearday, hour, hour_elec_demand_gwh))
                elec_data_INDO[yearday][hour] = hour_elec_demand_gwh_INDO
                elec_data_ITSDO[yearday][hour] = hour_elec_demand_gwh_ITSDO

                hour += 1
            else:
                counter_half_hour += 1

                half_hour_demand_INDO = float(line[2]) # INDO - National Demand
                half_hour_demand_ITSDO = float(line[4]) # Transmission System Demand

            if hour == 24:
                hour = 0

    return elec_data_INDO, elec_data_ITSDO

def compare_results(name_fig, data, y_real_array_INDO, y_real_array_ITSDO, y_factored_INDO, y_calculated_array, title_left, days_to_plot):
    """Compare national electrictiy demand data with model results

    Note
    ----
    RMSE fit criteria : Lower values of RMSE indicate better fit
    https://stackoverflow.com/questions/17197492/root-mean-square-error-in-python
    """
    logging.debug("...compare elec results")
    nr_of_h_to_plot = len(days_to_plot) * 24

    x = range(nr_of_h_to_plot)

    y_real_INDO = []
    y_real_ITSDO = []
    y_real_INDO_factored = []
    y_calculated = []

    for day in (days_to_plot):
        for hour in range(24):
            y_real_INDO.append(y_real_array_INDO[day][hour])
            y_real_ITSDO.append(y_real_array_ITSDO[day][hour])
            y_calculated.append(y_calculated_array[day][hour])
            y_real_INDO_factored.append(y_factored_INDO[day][hour])

    # -------------------
    # Smoothing algorithm
    # -------------------
    #y_calculated = savitzky_golay(y_calculated, 3, 3) # window size 51, polynomial order 3

    # RMSE
    rmse_val_INDO = basic_functions.rmse(np.array(y_real_INDO), np.array(y_calculated))
    rmse_val_ITSDO = basic_functions.rmse(np.array(y_real_ITSDO), np.array(y_calculated))
    rmse_val_corrected = basic_functions.rmse(np.array(y_real_INDO_factored), np.array(y_calculated))
    rmse_val_own_factor_correction = basic_functions.rmse(np.array(y_real_INDO), np.array(y_calculated))

    # R squared
    #slope, intercept, r_value, p_value, std_err = stats.linregress(np.array(y_real_INDO), np.array(y_calculated))

    # plot points
    plt.plot(x, y_real_INDO, color='black', label='TD') #'ro', markersize=1
    plt.plot(x, y_real_ITSDO, color='grey', label='TSD') #'ro', markersize=1
    plt.plot(x, y_real_INDO_factored, color='green', label='TD_factored') #'ro', markersize=1
    plt.plot(x, y_calculated, color='red', label='modelled') #'ro', markersize=1

    plt.xlim([0, 8760])
    plt.margins(x=0) #remove white space
    plt.axis('tight')

    plt.title('RMSE (TD): {}  RMSE (TSD):  {} RMSE (factored TSD): {}'.format(rmse_val_INDO, rmse_val_ITSDO, rmse_val_corrected), fontsize=10)
    plt.title(title_left, loc='left')

    plt.xlabel("Hours", fontsize=10)
    plt.ylabel("National electrictiy use [GWh / h]", fontsize=10)
    
    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], name_fig))

    plt.legend()

    if data['print_criteria'] == True:
        plt.show()
    else:
        pass

def compare_peak(name_fig, data, validation_elec_data_2015, tot_peak_enduses_fueltype):
    """Compare Peak electricity day with calculated peak energy demand

    TODO: IMPROVE:
    """
    logging.debug("...compare elec peak results")
    # -------------------------------
    # Find maximumg peak in real data
    # -------------------------------
    max_h_year = 0
    max_day = "None"

    for day in range(365):
        max_h_day = np.max(validation_elec_data_2015[day])

        if max_h_day > max_h_year:
            max_h_year = max_h_day
            max_day = day

    logging.debug("Max Peak Day:                    %s", max_day)
    logging.debug("max_h_year (real):               %s", max_h_year)
    logging.debug("max_h_year (modelled):           %s", np.max(tot_peak_enduses_fueltype))
    logging.debug("Fuel max peak day (real):        %s", np.sum(validation_elec_data_2015[max_day]))
    logging.debug("Fuel max peak day (modelled):    %s", np.sum(tot_peak_enduses_fueltype))

    # -------------------------------
    # Compare values
    # -------------------------------
    x = range(24)

    plt.figure(figsize=plotting_program.cm2inch(8, 8))

    plt.plot(x, tot_peak_enduses_fueltype, color='red', label='modelled')
    plt.plot(x, validation_elec_data_2015[max_day], color='green', label='real')

    # Y-axis ticks
    #plt.ylim(0, 80)
    plt.xlim(0, 25)
    plt.yticks(range(0, 90, 10))

    #plt.axis('tight')
    plt.title("Peak day comparison", loc='left')
    plt.xlabel("Hours")
    plt.ylabel("National electrictiy use [GWh / h]")
    plt.legend()
    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], name_fig))

    if data['print_criteria']:
        plt.show()
    else:
        pass

    return

def compare_results_hour_boxplots(name_fig, data, data_real, data_calculated):
    """Calculate differences for every hour and plot according to hour
    for the full year
    """
    data_h_full_year = {}
    for i in range(24):
        data_h_full_year[i] = []

    for yearday_python in range(365):
        for hour in range(24):

            # Calculate difference in electricity use
            diff = data_real[yearday_python][hour] - data_calculated[yearday_python][hour]

            # Differenc in % of real value
            diff_percent = (100 / data_real[yearday_python][hour]) * data_calculated[yearday_python][hour]

            # Add differene to list of specific hour
            data_h_full_year[hour].append(diff_percent)

    fig = plt.figure()

    ax = fig.add_subplot(111)

    # Add a horizontal grid to the plot, but make it very light in color so we can use it for reading data values but not be distracting
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax.axhline(y=100, xmin=0, xmax=3, c="red", linewidth=1, zorder=0)

    diff_values = []
    for hour in range(24):
        diff_values.append(np.asarray(data_h_full_year[hour]))

    ax.boxplot(diff_values)

    plt.xticks(range(1, 25), range(24))
    #plt.margins(x=0) #remove white space

    plt.xlabel("Hour")
    #plt.ylabel("Modelled electricity difference (real-modelled) [GWh / h]")
    plt.ylabel("Modelled electricity difference (real-modelled) [%]")

    plt.savefig(os.path.join(data['local_paths']['data_results_PDF'], name_fig))


    if data['print_criteria']:
        plt.show()
    else:
        pass

    return
