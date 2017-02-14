# This file stores all functions of main.py
print ("Loading main functions")

import csv
import sys
#import pandas as pd
import datetime
from datetime import date, timedelta as td

import numpy as np


def read_csv(path_to_csv):
    """
    This function reads in CSV files and skip header row.

    Input:
    -path_to_csv              Path to CSV file
    -dtypesList             List contining dtypes of columns

    Output:
    -elements_array         Array containing whole CSV file entries
    """
    with open(path_to_csv, 'r') as csvfile:              # Read CSV file
        list_elements = []
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines) # Skip first row

        # Rows
        for row in read_lines:
            list_elements.append(row)

    elements_array = np.array(list_elements)    # Convert list into array
    return elements_array


def generate_sim_period(date_list, reg_lookup, fuel_type_lookup, appliance_type_lu):
    '''
    This function creates the simulation time steps for which the energy demand is calculated.
    '''

    # Region, Fuel, 
    time_steps = range(4 * 7 * 24) # four weeks hourly
    hours = range(24)

    # Initialise
    time_steps = np.zeros((len(reg_lookup), len(fuel_type_lookup), len(time_steps), len(appliance_type_lu), len(hours)), dtype=float)

    for i in date_list:
        start_date = i[0]
        end_date = i[1]
        list_dates = list(datetime_range(start=start_date, end=end_date))

        for j in list_dates:
            _info = j.timetuple()
            month = _info[1] # Month 1: Jan
            month_python = month - 1
            year_day = _info[7] # Day nr of the year 1.Jan = 1
            year_day_python = year_day - 1
            weekday = _info[6] # 0: Monday
            


    #len_periods = len(days) * len(hours)
    sim_iteration_steps = np.zeros((len(seasons), len(days), len(hours)))


    return time_steps

def shape_base_resid_appliances(path_base_elec_load_profiles, day_type_lu, appliance_type_lu, base_year):
    '''
    This function reads in the HES eletricity load profiles
    of the base year and stores them in form of an array.
    First the absolute values are stored in a HES dictionary
    for the different month and day-types. Then the total
    demand of the year is calculated and all array entries
    calculated as percentage of the total demand.

    #TODO: expand for different regions, different dwelling types, fuels...

    Input:
    -path_base_elec_load_profiles   Path to .csv file with HSE data
    -season_lookup                  Lookup dictionary with seasons
    -day_type_lu                    Lookup dictionary with type of days
    -appliance_type_lu              Looup dictionary containing all appliances
    -base_year                      Base year

    Output:
    -appliances_shape               [%] Array containing the shape of appliances
                                    for every day in the base year
                                    Within each month, the same load curves are
                                    used for every working/holiday day.
        year_days of base year
            appliance_typ
                hour
    '''
    # Initilaise array to store all values for a year
    year_days = range(365)
    month_nr = range(12)
    hours = range(24)
    year_raw_values = np.zeros((len(year_days), len(appliance_type_lu), len(hours)), dtype=float)

    # Initialise HES dictionary with every month and day-type
    hes_data = np.zeros((len(day_type_lu), len(month_nr), len(appliance_type_lu), len(hours)), dtype=float)

    # Read in energy profiles of base_year
    raw_elec_data = read_csv(path_base_elec_load_profiles)

    for row in raw_elec_data: # Iterate raw data of hourly eletrictiy demand
        month = int(row[0])
        day_typ = int(row[1])
        appliance_typ = int(row[2])
        k_header = 3    # Check if in excel data starts here

        for hour in hours: # iterate over hour
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000)) # [kWH electric] Converts the summed watt into kWH
            #_value = float(row[k_header])  #REMOVE
            hes_data[day_typ][month][appliance_typ][hour] = _value
            k_header += 1

    # Create list with all dates of a year
    start_date = date(base_year, 1, 1)
    end_date = date(base_year, 12, 31)

    list_dates = list(datetime_range(start=start_date, end=end_date))
    #print("Nr of dates: " + str(len(list_dates)))

    if len(list_dates) != 365:
        print ("ERROR: year has 366 day and not 365.... ")
        sys.exit()
    
    # Assign every date to the place in the array of the year
    for dateInYear in list_dates:
        _info = dateInYear.timetuple()
        month = _info[1] # Month 1: Jan
        month_python = month - 1
        year_day = _info[7] # Day nr of the year 1.Jan = 1
        year_day_python = year_day - 1
        weekday = _info[6] # 0: Monday
        #weekday = dateInYear.weekday()   # Get weekday
        #dateInYear.month # Get Month
        #dateInYear.day   # Get day

        if weekday == 5 or weekday == 6: # Weekend
            holiday = True
            day_typ = 1
        else:
            holiday = False
            day_typ = 0

        # Get day from HES base data array
        _data = hes_data[day_typ][month_python]

        # Add values to yearly array
        for h in hours:
            year_raw_values[year_day_python] = _data
            #print("year_raw_values[year_day]: "  + str(year_raw_values[year_day]))

    # Calculate yearly total demand over all day years and all appliances
    total_y_demand = year_raw_values.sum()

    # Calculate Shape of the eletrictiy distribution of the appliances by assigning percent values each
    appliances_shape = np.zeros((len(year_days), len(appliance_type_lu), len(hours)), dtype=float)
    appliances_shape = (100/float(total_y_demand)) * year_raw_values
    return appliances_shape


def datetime_range(start=None, end=None):
    '''
    This function calculates all dates between a star and end date.
    '''

    span = end - start
    for i in range(span.days + 1):
        yield start + td(days=i)
















