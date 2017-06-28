import os
import csv
import re
import unittest
import json
import datetime
import copy
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
import energy_demand.main_functions as mf
import energy_demand.plot_functions as pf
ASSERTIONS = unittest.TestCase('__init__')
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def read_hes_data(paths_hes, nr_app_type_lu, day_type_lu):
    '''Read in HES raw csv files and provide for every day in a year (yearday) all fuels

    The fuel is provided for every daytype (weekend or working day) for every month
    and every appliance_typ

    Parameters
    ----------
    paths_hes : string
        Path to HES raw data file
    nr_app_type_lu : dict
        Number of appliances (defines size of container to store data)
    day_type_lu : dict
        Look-up table for daytypes

    Returns
    -------
    hes_data : array
        HES non peak raw data
    hes_y_coldest : array
        HES for coldest day
    hes_y_warmest : array
        HES for warmest day

    Info
    ----
    '''
    hes_data = np.zeros((len(day_type_lu), 12, 24, nr_app_type_lu), dtype=float)

    hes_y_coldest = np.zeros((24, nr_app_type_lu))
    hes_y_warmest = np.zeros((24, nr_app_type_lu))

    # Read in raw HES data from CSV
    raw_elec_data = mf.read_csv(paths_hes)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month, daytype, appliance_typ = int(row[0]), int(row[1]), int(row[2])
        k_header = 3 #Row in Excel where energy data start

        for hour in range(24): # iterate over hour  = row in csv file
            # [kWH electric] Converts the summed watt into kWH 
            # Note: This would actually not necessary as we are only calculating in relative terms
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000))

            # if coldest (see HES file)
            if daytype == 2:
                hes_y_coldest[hour][appliance_typ] = _value
                k_header += 1
            elif daytype == 3:
                hes_y_warmest[hour][appliance_typ] = _value
                k_header += 1
            else:
                hes_data[daytype][month][hour][appliance_typ] = _value
                k_header += 1

    return hes_data, hes_y_coldest, hes_y_warmest

def assign_hes_data_to_year(nr_of_appliances, hes_data, base_yr):
    '''Fill every base year day with correct data

    Parameters
    ----------
    nr_of_appliances : dict
        Defines how many appliance types are stored (max 10 provided in original hes file)
    hes_data : array
        HES raw data for every month and daytype and appliance
    base_yr : float
        Base year to generate shapes

    Returns
    -------
    year_raw_values : array
        Energy data for every day in the base year for every appliances
    '''
    year_raw_values = np.zeros((365, 24, nr_of_appliances), dtype=float)

    # Create list with all dates of a whole year
    list_dates = mf.fullyear_dates(start=date(base_yr, 1, 1), end=date(base_yr, 12, 31))

    # Assign every date to the place in the array of the year
    for yearday in list_dates:
        month_python = yearday.timetuple().tm_mon - 1 # - 1 because in _info: Month 1 = Jan
        yearday_python = yearday.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
        daytype = mf.get_weekday_type(yearday)
        year_raw_values[yearday_python] = hes_data[daytype][month_python] # Get day from HES raw data array

    return year_raw_values

def assign_carbon_trust_data_to_year(carbon_trust_data, base_yr):
    """Fill every base year day with correct data

    Parameters
    ----------
    carbon_trust_data : data
        Raw data
    base_yr : int
        Base Year
    """
    shape_non_peak_dh = np.zeros((365, 24))

    # Create list with all dates of a whole year
    list_dates = mf.fullyear_dates(start=date(base_yr, 1, 1), end=date(base_yr, 12, 31))

    # Assign every date to the place in the array of the year
    for yearday in list_dates:
        month_python = yearday.timetuple().tm_mon - 1 # - 1 because in _info: Month 1 = Jan
        yearday_python = yearday.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
        daytype = mf.get_weekday_type(yearday)
        _data = carbon_trust_data[daytype][month_python] # Get day from HES raw data array

        # Add values to yearly
        _data = np.array(list(_data.items()))
        shape_non_peak_dh[yearday_python] = np.array(_data[:, 1], dtype=float)   # now [yearday][24 hours with relative shape]

    return shape_non_peak_dh

