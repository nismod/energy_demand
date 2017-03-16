
import energy_demand.main_functions as mf
import numpy as np
import os
import csv
import main_functions as mf
from datetime import date
import unittest
import matplotlib.pyplot as plt
import data_loader_functions as df

def read_hes_data(data):
    '''
    Read in HES and give out for every yearday all types.

    # TODO: Don't read in HES relsted paramters but save them here (e.g. appliances)

    # NOTES: Yearly peak demand is stored in Month January = 0
    # Improve: Could read in shape of HES nicer (e.g. peak seperately)
    '''
    # initialise
    paths_hes = data['path_dict']['path_bd_e_load_profiles']
    daytype_lu = data['day_type_lu'] #0: Weekd_day, 1: Weekend, 2 : Coldest, 3 : Warmest
    app_type_lu = data['app_type_lu']
    month_nr = 12
    hours = 24
    hes_data = np.zeros((len(daytype_lu), month_nr, hours, len(app_type_lu)), dtype=float)

    hes_y_peak = np.zeros((hours, len(app_type_lu)))
    hes_y_warmest = np.zeros((hours, len(app_type_lu)))

    # Read in raw HES data from CSV
    raw_elec_data = mf.read_csv(paths_hes)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month, daytype, appliance_typ = int(row[0]), int(row[1]), int(row[2])
        k_header = 3    # TODO: Check if in excel data starts here

        # iterate over hour  = row in csv file
        for hour in range(hours):
            # [kWH electric] Converts the summed watt into kWH TODO: Is not necessary as we are only calculating in relative terms
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000))

            # if coldest (see HES file)
            if daytype == 2:
                hes_y_peak[hour][appliance_typ] = _value
                k_header += 1
                continue

            if daytype == 3:
                hes_y_warmest[hour][appliance_typ] = _value
                k_header += 1
                continue

            hes_data[daytype][month][hour][appliance_typ] = _value
            k_header += 1

    return hes_data, hes_y_peak, hes_y_warmest



def assign_hes_data_to_year(data, hes_data, base_year):
    ''' Fill every base year day with correct data '''

    year_days = 365
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


def get_hes_end_uses_shape(data, hes_data, year_raw_values, hes_y_peak, hes_y_warmest, end_use):
    ''' read out end-use shape'''
    # Calculate yearly total demand over all day years and all appliances

    # -----------------------------------
    # Peak calculation
    # -----------------------------------
    #Todo: Warmest load shape is not usd.abs

    #-- daily peak
    # Relationship of total yearly demand with averaged values and a peak day
    appliances_HES = data['app_type_lu']

    # If enduse is not in data
    print(data['lu_appliances_HES_matched'])
    if end_use not in data['lu_appliances_HES_matched'][:, 1]:
        print("Enduse not HES data: " + str(end_use))
        return data

    # Get end use of HES data of current end_use of EUREC Data
    for i in data['lu_appliances_HES_matched']:
        if i[1] == end_use:
            hes_app_id = int(i[0])
            break

    # Select end use daily peak demand
    peak_h_values = hes_y_peak[:, hes_app_id]

    total_d_peak_demand = np.sum(peak_h_values)  # Peak is stored in JAN READ_IN HES DATA 2: PEak, 0: January, Select column

    # Total yearly demand of end_use
    total_y_end_use_demand = np.sum(year_raw_values[:, :, hes_app_id]) 

    # Factor to calculate daily peak demand from total
    peak_d_shape = (100/total_y_end_use_demand) * total_d_peak_demand

    print("total_d_peak_demand: " + str(total_d_peak_demand))
    print("total_y_end_use_demand: " + str(total_y_end_use_demand))
    print("ypeak_d_shape: " + str(peak_d_shape))

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
    shape_d_non_peak = np.zeros((365, 1))
    shape_h_non_peak = np.zeros((365, 24))

    for day in range(365):
        d_sum = np.sum(year_raw_values[day, :, hes_app_id])
        shape_d_non_peak[day] = (100 / total_y_end_use_demand) * d_sum

        # daily shape
        shape_h_non_peak[day] = (100 / d_sum) * year_raw_values[day, :, hes_app_id]

    # Add to hourly shape
    data['dict_shapes_end_use_h'][end_use] = {'peak_h_shape': peak_h_shape, 'shape_h_non_peak': shape_h_non_peak}

    # Add to daily shape
    data['dict_shapes_end_use_d'][end_use]  = {'peak_d_shape': peak_d_shape, 'shape_d_non_peak': shape_d_non_peak}
    return data




