""" new load profile generator """
import numpy as np
import os
import csv
import main_functions as mf

from datetime import date
import unittest
import matplotlib.pyplot as plt

# Dictioneriers for over full year

day_p_of_year = np.empty((365, 1), dtype=float)  
h_p_of_day = np.empty((365, 24), dtype=float)

peak_h_max = np.empty((1,24), dtype=float)
peak_h_min = np.empty((1,24), dtype=float)


'''
h_dict = {
    'end_use':
        {
        'peak_h_max': peak_h_max,
        'normal_h': h_p_of_day,
        'peak_h_min': peak_h_min
        },
    }

d_dict = {
    'end_use':
        {
        'peak_day_max': day_max,
        'normal_day': d_p_of_day,
        'peak_day_min': peak_h_min
        },
    }
'''



def read_HES_data(data, data_ext, paths_HES, end_use):
    '''
    Read in HES and give out for every yearday all types.

    # TODO: Don't read in HES relsted paramters but save them here (e.g. appliances)

    # NOTES: Peak Demand is stored in Month January = 0
    '''
    # DATA
    daytype_lu = data['day_type_lu'] #0: Weekd_day, 1: Weekend, 2 : Coldest, 3 : Warmest
    app_type_lu = data['app_type_lu']
    base_year = data_ext['glob_var']['base_year']

    # Read in raw HES data from CSV
    raw_elec_data = mf.read_csv(paths_HES)

    # initialise
    year_days = 365
    month_nr = 12
    hours = 24

    
    hes_data = np.zeros((len(daytype_lu), month_nr, hours, len(app_type_lu)), dtype=float)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month, daytype, appliance_typ = int(row[0]), int(row[1]), int(row[2])
        k_header = 3    # TODO: Check if in excel data starts here

        # iterate over hour
        for hour in range(hours):
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000)) # [kWH electric] Converts the summed watt into kWH
            hes_data[daytype][month][hour][appliance_typ] = _value
            k_header += 1
    return hes_data




def assign_HES_data_to_year(data, hes_data, data_ext):
    ''' Fill every base year day with correct data '''
    base_year = data_ext['glob_var']['base_year']

    year_days = 365
    month_nr = 12
    hours = 24
    app_type_lu = data['app_type_lu']

    year_raw_values = np.zeros((year_days, hours, len(app_type_lu)), dtype=float)

    # Create list with all dates of a whole year
    start_date, end_date = date(base_year, 1, 1), date(base_year, 12, 31)
    list_dates = list(mf.datetime_range(start=start_date, end=end_date))

    # Assign every date to the place in the array of the year
    for yearday in list_dates:
        _info = yearday.timetuple()
        month_python = _info[1] - 1       # - 1 because in _info: Month 1 = Jan
        yearday_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        daytype = mf.get_weekday_type(yearday)

        _data = hes_data[daytype][month_python] # Get day from HES raw data array

        # Add values to yearly array
        year_raw_values[yearday_python] = _data   # now [yearday][hour][appliance_typ] 

    return year_raw_values


def get_HES_end_uses_shape(data, hes_data, year_raw_values, end_use):
    ''' read out end-use shape'''
    # Calculate yearly total demand over all day years and all appliances

    # -----------------------------------
    # Peak calculation
    # -----------------------------------
    
    #-- daily peak
    # Relationship of total yearly demand with averaged values and a peak day
    appliances_HES = data['app_type_lu']

    # Get end use of HES data of current end_use of EUREC Data
    for i in data['lu_appliances_HES_matched']:
        if i[1] == end_use:
            hes_app_id = int(i[0])
            break

    # Select end use daily peak demand
    peak_h_values = hes_data[2][0][:, hes_app_id]

    total_d_peak_demand = np.sum(peak_h_values)  # Peak is stored in JAN READ_IN HES DATA 2: PEak, 0: January, Select column

    # Total yearly demand of end_use
    total_y_end_use_demand = np.sum(year_raw_values[:, :, hes_app_id]) 

    # Factor to calculate daily peak demand from total
    factor_to_calc_daily_peak_from_y_tot = (100/total_y_end_use_demand) * total_d_peak_demand

    print("total_d_peak_demand: " + str(total_d_peak_demand))
    print("total_y_end_use_demand: " + str(total_y_end_use_demand))
    print("yfactor_to_calc_daily_peak_from_y_tot: " + str(factor_to_calc_daily_peak_from_y_tot))

    # -----------------------------------
    # Get peak daily load shape
    # -----------------------------------

    #-- hourly shape [% of total daily]
    peak_h_shape = hes_data[2][0][:, hes_app_id] / total_d_peak_demand
    print("peak_h_shape: " + str(peak_h_shape))
    print("sum: " + str(np.sum(peak_h_shape)))

    # -------------------------
    # Calculate non-peak shapes
    # -------------------------
    shape_d_non_peak = np.zeros((365,))
    shape_h_non_peak = np.zeros((365, 24))

    for day in range(365):
        d_sum = np.sum(year_raw_values[day, :, hes_app_id])
        shape_d_non_peak[day] = (100 / total_y_end_use_demand) * d_sum

        # daily shape
        shape_h_non_peak[day] = (100 / d_sum) * year_raw_values[day, :, hes_app_id]

    # Add to hourly shape
    data['dict_shapes_end_use_h'][end_use] = {'peak_h_shape': peak_h_shape, 'factor_to_calc_daily_peak_from_y_tot': factor_to_calc_daily_peak_from_y_tot} 

    # Add to daily shape
    data['dict_shapes_end_use_day'][end_use]  = {'shape_d_non_peak': shape_d_non_peak, 'shape_h_non_peak': shape_h_non_peak} 

    return data 