def get_hes_load_shapes(appliances_HES_enduse_matching, year_raw_values, hes_y_peak, enduse):
    """Read in raw HES data and generate shapes

    Calculate peak day demand

    Parameters
    ----------
    appliances_HES_enduse_matching : dict
        HES appliances are matched witch enduses
    year_raw_values : data
        Yearly values from raw
    hes_y_peak : data
        Peak raw values
    enduse : string
        enduse

    Returns
    -------
    shape_peak_yd_factor : float
        Peak day demand (Calculate factor which can be used to multiply yearly demand to generate peak demand)
    shape_peak_yh : float
        Peak demand of each hours of peak day

    Notes
    -----
    The HES appliances are matched with enduses
    """
    # Match enduse with HES appliance ID (see look_up table in original files for more information)
    if enduse in appliances_HES_enduse_matching:
        hes_app_id = appliances_HES_enduse_matching[enduse]
    else:
        print("...The enduse has not HES ID and thus shape")

    # Total yearly demand of hes_app_id
    tot_enduse_y = np.sum(year_raw_values[:, :, hes_app_id])


    # ---Peak calculation Get peak daily load shape

    # Calculate amount of energy demand for peak day of hes_app_id
    peak_h_values = hes_y_peak[:, hes_app_id]

    # Shape of peak day
    shape_peak_dh = mf.absolute_to_relative(peak_h_values) #(1.0 / tot_peak_demand_d) * peak_h_values # hourly values of peak day

    # Maximum daily demand
    tot_peak_demand_d = np.sum(peak_h_values)

    # Factor to calculate daily peak demand from yearly demand
    shape_peak_yd_factor = (1.0 / tot_enduse_y) * tot_peak_demand_d


    # ---Calculate non-peak shapes
    shape_non_peak_yd = np.zeros((365))
    shape_non_peak_dh = np.zeros((365, 24))

    for day in range(365):
        day_values = year_raw_values[day, :, hes_app_id]

        shape_non_peak_yd[day] = (1.0 / tot_enduse_y) * np.sum(day_values)
        shape_non_peak_dh[day] = (1.0 / np.sum(day_values)) * day_values # daily shape

    return shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd



# CARBON TRUST-----------------------------------
def initialise_out_dict_av():
    out_dict_av = {0: {}, 1: {}}
    for dtype in out_dict_av:
        month_dict = {}
        for month in range(12):
            month_dict[month] = {k: 0 for k in range(24)}
        out_dict_av[dtype] = month_dict
    return out_dict_av

def initialise_main_dict():
    out_dict_av = {0: {}, 1: {}}
    for dtype in out_dict_av:
        month_dict = {}
        for month in range(12):
            month_dict[month] = {k: [] for k in range(24)}
        out_dict_av[dtype] = month_dict
    return out_dict_av

def dict_init_carbon_trunst():

    # Initialise yearday dict
    carbon_trust_raw = {}
    for day in range(365):
        day_dict_h = {k: [] for k in range(24)}
        carbon_trust_raw[day] = day_dict_h

    return carbon_trust_raw