def shape_residential_heating_gas(data, end_use):
    """
    This function creates the shape of the base year heating demand over the full year

    #Todo: Different shapes depending on workingday/holiday

    Input:
    -csv_temp_2015      SNCWV temperatures for every gas-year day
    -hourly_gas_shape   Shape of hourly gas for Day, weekday, weekend (Data from Robert Sansom)

    """

    # Read in temperatures for base year
    csv_temp_2015 = mf.read_csv(data['path_dict']['path_temp_2015'])
    hourly_gas_shape = mf.read_csv_float(data['path_dict']['path_hourly_gas_shape'])
    #print("hourly_gas_shape " + str(hourly_gas_shape))

    data['csv_temp_2015'] = csv_temp_2015
    #add hourly data

    # Initilaise array to store all values for a year
    year_days, hours = 365, 24
    hourly_hd = np.zeros((1, hours), dtype=float)
    hd_data = np.zeros((year_days, hours), dtype=float)     # Initialise dictionary with every day and hour
    #shape_hd = np.zeros((year_days, hours), dtype=float)

    # Get hourly distribution (Sansom Data)
    hourly_gas_shape_day = hourly_gas_shape[0]      # Hourly gas shape
    hourly_gas_shape_wkday = hourly_gas_shape[1]    # Hourly gas shape
    hourly_gas_shape_wkend = hourly_gas_shape[2]    # Hourly gas shape

    # Read in SNCWV and calculate heating demand for every yearday
    for row in csv_temp_2015:
        sncwv = float(row[1])
        row_split = row[0].split("/")
        _day = int(row_split[0])
        _month = int(row_split[1])
        _year = int(row_split[2])
        date_gas_day = date(_year, _month, _day)
        _info = date_gas_day.timetuple()
        yearday_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        weekday = _info[6]                # 0: Monday

        # Calculate demand based on correlation Source: Correlation taken from CWV and Seasonsal Normal demands Rolling 
        heating_demand_correlation = -158.15 * sncwv + 3622.5

        # Distribute daily deamd into hourly demand
        if weekday == 5 or weekday == 6:
            _data = hourly_gas_shape_wkend * heating_demand_correlation
            hd_data[yearday_python] = _data  # DATA ARRAY
        else:
            _data = hourly_gas_shape_wkday * heating_demand_correlation
            hd_data[yearday_python] = _data  # DATA ARRAY


    # ---------------
    # Create hourly peak
    # ---------------
    shape_h_non_peak = np.copy(hd_data)
    print("shape_h_non_peak" + str(shape_h_non_peak))
    cnt = 0
    for hourly_values in shape_h_non_peak:
        day_sum = np.sum(hourly_values)
        shape_h_non_peak[cnt] = (1 / day_sum) * hourly_values
        cnt += 1

    print("shape_h_non_peak: " + str(shape_h_non_peak))
    # ---------------
    # Create day peak
    # ---------------
    # Total yearly heating demand
    total_y_hd = np.sum(hd_data)

    shape_d_non_peak = np.zeros((365, 1)) #Two dimensional array with one row

    # Percentage of total demand for every day
    cnt = 0
    for day in hd_data:
        shape_d_non_peak[cnt] = (1.0/total_y_hd) * np.sum(day) #calc daily demand in percent
        cnt += 1

    #print("Sum appliances_shape: " + str(shape_d_non_peak))
    #print(shape_d_non_peak.shape)
    #print(end_use)
    #prnt("..")

    # Add to hourly shape
    data['dict_shapes_end_use_h'][end_use] = {'peak_h_shape': shape_h_non_peak, 'shape_h_non_peak': shape_h_non_peak} # TODO: no peak for gas

    # Add to daily shape
    data['dict_shapes_end_use_d'][end_use]  = {'peak_d_shape': shape_d_non_peak, 'shape_d_non_peak': shape_d_non_peak} # No peak

    return data