# ------------scrap
'''
def attributeRealVAlues():
    _share_jan = float(31)/float(365)
    _share_feb = float(28)/float(365)
    return



def assignSeasonToMonth(month):
    
    ASsign month to season according to lookup_season.csv

    Input:
    -month (0: Jan)

    Output:
    -season (0: Winter)
    
    if month == 11 or month == 0 or month == 1:
        season = 0
    elif month == 2 or month == 3 or month == 4:
        season = 1
    elif month == 5 or month == 6 or month == 7:
        season = 2
    elif month == 8 or month == 9 or month == 10:
        season = 3

    return season
'''

'''
def read_csv(path_to_csv, dtypesList):
    """
    This function reads in CSV files and skip header row.

    Input:
    -path_to_csv              Path to CSV file
    -dtypesList             List contining dtypes of columns

    Output:
    -elements_array         Array containing whole CSV file entries
    """

    with open(path_to_csv, 'r') as csvfile:              # Read CSV file
        list_elements = []
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line

        # Headings of CSV file (first row)
        #for row in read_lines:
        #    colum_headings = row
        #    break
        #print(":::::::::::::::TEST")
        #for row in read_lines:
        #    print row
        #    break

        headings = next(read_lines)
        #next(read_lines)  # Skip first position (headings)
        print (":....")
        print (headings)

        headingsList = []
        for i in headings:
            headingsList.append(str(i))

        headingsList = tuple(headingsList) #convert to tuple

        #dtypesList = ('S20', 'i4')
        print ("eee: " + str(headingsList))

        #test = zip(headingsList, dtypesList)
        test = map(lambda x,y:(x,y),headingsList,dtypesList)
        print ("f: " + str(test))
        test2 = []
        for i in test:
            print ("test: " + str(i))
            test2.append(list(i))

        # Rows
        for row in read_lines:
            

            list_elements.append(tuple(row))


    print ("list_elements: " + str(list_elements))
    print(test2)
    #dt = np.dtype(test2)
    #elements_array = np.array(list_elements, dtype=dt)    # Convert list into array
    elements_array = np.array((list_elements), dtype=test2)    # Convert list into array

    print ("........dd....")
    print (elements_array)

    r = 0
    for i in elements_array:
        r += i[1]
    print (r)
    print ("finish")


    return elements_array
    '''

'''
def get_days_month(month):

    This function returns all days of a month where the year is numbered from 0 to 364.

    Input:
    -month  #Jan = 0

    Output:
    -day        : list containing all days 0 = 1. January
    # https://landweb.modaps.eosdis.nasa.gov/browse/calendar.html (always - 1)


    if month == 0:
        days = range(31)
    elif month == 1:
        days = range(31,59)
    elif month == 2:
        days = range(59,90)
    elif month == 3:
        days = range(90,120)
    elif month == 4:
        days = range(120,151)
    elif month == 5:
        days = range(151,181)
    elif month == 6:
        days = range(181,212)
    elif month == 7:
        days = range(212,243)
    elif month == 8:
        days = range(243,273)
    elif month == 9:
        days = range(273,304)
    elif month == 10:
        days = range(304,334)
    elif month == 11:
        days = range(334,365)
    return days
'''

'''def get_Nr_Of_hollidays_wd(info_year):

    #This function reads the number of working and holidays of a year#

    monthList = {}

    #days_per_month = [(0, 31), (1, 28), (2, 31), (3,30), (4, 31), (5, 30), (6, 31), (7, 31), (8, 30), (9, 31), (10, 30), (11,31)]

    jan_wd = np.busday_count(str(info_year) + str('-01-01'), str(info_year) + str('-01-31'))
    feb_wd = np.busday_count(str(info_year) + str('-02-01'), str(info_year) + str('-02-28'))
    march_wd = np.busday_count(str(info_year) + str('-03-01'), str(info_year) + str('-03-31'))
    april_wd = np.busday_count(str(info_year) + str('-04-01'), str(info_year) + str('-04-30'))
    may_wd = np.busday_count(str(info_year) + str('-05-01'), str(info_year) + str('-05-31'))
    june_wd = np.busday_count(str(info_year) + str('-06-01'), str(info_year) + str('-06-30'))
    july_wd = np.busday_count(str(info_year) + str('-07-01'), str(info_year) + str('-07-31'))
    august_wd = np.busday_count(str(info_year) + str('-08-01'), str(info_year) + str('-08-31'))
    september_wd = np.busday_count(str(info_year) + str('-09-01'), str(info_year) + str('-09-30'))
    october_wd = np.busday_count(str(info_year) + str('-10-01'), str(info_year) + str('-10-31'))
    november_wd = np.busday_count(str(info_year) + str('-11-01'), str(info_year) + str('-11-30'))
    december_wd = np.busday_count(str(info_year) + str('-12-01'), str(info_year) + str('-12-31'))
    
    jan_holidays = 31-jan_wd
    feb_holidays = 28-feb_wd
    march_holidays = 31-march_wd
    april_holidays = 30-april_wd
    may_holidays = 31-may_wd
    june_holidays = 30-june_wd
    july_holidays = 31-july_wd
    august_holidays = 31-august_wd
    september_holidays = 30-september_wd
    october_holidays = 31-october_wd
    november_holidays = 30-november_wd
    december_holidays = 31-december_wd

    monthList[0] = [jan_wd, jan_holidays]
    monthList[1] = [feb_wd, feb_holidays]
    monthList[2] = [march_wd, march_holidays]
    monthList[3] = [april_wd, april_holidays]
    monthList[4] = [may_wd, may_holidays]
    monthList[5] = [june_wd, june_holidays]
    monthList[6] = [july_wd, july_holidays]
    monthList[7] = [august_wd, august_holidays]
    monthList[8] = [september_wd, september_holidays]
    monthList[9] = [october_wd, october_holidays]
    monthList[10] = [november_wd, november_holidays]
    monthList[11] = [december_wd, december_holidays]

    return monthList
'''