def read_raw_carbon_trust_data(folder_path):
    """

    Parameters
    ----------
    foder_path : string
        Path to folder with stored csv files

    Returns
    -------


    Info
    -----
    A. Get gas peak day load shape (the max daily demand can be taken from weather data, the daily shape however is not provided by samson)
        I. Iterate individual files which are about a year (even though gaps exist)
        II. Select those day with the maximum load
        III. Get the hourly shape of this day

    1. Calculate total demand of every day
    2. Assign percentag of total daily demand to each hour

    """
    # Get all files in folder
    all_csv_in_folder = os.listdir(folder_path)
    main_dict = initialise_main_dict()
    carbon_trust_raw = dict_init_carbon_trunst()

    nr_of_line_entries = 0
    dict_max_dh_shape = {}

    # Itreateu folder with csv files
    for path_csv_file in all_csv_in_folder:
        path_csv_file = os.path.join(folder_path, path_csv_file)

        # Read csv file
        with open(path_csv_file, 'r') as csv_file:
            print("path_csv_file: " + str(path_csv_file))
            read_lines = csv.reader(csv_file, delimiter=',')
            _headings = next(read_lines)
            max_d_demand = 0 # Used for searching maximum

            # Count number of lines in CSV file
            row_data = []
            for count_row, row in enumerate(read_lines):
                row_data.append(row)
            #print("Number of lines in csv file: " + str(count_row))

            # Calc yearly demand based on one year data measurements
            if count_row > 365: # if more than one year is recorded in csv file TODO: All but then distored?
                print("FILE covers a full year---------------------------")

                for day, row in enumerate(row_data):
                    if len(row) != 49: # Test if file has correct form and not more entries than 48 half-hourly entries
                        continue # Skip row

                    # Use only data of one year
                    if day > 365:
                        continue

                    load_shape_dh = np.zeros((24))

                    row[1:] = map(float, row[1:]) # Convert all values except date into float values
                    daily_sum = sum(row[1:]) # Total daily sum
                    nr_of_line_entries += 1 # Nr of lines added
                    day, month, year = int(row[0].split("/")[0]), int(row[0].split("/")[1]), int(row[0].split("/")[2])

                    # Redefine yearday to another year and skip 28. of Feb.
                    if is_leap_year(int(year)) == True:
                        year = year + 1 # Shift whole dataset to another year
                        if month == 2 and day == 29:
                            continue #skip leap day

                    date_row = date(year, month, day)
                    daytype = mf.get_weekday_type(date_row)
                    yearday_python = date_row.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
                    month_python = month - 1 # Month Python

                    h_day, cnt, control_sum = 0, 0, 0

                    # -----------------------------------------------
                    # Iterate half hour data and summarise to hourly
                    # -----------------------------------------------
                    for data_h in row[1:]:  # Skip first date row in csv file
                        cnt += 1
                        if cnt == 2:

                            demand_h = first_data_h + data_h
                            control_sum += abs(demand_h)

                            # Calc percent of total daily demand
                            carbon_trust_raw[yearday_python][h_day].append(demand_h)

                            # Stor demand according to daytype (aggregated by doing so)
                            main_dict[daytype][month_python][h_day].append(demand_h)

                            if daily_sum == 0: # Skip row if no demand of the day
                                load_shape_dh[h_day] = 0
                                continue
                            else:
                                load_shape_dh[h_day] = demand_h * np.divide(1.0, daily_sum) # Load shape of this day

                                cnt = 0

                            h_day += 1

                        # Value lagging behind one iteration
                        first_data_h = data_h

                    # Test if this is the day with maximum demand of this CSV file
                    if daily_sum >= max_d_demand:
                        max_d_demand = daily_sum
                        max_dh_shape = load_shape_dh

                    # Check if 100 %
                    ASSERTIONS = unittest.TestCase('__init__')
                    ASSERTIONS.assertAlmostEqual(control_sum, daily_sum, places=7, msg=None, delta=None)

                # Add load shape of maximum day in csv file
                dict_max_dh_shape[path_csv_file] = max_dh_shape

    # ---------------
    # Data processing
    # ---------------

    # --Average average maxium peak dh of every csv file
    load_peak_average_dh = np.zeros((24))
    for peak_shape_dh in dict_max_dh_shape.values():
        load_peak_average_dh += peak_shape_dh
    load_peak_shape_dh = np.divide(load_peak_average_dh, len(dict_max_dh_shape))

    # Calculate average of for different csv files (sum of all entries / number of entries)
    carbon_trust_raw_array = np.zeros((365, 24))
    for yearday in carbon_trust_raw:
        for h_day in carbon_trust_raw[yearday]:

            # Add average to array
            carbon_trust_raw_array[yearday][h_day] = np.divide(sum(carbon_trust_raw[yearday][h_day]), len(carbon_trust_raw[yearday][h_day])) #average

            # Add average to dict
            carbon_trust_raw[yearday][h_day] = np.divide(sum(carbon_trust_raw[yearday][h_day]), len(carbon_trust_raw[yearday][h_day])) #average

    # -----------------------------------------------
    # Calculate average load shapes for every month
    # -----------------------------------------------

    # -- Average (initialise dict)
    out_dict_av = initialise_out_dict_av()

    # Calculate average for monthly dict
    for daytype in main_dict:
        for month in main_dict[daytype]:
            for hour in main_dict[daytype][month]:
                nr_of_entries = len(main_dict[daytype][month][hour])
                if nr_of_entries != 0:
                    out_dict_av[daytype][month][hour] = np.divide(sum(main_dict[daytype][month][hour]), nr_of_entries)

    # ----------------------------------------------------------
    # Distribute raw data into base year depending on daytype
    # ----------------------------------------------------------
    year_data = assign_carbon_trust_data_to_year(out_dict_av, 2015)

    #year_data_shape = mf.absolute_to_relative(year_data) #np.divide(1, np.sum(year_data)) * year_data

    # Calculate yearly sum
    yearly_demand = np.sum(year_data)

    # Calculate shape_peak_yd_factor
    max_demand_d = 0
    for yearday, carbon_trust_d in enumerate(year_data):
        daily_sum = np.sum(carbon_trust_d)
        if daily_sum > max_demand_d:
            max_demand_d = daily_sum
            #max_day = yearday

    shape_peak_yd_factor = np.divide(1, yearly_demand) * max_demand_d
    print("shape_peak_yd_factor: " + str(shape_peak_yd_factor))

    # Create load_shape_dh
    load_shape_dh = np.zeros((365, 24))
    for day, dh_values in enumerate(year_data):
        load_shape_dh[day] = mf.absolute_to_relative(dh_values) #np.divide(1.0, np.sum(dh_values)) * dh_values # daily shape

    ASSERTIONS.assertAlmostEqual(np.sum(load_shape_dh), 365.0, places=2, msg=None, delta=None)

    # Calculate shape_non_peak_yd
    shape_non_peak_yd = np.zeros((365))
    for yearday, carbon_trust_d in enumerate(year_data):
        shape_non_peak_yd[yearday] = np.sum(carbon_trust_d)
    shape_non_peak_yd = np.divide(1, yearly_demand) * shape_non_peak_yd

    ASSERTIONS.assertAlmostEqual(np.sum(np.sum(shape_non_peak_yd)), 1.0, places=2, msg=None, delta=None)

    return load_shape_dh, load_peak_shape_dh, shape_peak_yd_factor, shape_non_peak_yd

