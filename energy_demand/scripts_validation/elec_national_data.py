"""This scripts reads the national electricity data for the base year"""
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
import pylab
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_basic import unit_conversions
from energy_demand.scripts_technologies import diffusion_technologies as diffusion

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
                hour_elec_demand_gwh = unit_conversions.convert_mw_gwh(hour_elec_demand, 0.5) #1)

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

def compare_results(y_real_array, y_calculated_array, title_left):
    """plot full year

    Info
    ----
    RMSE fit criteria : Lower values of RMSE indicate better fit
    https://stackoverflow.com/questions/17197492/root-mean-square-error-in-python
    """
    def rmse(predictions, targets):
        """RMSE calculations
        """
        return np.sqrt(((predictions - targets) ** 2).mean())

    print("plot and compare calculated and real for year 2015")
    # Set figure size in cm
    #plt.scatter(x, y)

    # Number of days to plot
    #days_to_plot = range(70, 100) #range(0,365)
    days_to_plot = list(range(0, 14)) + list(range(100, 114)) + list(range(200, 214)) + list(range(300, 314))

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
    plt.plot(x, y_real, color='green', label='real') #'ro', markersize=1, # REAL DATA
    plt.plot(x, y_calculated, color='red', label='modelled') #'ro', markersize=1 #Calculated

    plt.title('RMSE Value: {}'.format(rmse_val))
    plt.title(title_left, loc='left')
    #plt.title('Right Title', loc='right')
    plt.legend()

    plt.show()
    