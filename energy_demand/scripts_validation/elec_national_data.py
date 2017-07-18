"""This scripts reads the national electricity data for the base year"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_basic import unit_conversions
#from energy_demand.scripts_technologies import diffusion_technologies as diffusion

def get_month_from_string(month_string):
    """Convert string month to int month with Jan == 1
    """
    if month_string == 'Jan':
        month_int = 1
    elif month_string == 'Feb':
        month_int = 2
    elif month_string == 'Mar':
        month_int = 3
    elif month_string == 'Apr':
        month_int = 4
    elif month_string == 'May':
        month_int = 5
    elif month_string == 'Jun':
        month_int = 6
    elif month_string == 'Jul':
        month_int = 7
    elif month_string == 'Aug':
        month_int = 8
    elif month_string == 'Sep':
        month_int = 9
    elif month_string == 'Oct':
        month_int = 10
    elif month_string == 'Nov':
        month_int = 11
    elif month_string == 'Dec':
        month_int = 12
    else:
        sys.exit("Could not convert string month to int month")

    return int(month_int)

def read_raw_elec_2015_data(path_to_csv):
    """Read in national electricity values provided in MW and convert to GWh

    Info
    -----
    Half hourly measurements are aggregated to hourly values

    Necessary data preparation: On 29 March and 25 Octobre there are 46 and 48 values because of the changing of the clocks
    The 25 Octobre value is omitted, the 29 March hour interpolated in the csv file
    """
    year = 2015
    total_MW = 0

    elec_data = np.zeros((365, 24))

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        hour = 0
        counter_half_hour = 0
        # Iterate rows
        for line in read_lines:

            month = get_month_from_string(line[0].split("-")[1])
            day = int(line[0].split("-")[0])

            # Get yearday
            yearday = date_handling.convert_date_to_yearday(year, month, day)

            if counter_half_hour == 1:
                counter_half_hour = 0

                # Sum value of first and second half hour
                hour_elec_demand = half_hour_demand + float(line[2])
                total_MW += hour_elec_demand

                # Convert MW to GWH (input is MW aggregated for two half
                # hourly measurements, therfore divide by 0.5)
                hour_elec_demand_gwh = unit_conversions.convert_mw_gwh(hour_elec_demand, 0.5)

                # Add to array
                #print(" sdf  {}  {}  {}  ".format(yearday, hour, hour_elec_demand_gwh))
                elec_data[yearday][hour] = hour_elec_demand_gwh

                hour += 1
            else:
                counter_half_hour += 1

                half_hour_demand = float(line[2])

            if hour == 24:
                hour = 0

    return elec_data

def compare_results(y_real_array, y_calculated_array, title_left, days_to_plot):
    """Compare national electrictiy demand data with model results

    Info
    ----
    RMSE fit criteria : Lower values of RMSE indicate better fit
    https://stackoverflow.com/questions/17197492/root-mean-square-error-in-python
    """
    print("...compare elec results")
    def rmse(predictions, targets):
        """RMSE calculations
        """
        return np.sqrt(((predictions - targets) ** 2).mean())

    # Number of days to plot
    #days_to_plot = list(range(0, 14)) + list(range(100, 114)) + list(range(200, 214)) + list(range(300, 314))

    nr_of_h_to_plot = len(days_to_plot) * 24

    x = range(nr_of_h_to_plot)

    y_real = []
    y_calculated = []

    for day in days_to_plot:
        for hour in range(24):
            y_real.append(y_real_array[day][hour])
            y_calculated.append(y_calculated_array[day][hour])

    # RMSE
    rmse_val = rmse(np.array(y_real), np.array(y_calculated))

    # plot points
    plt.plot(x, y_real, color='green', label='real') #'ro', markersize=1
    plt.plot(x, y_calculated, color='red', label='modelled') #'ro', markersize=1

    plt.title('RMSE Value: {}'.format(rmse_val))
    plt.title(title_left, loc='left')
    #plt.title('Right Title', loc='right')
    plt.legend()

    plt.show()

def compare_peak(validation_elec_data_2015, peak_all_models_all_enduses_fueltype):
    """Compare Peak electricity day with calculated peak energy demand
    """
    print("...compare elec peak results")
    # -------------------------------
    # Find maximumg peak in real data
    # -------------------------------
    peak_day_real = np.zeros((24))

    max_h_year = 0
    max_day = "None"

    for day in range(365):
        max_h_day = np.max(validation_elec_data_2015[day])

        if max_h_day > max_h_year:
            max_h_year = max_h_day
            max_day = day

    print("Max Peak Day:                    " + str(max_day))
    print("max_h_year (real):               " + str(max_h_year))
    print("max_h_year (modelled):           " + str(np.max(peak_all_models_all_enduses_fueltype)))
    print("Fuel max peak day (real):        " + str(np.sum(validation_elec_data_2015[max_day])))
    print("Fuel max peak day (modelled):    " + str(np.sum(peak_all_models_all_enduses_fueltype)))
    # -------------------------------
    # Compare values
    # -------------------------------
    '''#Scrap
    a = []
    for day in range(365):
        for hour in range(24):
            a.append(validation_elec_data_2015[day][hour])
    plt.plot(range(8760), a, color='green', label='real')
    plt.show()
    '''

    x = range(24)
    plt.plot(x, peak_all_models_all_enduses_fueltype, color='red', label='modelled')
    plt.plot(x, validation_elec_data_2015[max_day], color='green', label='real')

    plt.axis('tight')
    plt.title("Peak day comparison", loc='left')
    plt.xlabel("Hours")
    plt.ylabel("National electrictiy use [GWh]")
    plt.legend()
    plt.show()

def compare_results_hour_boxplots(data_real, data_calculated):

    data_months_real = {}
    data_months_calculated = {}

    for i in range(12):
        data_months_real[i] = []
        data_months_calculated[i] = []

    for yearday_python in range(365):

        # Yerday
        date_object = date_handling.convert_yearday_to_date(2015, yearday_python)

        # Month
        month = date_object.timetuple().tm_mon - 1


        # Dict with real data
        data_months_real[month] += list(data_real[yearday_python])
        data_months_calculated[month] +=  list(data_calculated[yearday_python])

    fig = plt.figure()
    ax = fig.add_subplot(111)

    months_real = data_months_real.items()
    months_calculated = data_months_calculated.items()

    ax.boxplot(months_real)
    ax.boxplot(months_calculated)
    plt.show()