def is_leap_year(year):
    """Determine whether a year is a leap year"""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def read_weather_data_raw(path_to_csv, placeholder_value):
    """Read in raw weather data

    Parameters
    ----------
    path_to_csv : string
        Path to weather data csv FileExistsError

    placeholder_value : int
        Placeholder number which is used in case no measurment exists for an hour

    Returns
    -------
    temp_stations : dict
        Contains temperature data (e.g. {'station_id: np.array((yeardays, 24))})

    Info
    ----
    The data are obtained from the Centre for Environmental Data Analysis

    http://data.ceda.ac.uk/badc/ukmo-midas/data/WH/yearly_files/ (Download link)

    http://badc.nerc.ac.uk/artefacts/badc_datadocs/ukmo-midas/WH_Table.html (metadata)
    """
    temp_stations = {}

    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')

        # Iterate rows
        for row in read_lines: # select row
            date_measurement = row[0].split(" ")
            year = int(date_measurement[0].split("-")[0])
            month = int(date_measurement[0].split("-")[1])
            day = int(date_measurement[0].split("-")[2])
            hour = int(date_measurement[1][:2])

            # Weather station id
            station_id = int(row[5])

            # Air temperature in Degrees Celcius
            if row[35] == ' ': # If no data point
                air_temp = placeholder_value
            else:
                air_temp = float(row[35])

            # Get yearday
            yearday = mf.convert_date_to_yearday(year, month, day)

            # Add weather station if not already added to dict
            if station_id not in temp_stations:
                temp_stations[station_id] = np.zeros((365, 24))

            # Add data
            temp_stations[station_id][yearday][hour] = air_temp

    return temp_stations

def clean_weather_data_raw(temp_stations, placeholder_value):
    """Relace missing data measurement points and remove weater stations with no data

    Parameters
    ----------
    temp_stations : dict
        Raw data of temperature measurements

    placeholder_value : int
        Placeholder value for missing measurement point

    Returns
    -------
    temp_stations_cleaned : dict
        Cleaned temp measurements

    Notes
    -----
    In the temperature mesaurements there are missing data points and for some stations, only 0 values are provided.
    From the raw dataset, all those stations are excluded where:
        - At least one day in a year has no measurement values
        - There is a day in the year with too many 0 values (zeros_day_crit criteria)
        - There is a day in a year with more than one missing measurement point

    In case only one measurement point is missing, this point gets interpolated.
    """
    zeros_day_crit = 10 # How many 0 values there must be in a day in order to ignore weater station
    temp_stations_cleaned = {}

    for station_id in temp_stations:

        # Iterate to see if data can be copyied or not
        copy_weater_station_data = True
        for day_nr, day in enumerate(temp_stations[station_id]):
            if np.sum(day) == 0:
                copy_weater_station_data = False

            # Count number of zeros in a day
            cnt_zeros = 0
            for h in day:
                if h == 0:
                    cnt_zeros += 1

            if cnt_zeros > zeros_day_crit:
                copy_weater_station_data = False

        if copy_weater_station_data:
            temp_stations_cleaned[station_id] = temp_stations[station_id]
        else: # Do not add data
            continue # Continue iteration

        # Check if missing single temp measurements
        for day_nr, day in enumerate(temp_stations[station_id]):
            if placeholder_value in day: # If day with missing data point

                # check number of missing values
                nr_of_missing_values = 0
                for h in day:
                    if h == placeholder_value:
                        nr_of_missing_values += 1

                # If only one placeholder
                if nr_of_missing_values == 1:

                    # Interpolate depending on hour
                    for h, temp in enumerate(day):
                        if temp == placeholder_value:
                            if h == 0 or h == 23:
                                if h == 0: #If value of hours hour in day is missing
                                    temp_stations_cleaned[station_id][day_nr][h] = day[h + 1] #Replace with temperature of next hour
                                if h == 23:
                                    temp_stations_cleaned[station_id][day_nr][h] = day[h - 1] # Replace with temperature of previos hour
                            else:
                                temp_stations_cleaned[station_id][day_nr][h] = (day[h - 1] + day[h + 1]) / 2 # Interpolate

                # if more than one temperture data point is missing in a day, remove weather station
                if nr_of_missing_values > 1:
                    del temp_stations_cleaned[station_id]
                    break

    return temp_stations_cleaned

def read_weather_stations_raw(path_to_csv):
    """Read in all weater stations from csv file

    Parameter
    ---------
    path_to_csv : string
        Path to csv with stored weater station data

    Returns:
    --------
    weather_stations : dict
        Contains coordinates and station_id of weather stations

    Note
    ----
    Downloaded from MetOffice
    http://badc.nerc.ac.uk/cgi-bin/midas_stations/excel_list_station_details.cgi.py (09-05-2017)
    """
    weather_stations = {}

    with open(path_to_csv, 'r') as csvfile: # Read CSV file
        _headings = next(csvfile) # Skip first row
        _headings = next(csvfile) # Skip second row

        for row in csvfile:
            row_split = re.split('\s+', row)

            # Get only the float elements of each row
            all_float_values = []
            for entry in row_split:
                # Test if can be converted to float
                try:
                    all_float_values.append(float(entry))
                except ValueError:
                    pass

            station_id = int(all_float_values[0])
            station_latitude = float(all_float_values[1])
            station_longitude = float(all_float_values[2])

            weather_stations[station_id] = {'station_latitude': station_latitude, 'station_longitude': station_longitude}

    return weather_stations

def reduce_weather_stations(station_ids, weather_stations):
    """Get only those weather station information for which there is cleaned data available

    Parameters
    ----------
    station_ids : list
        Weather station ids with data
    weather_stations : dict
        Weather station information

    Return
    ------
    stations_with_data : dict
        Weather station information
    """
    stations_with_data = {}

    # Iterate all stations containing data
    for id_station in station_ids:

        # If there are data for a station add them
        if id_station in weather_stations.keys():
            stations_with_data[id_station] = weather_stations[id_station]

    return stations_with_data

def create_txt_shapes(end_use, path_txt_shapes, shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd, other_string_info):
    """ Function collecting functions to write out txt files"""
    jason_to_txt_shape_peak_dh(shape_peak_dh, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_dh') + str('.txt')))
    jason_to_txt_shape_non_peak_dh(shape_non_peak_dh, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_non_peak_dh') + str('.txt')))
    jason_to_txt_shape_peak_yd_factor(shape_peak_yd_factor, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_peak_yd_factor') + str('.txt')))
    jason_to_txt_shape_non_peak_yd(shape_non_peak_yd, os.path.join(path_txt_shapes, str(end_use) + str("__") + str('shape_non_peak_yd') + str('.txt')))

    return

def jason_to_txt_shape_peak_dh(input_array, outfile_path):
    """Wrte to txt. Array with shape: (24,)
    """
    np_dict = dict(enumerate(input_array))
    with open(outfile_path, 'w') as outfile:
        json.dump(np_dict, outfile)

def jason_to_txt_shape_non_peak_dh(input_array, outfile_path):
    """Wrte to txt. Array with shape: (365, 24)
    """
    out_dict = {}
    for k, row in enumerate(input_array):
        out_dict[k] = dict(enumerate(row))
    with open(outfile_path, 'w') as outfile:
        json.dump(out_dict, outfile)

def jason_to_txt_shape_peak_yd_factor(input_array, outfile_path):
    """Wrte to txt. Array with shape: ()
    """
    with open(outfile_path, 'w') as outfile:
        json.dump(input_array, outfile)

def jason_to_txt_shape_non_peak_yd(input_array, outfile_path):
    """Wrte to txt. Array with shape: (365)"""
    out_dict = {}
    for k, row in enumerate(input_array):
        out_dict[k] = row
    with open(outfile_path, 'w') as outfile:
        json.dump(out_dict, outfile)

def read_txt_shape_peak_dh(file_path):
    """Read to txt. Array with shape: (24,)
    """
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    out_dict = np.array(read_dict_list, dtype=float)
    return out_dict

def read_txt_shape_non_peak_yh(file_path):
    """Read to txt. Array with shape: (365, 24)"""
    out_dict = np.zeros((365, 24))
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(list(row.values()), dtype=float)
    return out_dict

def read_txt_shape_peak_yd_factor(file_path):
    """Read to txt. Array with shape: (365, 24)
    """
    out_dict = json.load(open(file_path))
    return out_dict

def read_txt_shape_non_peak_yd(file_path):
    """Read to txt. Array with shape: (365, 1)
    """
    out_dict = np.zeros((365))
    read_dict = json.load(open(file_path))
    read_dict_list = list(read_dict.values())
    for day, row in enumerate(read_dict_list):
        out_dict[day] = np.array(row, dtype=float)
    return out_dict


'''
def compare_jan_jul(main_dict_dayyear_absolute):
    """ COMPARE JAN AND JUL DATA"""
    # Percentages for every day:
    jan_yearday = range(0, 30)
    jul_yearday = range(181, 212)
    jan = {k: [] for k in range(24)}
    jul = {k: [] for k in range(24)}

    # Read out for the whole months of jan and ful
    for day in main_dict_dayyear_absolute:
        for h in main_dict_dayyear_absolute[day]:
            if day in jan_yearday:
                jan[h].append(main_dict_dayyear_absolute[day][h])
            if day in jul_yearday:
                jul[h].append(main_dict_dayyear_absolute[day][h])
    #print(jan)
    # Average the montly entries
    for i in jan:
        print("Nr of datapoints in Jan for hour: " + str(len(jan[i])))
        jan[i] = sum(jan[i]) / len(jan[i])

    for i in jul:
        print("Nr of datapoints in Jul for hour:" + str(len(jul[i])))
        jul[i] = sum(jul[i]) / len(jul[i])

    # Test HEATING_ELEC SHARE DIFFERENCE JAN and JUN [daytype][_month][_hr]
    jan = np.array(list(jan.items())) #convert to array
    jul = np.array(list(jul.items())) #convert to array
    jul_percent_of_jan = (100/jan[:, 1]) * jul[:, 1]

    x_values = range(24)
    y_values = list(jan[:, 1]) # to get percentages
    plt.plot(x_values, list(jan[:, 1]), label="Jan")
    plt.plot(x_values, list(jul[:, 1]), label="Jul")
    plt.plot(x_values, list(jul_percent_of_jan), label="% dif of Jan - Jul")
    plt.legend()
    plt.show()


    #--- if JAn = 100%
    jul_percent_of_jan = (100/jan[:, 1]) * jul[:, 1]
    for h ,i in enumerate(jul_percent_of_jan):
        print("h: " + str(h) + "  %" + str(i) + "   Diff: " + str(100-i))

    pf.plot_load_shape_yd_non_resid(jan)
    print("TEST: " + str(jan-jul))
'''

'''def followup_processing(out_dict_average, out_dict_not_average):

    # --------------------------------------------------------
    # Calculate average daily load shape for all mongth (averaged)
    # --------------------------------------------------------
    # Initiate
    yearly_averaged_load_curve = {0: {}, 1: {}}
    for daytype in yearly_averaged_load_curve:
        yearly_averaged_load_curve[daytype] = {k: 0 for k in range(24)}

    for daytype in out_dict_average:

        # iterate month
        for hour in range(24):
            h_average_y = 0

            # Get every hour of all months
            for month in range(12):
                h_average_y += out_dict_average[daytype][month][hour]

            h_average_y = h_average_y / 12
            yearly_averaged_load_curve[daytype][hour] = h_average_y

    print("Result yearly averaged:")
    print(yearly_averaged_load_curve)
    return
'''