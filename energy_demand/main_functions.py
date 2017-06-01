"""This file stores all functions of main.py"""
import os
import sys
import csv
import re
from datetime import date
from datetime import timedelta as td
import math as m
import copy
import pprint
import numpy as np
import yaml
import pylab
import matplotlib.pyplot as plt
from haversine import haversine # PAckage to calculate distance between two long/lat points
from scipy.optimize import curve_fit

import unittest
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

def add_yearly_external_fuel_data(data, dict_to_add_data):
    """This data check what enduses are provided by wrapper
    and then adds the yearls fule data to data

    #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE
    """
    for external_enduse in data['data_ext']['external_enduses_resid']:
        new_fuel_array = np.zeros((len(data['fuel_type_lu']), 1))
        for fueltype in data['data_ext']['external_enduses_resid'][external_enduse]:
            new_fuel_array[fueltype] = data['data_ext']['external_enduses_resid'][external_enduse][fueltype]
        dict_to_add_data[external_enduse] = new_fuel_array
    return data

def get_temp_region(dw_reg_name, coordinates):
    """
    #TODO Reallocation any region input with wheater region (mabe also coordinate inputs)

    """
    coordinates = coordinates

    temperature_region_relocated = 'Midlands'

    return temperature_region_relocated

def read_txt_t_base_by(pattemp_h_txt, base_yr):
    """Read out mean temperatures for all regions and store in dict

    Parameters
    ----------
    pattemp_h_txt : str
        Path to folder with temperature txt files
    base_yr : int
        Base year

    Returns
    -------
    out_dict : dict
        Returns a dict with name of file and base year mean temp for every month

    Example
    -------
    out_dict = {'file_name': {0: mean_teamp, 1: mean_temp ...}}

    #

    """
    # get all files in folder
    all_txt_files = os.listdir(pattemp_h_txt)
    out_dict = {}

    # Iterate files in folder
    for file_name in all_txt_files:
        reg_name = file_name[:-4] # remove .txt
        file_name = os.path.join(pattemp_h_txt, file_name)
        txt = open(file_name, "r")
        out_dict_reg = {}

        # Iterate rows in txt file
        for row in txt:
            row_split = re.split('\s+', row)

            if row_split[0] == str(base_yr):
                for month in range(12):
                    out_dict_reg[month] = float(row_split[month + 1]) #:because first entry is year in txt

        out_dict[reg_name] = out_dict_reg

    return out_dict

def convert_out_format_es(data, object_country):
    """Adds total hourly fuel data into nested dict

    Parameters
    ----------
    data : dict
        Dict with own data
    object_country : object
        Contains objects of the region

    Returns
    -------
    results : dict
        Returns a list for energy supply model with fueltype, region, hour"""

    # Create timesteps for full year (wrapper-timesteps)
    results = {}

    for fueltype_id, fueltype in data['fuel_type_lu'].items():
        results[fueltype] = []

        for reg_name in data['lu_reg']:
            reg = getattr(object_country, str(reg_name))
            region_name = reg.reg_name  # Get object region name
            hourly_all_fuels = reg.tot_all_enduses_h(data, 'enduse_fuel_yh')  # Get total fuel

            for day, hourly_demand in enumerate(hourly_all_fuels[fueltype_id]):
                for hour_in_day, demand in enumerate(hourly_demand):
                    hour_in_year = "{}_{}".format(day, hour_in_day)
                    result = (region_name, hour_in_year, float(demand), "units")
                    results[fueltype].append(result)

    return results

def read_csv_float(path_to_csv):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    list_elements = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(row)

    return np.array(list_elements, float) # Convert list into array

def read_csv(path_to_csv):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : array_like
        Returns an array `elements_array` with the read in csv files.

    Notes
    -----
    The header row is always skipped.
    """
    list_elements = []
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(row)

    return np.array(list_elements) # Convert list into array

def read_csv_base_data_resid(path_to_csv):
    """This function reads in base_data_CSV all fuel types (first row is fueltype, subkey), header is appliances

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    _dt : str
        Defines dtype of array to be read in (takes float)

    Returns
    -------
    elements_array : dict
        Returns an dict with arrays

    Notes
    -----
    the first row is the fuel_ID
    The header is the sub_key
    # Quick and dirty
    The fuel input dictionary must have a value for every fuel (0)
    """
    try:
        lines = []
        end_uses_dict = {}

        with open(path_to_csv, 'r') as csvfile:               # Read CSV file
            read_lines = csv.reader(csvfile, delimiter=',')   # Read line
            _headings = next(read_lines)                      # Skip first row

            # Iterate rows
            for row in read_lines: # select row
                lines.append(row)

            for i in _headings[1:]: # skip first
                end_uses_dict[i] = np.zeros((len(lines), 1)) # len fuel_ids

            for cnt_fueltype, row in enumerate(lines):
                cnt = 1 #skip first
                for i in row[1:]:
                    end_use = _headings[cnt]
                    end_uses_dict[end_use][cnt_fueltype] = i
                    cnt += 1
    except:
        print("Error in loading fuel data. Check wheter there are any empty cells in the csv files (instead of 0)")
    return end_uses_dict

def read_technologies(path_to_csv, data):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    dict_technologies : dict
        All technologies and their assumptions provided as input
    """
    dict_technologies = {}

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            technology = row[0]
            dict_technologies[technology] = {
                'fuel_type': data['lu_fueltype'][str(row[1])],
                'eff_by': float(row[2]),
                'eff_ey': float(row[3]),
                'eff_achieved': float(row[4]),
                'diff_method': str(row[5]),
                'market_entry': float(row[6])
            }
    #If this function does not work, check if in excel empty rows are loaded in
    return dict_technologies

def read_csv_assumptions_fuel_switches(path_to_csv, data):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    dict_with_switches : dict
        All assumptions about fuel switches provided as input
    """
    list_elements = []
    dict_with_switches = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(
                {
                    'enduse': str(row[0]),
                    'enduse_fueltype_replace': data['lu_fueltype'][str(row[1])],
                    'technology_install': str(row[2]),
                    'year_fuel_consumption_switched': float(row[3]),
                    'share_fuel_consumption_switched': float(row[4]),
                    'max_theoretical_switch': float(row[5])
                }
            )
    
    # -------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for element in list_elements:
        if element['share_fuel_consumption_switched'] > element['max_theoretical_switch']:
            sys.exit("Error while loading fuel switch assumptions: More fuel is switched than theorically possible for enduse '{}' and fueltype '{}".format(element['enduse'], element['enduse_fueltype_replace']))

    return list_elements

def read_csv_assumptions_service_switch(path_to_csv, assumptions):
    """This function reads in service assumptions from csv file. 

    If no assumptions about service switches, return empty dicts.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file
    assumptions : dict
        Assumptions

    Returns
    -------
    dict_with_switches : dict
        All assumptions about fuel switches provided as input

    Notes
    -----
    - skips header row
    - It also test if plausible inputs
    While not only loading in all rows, this function as well tests if inputs are plausible (e.g. sum up to 100%)
    """
    list_elements = []
    dict_with_switches_by = {}
    dict_with_switches_ey = {}
    assump_max_share_L = {}

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(
                {
                    'enduse_service': str(row[0]),
                    'tech': str(row[1]),
                    'service_share_by': float(row[2]),
                    'service_share_ey': float(row[3]),
                    'tech_assum_max_share': float(row[4])
                }
            )

    # Group all entries according to enduse
    all_enduses = []
    for line in list_elements:
        enduse = line['enduse_service']
        if enduse not in all_enduses:
            all_enduses.append(enduse)
            dict_with_switches_by[enduse] = {}
            dict_with_switches_ey[enduse] = {}
            assump_max_share_L[enduse] = {}

    # Iterate all endusese and assign all lines
    for enduse in all_enduses:
        for line in list_elements:
            if line['enduse_service'] == enduse:
                tech = line['tech']
                dict_with_switches_by[enduse][tech] = line['service_share_by']
                dict_with_switches_ey[enduse][tech] = line['service_share_ey']
                assump_max_share_L[enduse][tech] = line['tech_assum_max_share']

    # Add to assumptions
    assumptions['service_tech_by_p'] = dict_with_switches_by
    assumptions['share_service_tech_ey_p'] = dict_with_switches_ey
    assumptions['test_assump_max_share_L'] = assump_max_share_L

    # -------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    # Test if service of all provided technologies sums up to 100% in the end year
    for enduse in dict_with_switches_by:

        if sum(dict_with_switches_by[enduse].values()) != 1.0:
            sys.exit("Error while loading future services assumptions: The provided service switch of enduse '{}' does not sum up to 1.0 (100%)".format(enduse))

        if sum(dict_with_switches_ey[enduse].values()) != 1.0:
            sys.exit("Error while loading future services assumptions: The provided service switch of enduse '{}' does not sum up to 1.0 (100%)".format(enduse))

    return assumptions

def fullyear_dates(start=None, end=None):
    """Calculates all dates between a star and end date.
    TESTED_PYTEST

    Parameters
    ----------
    start : date
        Start date
    end : date
        end date

    Returns
    -------
    list_dates : list
        A list with dates
    """
    list_dates = []
    span = end - start
    for i in range(span.days + 1):
        list_dates.append(start + td(days=i))
    return list(list_dates)

def conversion_ktoe_gwh(data_ktoe):
    """Conversion of ktoe to gwh
    TESTED_PYTEST
    Parameters
    ----------
    data_ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in GWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    data_gwh = data_ktoe * 11.6300000
    return data_gwh

def conversion_ktoe_TWh(data_ktoe):
    """Conversion of ktoe to TWh

    Parameters
    ----------
    data_ktoe : float
        Energy demand in ktoe

    Returns
    -------
    data_gwh : float
        Energy demand in TWh

    Notes
    -----
    https://www.iea.org/statistics/resources/unitconverter/
    """
    data_gwh = data_ktoe * 0.0116300000
    return data_gwh

def timesteps_full_year(base_yr):
    """A list is generated from the first hour of the base year to the last hour of teh base year

    This function generates a single list from a list with
    containg start and end dates of the base year

    Parameters
    ----------
    base_yr : int
        Year used to generate timesteps.

    Returns
    -------
    timesteps : dict
        Contains every yearday and the start and end time_ID

    Note
    ----
    The base year must be identical to the input energy data

    """
    # List with all dates of the base year
    list_dates = fullyear_dates(start=date(base_yr, 1, 1), end=date(base_yr, 12, 31)) # List with every date in a year

    timesteps = {}

    #Add to list
    for day_date in list_dates:
        yearday = day_date.timetuple().tm_yday - 1 # -1 because in _info yearday 1: 1. Jan    ((tm_year=2015, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=-1))

        # Iterate hours
        for h_id in range(24):
            start_period = "P{}H".format(yearday * 24 + h_id) # Start intervall ID
            end_period = "P{}H".format(yearday * 24 + h_id + 1) # End intervall ID
            yearday_h_id = str(str(yearday) + str("_") + str(h_id)) # Timestep ID

            # Add to dict
            timesteps[yearday_h_id] = {'start': start_period, 'end': end_period}

    return timesteps

def get_weekday_type(date_from_yearday):
    """Gets the weekday of a date
    TESTED_PYTEST
    Parameters
    ----------
    date_from_yearday : date
        Date of a day in ayear

    Returns
    -------
    daytype : int
        If 1: holiday, if 0; working day

    Notes
    -----
    notes
    """
    weekday = date_from_yearday.timetuple().tm_wday # (tm_year=2015, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=-1)

    if weekday == 5 or weekday == 6:
        return 1 # Holiday
    else:
        return 0 # Working day

def read_csv_nested_dict(path_to_csv):
    """Read in csv file into nested dictionary with first row element as main key

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {float(1990): {str(Header1): float(Val1), str(Header2): Val2}}
    """
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            out_dict[float(row[0])] = {}
            cnt = 1 # because skip first element
            for i in row[1:]:
                out_dict[float(row[0])][_headings[cnt]] = float(i)
                cnt += 1

    return out_dict

def read_csv_dict(path_to_csv):
    """Read in csv file into a dict (with header)

    The function tests if a value is a string or float
    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {{str(Year): float(1990), str(Header1): float(Val1), str(Header2): float(Val2)}}
    """
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        for row in read_lines: # Iterate rows
            for k, i in enumerate(row): # Iterate row entries
                try: # Test if float or string
                    out_dict[_headings[k]] = float(i)
                except ValueError:
                    out_dict[_headings[k]] = str(i)

    return out_dict

def read_csv_dict_no_header(path_to_csv):
    """Read in csv file into a dict (without header)

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    out_dict : dict
        Dictionary with first row element as main key and headers as key for nested dict.
        All entries and main key are returned as float

    Info
    -------
    Example:

        Year    Header1 Header2
        1990    Val1    Val2

        returns {{str(Year): float(1990), str(Header1): float(Val1), str(Header2): float(Val2)}}
    """
    out_dict = {}
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        for row in read_lines: # Iterate rows
            try:
                out_dict[int(row[0])] = float(row[1])
            except ValueError:
                out_dict[int(row[0])] = str(row[1])

    return out_dict

def write_YAML(crit_write, path_YAML, yaml_list):
    """Creates a YAML file with the timesteps IDs

    Parameters
    ----------
    crit_write : int
        Whether a yaml file should be written or not (1 or 0)
    path_YAML : str
        Path to write out YAML file
    yaml_list : list
        List containing YAML dictionaries for every region
    """
    if crit_write:
        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)

    return

def write_final_result(data, result_dict, lu_reg, crit_YAML):
    """Write reults for energy supply model

    Parameters
    ----------
    data : dict
        Whether a yaml file should be written or not (1 or 0)
    result_dict : dict
        Dictionary which is stored to txt
    lu_reg : dict
        Look up dict for regions
    crit_YAML : bool
        Criteria if YAML files are generated

    Example
    -------
    The output in the textfile is as follows:

        england, P0H, P1H, 139.42, 123.49
    """
    main_path = data['path_dict']['path_main'][:-5] # Remove data from path_main

    for fueltype in data['fuel_type_lu']:

        # Path to create csv file
        path = os.path.join(main_path, 'model_output/_fueltype_{}_hourly_results.csv'.format(fueltype))

        with open(path, 'w', newline='') as fp:
            csv_writer = csv.writer(fp, delimiter=',')
            data = []
            yaml_list_fuel_type = []

            # Iterate fueltypes
            for reg in result_dict[fueltype]:

                for reg, hour, obs_value, units in result_dict[fueltype]:
                    start_id = "P{}H".format(hour)
                    end_id = "P{}H".format(hour + 1)
                    data.append((lu_reg[reg], start_id, end_id, obs_value))
                    yaml_list_fuel_type.append({'region':  lu_reg[reg], 'start': start_id, 'end': end_id, 'value': float(obs_value), 'units': 'CHECK GWH', 'year': 'XXXX'})

            csv_writer.writerows(data)

            # Write YAML
            write_YAML(crit_YAML, os.path.join(main_path, 'model_output/YAML_TIMESTEPS_{}.yml'.format(fueltype)), yaml_list_fuel_type)

def write_out_txt(path_to_txt, enduses_service):
    """Generate a txt file"""

    file = open(path_to_txt, "w")

    file.write("---------------------------" + '\n')
    file.write("Base year energy service (as share of total per enduse)" + '\n')
    file.write("---------------------------" + '\n')

    for enduse in enduses_service:
        file.write(" " + '\n')
        file.write("Enduse  "+ str(enduse) + '\n')
        file.write("----------" + '\n')

        for tech in enduses_service[enduse]:
            file.write(str(tech) + str("\t") + str("\t") + str("\t") + str(enduses_service[enduse][tech]) + '\n')

        file.close()
    return

def apply_elasticity(base_demand, elasticity, price_base, price_curr):
    """Calculate current demand based on demand elasticity
    TESTED_PYTEST
    As an input the base data is provided and price differences and elasticity

    Parameters
    ----------
    base_demand : array_like
        Input with base fuel demand
    elasticity : float
        Price elasticity
    price_base : float
        Fuel price in base year
    price_curr : float
        Fuel price in current year

    Returns
    -------
    current_demand
        Demand of current year considering price elasticity.

    Info
    ------
    Price elasticity is defined as follows:

        price elasticity = (% change in quantity) / (% change in price)
        or
        elasticity       = ((Q_base - Q_curr) / Q_base) / ((P_base - P_curr)/P_base)

    Reformulating to calculate current demand:

        Q_curr = Q_base * (1 - e * ((P_base - P_curr)/ P_base))

    The function prevents demand becoming negative as in extreme cases this
    would otherwise be possibe.
    """
     # New current demand
    current_demand = base_demand * (1 - elasticity * ((price_base - price_curr) / price_base))

    if current_demand < 0:
        return 0
    else:
        return current_demand

def convert_date_to_yearday(year, month, day):
    """Gets the yearday (julian year day) of a year minus one to correct because of python iteration
    TESTED_PYTEST

    Parameters
    ----------
    date_base_yr : int
        Year
    date_base_yr : int
        Month
    day : int
        Day

    Example
    -------
    5. January 2015 --> Day nr 5 in year --> -1 because of python --> Out: 4
    """
    date_y = date(year, month, day)
    yearday = date_y.timetuple().tm_yday - 1 #: correct because of python iterations

    return yearday

def convert_yearday_to_date(year, yearday_python):
    """Gets the yearday of a year minus one to correct because of python iteration
    TESTED_PYTEST

    Parameters
    ----------
    year : int
        Year
    yearday_python : int
        Yearday - 1
    """
    date_first_jan = date(year, 1, 1)
    date_new = date_first_jan + td(yearday_python)

    return date_new

def hdd_hitchens(days_per_month, k_hitchens_location_constant, t_base, t_mean):
    """Calculate the number of heating degree days based on Hitchens

    Parameters
    ----------
    days_per_month : int
        Number of days of a month
    k_hitchens_location_constant : int
        Hitchens constant
    t_base : int
        Base temperature
    t_mean : int
        Mean temperature of a month

    Info
    ----
    For the hitchens constant a value of 0.71 is suggest for the United Kingdom.

    More info: Day, T. (2006). Degree-days: theory and application. https://doi.org/TM41
    """
    hdd_hitchens = days_per_month * (t_base - t_mean)  / (1 - m.exp(-k_hitchens_location_constant * (t_base-t_mean)))

    return hdd_hitchens

def calc_hdd(t_base, temp_yh):
    """Heating Degree Days for every day in a year

    Parameters
    ----------
    t_base : int
        Base temperature
    temp_yh : array
        Array containing daily temperatures for each day (shape 365, 24)

    Returns
    -------
    hdd_d : array
        An array containing the Heating Degree Days for every day (shape 365, 1)
    """
    hdd_d = np.zeros((365, 1))

    for day, temp_day in enumerate(temp_yh):
        hdd = 0
        for temp_h in temp_day:
            diff = t_base - temp_h
            if diff > 0:
                hdd += t_base - temp_h
        hdd_d[day] = hdd / 24.0

    return hdd_d

def get_tot_y_hdd_reg(t_mean_reg_months, t_base):
    """Calculate total number of heating degree days in a region

    #TODO: Maybe calculate HDD For every day based on houlry data and not monthly! (don't use hitchens then but real calculation)

    Parameters
    ----------
    t_mean_reg_months : float
        Mean temperature in region
    """
    month_days = {0: 31, 1: 28, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 31, 8: 30, 9: 31, 10: 30, 11: 31}
    hdd_tot = 0

    for month in range(12):
        days_per_month = month_days[month]

        k_hitchens_location_constant = 0.71
        #print(days_per_month)
        #print(t_base)
        #print(t_mean_reg_months[month])
        hdd_tot += hdd_hitchens(days_per_month, k_hitchens_location_constant, t_base, t_mean_reg_months[month])

    return hdd_tot

def get_hdd_country(regions, data):
    """Calculate total number of heating degree days in a region for the base year

    Parameters
    ----------
    regions : dict
        Dictionary containing regions
    data : dict
        Dictionary with data
    """
    #temp_data = data['temp_mean']

    hdd_country = 0
    hdd_regions = {}
    t_base = data['assumptions']['t_base_heating_resid']['base_yr']

    for region in regions:

        coordinates_of_region = "TODO"
        #reclassify region #TODO         # Regional HDD #CREATE DICT WHICH POINT IS IN WHICH REGION (e.g. do with closest)
        temperature_region_relocated = get_temp_region(region, coordinates_of_region)
        t_mean_reg_months = data['temp_mean'][temperature_region_relocated]

        hdd_reg = get_tot_y_hdd_reg(t_mean_reg_months, t_base)

        hdd_regions[region] = hdd_reg # get regional temp over year
        hdd_country += hdd_reg # Sum regions

    return hdd_regions

def t_base_sigm(curr_y, assumptions, base_yr, end_yr, t_base_str):
    """Calculate base temperature depending on sigmoid diff and location

    Depending on the base temperature in the base and end year
    a sigmoid diffusion from the base temperature from the base year
    to the end year is calculated

    This allows to model changes e.g. in thermal confort

    Parameters
    ----------
    curr_y : float
        Current Year
    assumptions : dict
        Dictionary with assumptions
    base_yr : float
        Base year
    end_yr : float
        Simulation End year

    Return
    ------
    t_base_cy : float
        Base temperature of current year
    """
    # Base temperature of end year minus base temp of base year
    t_base_diff = assumptions[t_base_str]['end_yr'] - assumptions[t_base_str]['base_yr']

    # Sigmoid diffusion
    t_base_frac = sigmoid_diffusion(base_yr, curr_y, end_yr, assumptions['sig_midpoint'], assumptions['sig_steeppness'])

    # Temp diff until current year
    t_diff_cy = t_base_diff * t_base_frac

    # Add temp change to base year temp
    t_base_cy = t_diff_cy + assumptions[t_base_str]['base_yr']

    return t_base_cy

def linear_diff(base_yr, curr_yr, value_start, value_end, sim_years):
    """This function assumes a linear fuel_enduse_switch diffusion.

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.
    Parameters
    ----------
    base_yr : int
        The year of the current simulation.
    curr_yr : int
        The year of the current simulation.
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    sim_years : str
        Total number of simulated years.
    Returns
    -------
    fract_sy : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    # If current year is base year, return zero
    if curr_yr == base_yr or sim_years == 0:
        fract_sy = 0
    else:
        fract_sy = np.divide((value_end - value_start), (sim_years - 1)) * (curr_yr - base_yr) #-1 because in base year no change

    return fract_sy

def sigmoid_diffusion(base_yr, curr_yr, end_yr, sig_midpoint, sig_steeppness):
    """Calculates a sigmoid diffusion path of a lower to a higher value where saturation is assumed at the endyear

    Parameters
    ----------
    base_yr : int
        Base year of simulation period
    curr_yr : int
        The year of the current simulation
    end_yr : int
        The year a fuel_enduse_switch saturaes
    sig_midpoint : float
        Mid point of sigmoid diffusion function can be used to shift curve to the left or right (standard value: 0)
    sig_steeppness : float
        Steepness of sigmoid diffusion function The steepness of the sigmoid curve (standard value: 1)

    Returns
    -------
    cy_p : float
        The fraction of the diffusion in the current year

    Infos
    -------
    It is always assuemed that for the simulation year the share is
    replaced with technologies having the efficencies of the current year. For technologies
    which get replaced fast (e.g. lightbulb) this is corret assumption, for longer lasting
    technologies, thie is more problematic (in this case, over every year would need to be iterated
    and calculate share replaced with efficiency of technology in each year).

    TODO: Always return positive value. Needs to be considered for changes in negative
    """
    if curr_yr == base_yr:
        return 0

    if curr_yr == end_yr:
        return 1 # 100 % diffusion
    else:
        # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
        if end_yr == base_yr:
            y_trans = 6.0
        else:
            y_trans = -6.0 + (12.0 / (end_yr - base_yr)) * (curr_yr - base_yr)

        # Get a value between 0 and 1 (sigmoid curve ranging from 0 to 1)
        cy_p = np.divide(1, (1 + m.exp(-1 * sig_steeppness * (y_trans - sig_midpoint))))

        return cy_p

def calc_cdd(t_base_cooling_resid, temperatures):
    """Calculate cooling degree days

    The Cooling Degree Days are calculated based on
    cooling degree hours with temperatures of a full year

    Parameters
    ----------
    t_base_cooling_resid : float
        Base temperature for cooling
    temperatures : array
        Temperatures for every hour in a year

    Return
    ------
    cdd_d : array
        Contains all CDD for every day in a year (365, 1)

    Info
    -----
    For more info see Formual 2.1: Degree-days: theory and application

    https://www.designingbuildings.co.uk/wiki/Cooling_degree_days
    """
    cdd_d = np.zeros((365, 1))

    for day_nr, day in enumerate(temperatures):
        sum_d = 0
        for temp_h in day:
            diff_t = temp_h - t_base_cooling_resid

            if diff_t > 0: # Only if cooling is necessary
                sum_d += diff_t

        cdd_d[day_nr] = np.divide(sum_d, 24)

    return cdd_d

def change_temp_data_climate_change(data):
    """Change temperature data for every year depending on simple climate change assumptions

    Parameters
    ---------
    data : dict
        Data

    Returns
    -------
    temp_data_climate_change : dict
        Adapted temperatures for all weather stations depending on climate change assumptions
    """
    temp_data_climate_change = {}

    # Change weather for all weater stations
    for weather_station_id in data['temperature_data']:
        temp_data_climate_change[weather_station_id] = {}

        # Iterate over simulation period
        for current_year in data['data_ext']['glob_var']['sim_period']:
            temp_data_climate_change[weather_station_id][current_year] = np.zeros((365, 24)) # Initialise

            # Iterate every month and substract
            for yearday in range(365):

                # Create datetime object
                date_object = convert_yearday_to_date(data['data_ext']['glob_var']['base_yr'], yearday)

                # Get month of yearday
                month_yearday = date_object.timetuple().tm_mon - 1

                # Get linear diffusion of current year
                temp_by = 0
                temp_ey = data['assumptions']['climate_change_temp_diff_month'][month_yearday]

                lin_diff_current_year = linear_diff(
                    data['data_ext']['glob_var']['base_yr'],
                    current_year,
                    temp_by,
                    temp_ey,
                    len(data['data_ext']['glob_var']['sim_period'])
                )

                # Iterate hours of base year
                for h, temp_old in enumerate(data['temperature_data'][weather_station_id][yearday]):
                    temp_data_climate_change[weather_station_id][current_year][yearday][h] = temp_old + lin_diff_current_year

    return temp_data_climate_change

def get_heatpump_eff(temp_yr, m_slope, b, t_base_heating):
    """Calculate efficiency according to temperatur difference of base year

    For every hour the temperature difference is calculated and the efficiency of the heat pump calculated
    based on efficiency assumptions

    #TODO: EITHER ASSUME DIFFERENT HEAT PUMP TECHNOLOGIES OR HEAT PUMP MIX TO CALCULATE EFFICIENCY

    Parameters
    ----------
    temp_yr : array
        Temperatures for every hour in a year (365, 24)
    m_slope : float
        Slope of efficiency of heat pump for different temperatures
    b : float
        Intercept (TODO: define for slope...(check in excel for GSHP and HSP))
    t_base_heating : float
        Base temperature for heating

    Return
    ------
    eff_hp_yh : array (365, 24)
        Efficiency for every hour in a year

    Info
    -----
    The efficiency assumptions of the heat pump are taken from Staffell et al. (2012).

    Staffell, I., Brett, D., Brandon, N., & Hawkes, A. (2012). A review of domestic heat pumps.
    Energy & Environmental Science, 5(11), 9291. https://doi.org/10.1039/c2ee22653g
    """
    eff_hp_yh = np.zeros((365, 24))

    for day, temp_day in enumerate(temp_yr):
        for h_nr, temp_h in enumerate(temp_day):
            if t_base_heating < temp_h:
                h_diff = 0
            else:
                if temp_h < 0: #below zero temp
                    h_diff = t_base_heating + abs(temp_h)
                else:
                    h_diff = abs(t_base_heating - temp_h)
            eff_hp_yh[day][h_nr] = m_slope * h_diff + b #[day][h_nr]

    return eff_hp_yh

def const_eff_yh(input_eff):
    """Assing a constant efficiency to every hour in a year

    Parameters
    ----------
    input_eff : float
        Efficiency of a technology

    Return
    ------
    eff_yh : array
        Array with efficency for every hour in a year (365,24)
    """
    eff_yh = np.zeros((365, 24))
    eff_yh += input_eff
    return eff_yh

def init_dict(first_level_keys, crit):
    """Initialise a  dictionary with one level

    Parameters
    ----------
    first_level_keys : list
        First level data
    crit : str
        Criteria wheater initialised with `{}` or `0`

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = {}

    # Iterate first level
    for first_key in first_level_keys:
        if crit == 'brackets':
            one_level_dict[first_key] = {}
        if crit == 'zero':
            one_level_dict[first_key] = 0

    return one_level_dict

def init_nested_dict(first_level_keys, second_level_keys, crit):
    """Initialise a nested dictionary with two levels

    Parameters
    ----------
    first_level_keys : list
        First level data
    second_level_keys : list
        Data to add in nested dict
    crit : str
        Criteria wheater initialised with `{}` or `0`

    Returns
    -------
    nested_dict : dict
        Nested 2 level dictionary
    """
    nested_dict = {}

    for first_level_key in first_level_keys:
        nested_dict[first_level_key] = {}
        for second_level_key in second_level_keys:
            if crit == 'brackets':
                nested_dict[first_level_key][second_level_key] = {}
            if crit == 'zero':
                nested_dict[first_level_key][second_level_key] = 0

    return nested_dict

def sum_2_level_dict(two_level_dict):
    """Sum all entries in a two level dict

    Parameters
    ----------
    two_level_dict : dict
        Nested dict

    Returns
    -------
    tot_sum : float
        Number of all entries in nested dict
    """
    tot_sum = 0
    for i in two_level_dict:
        for j in two_level_dict[i]:
            tot_sum += two_level_dict[i][j]

    return tot_sum

def generate_sig_diffusion(data):
    """Calculates parameters for sigmoid diffusion of technologies which are switched to (installed technologies)

    Parameters
    ----------
    data : dict
        Data

    Return
    ------
    data['assumptions'] : dict
        Data dictionary containing all calculated parameters in assumptions

    Info
    ----
    It is assumed that the technology diffusion is the same over all the uk (no regional different diffusion)
    """
    enduses_with_fuels = data['fuel_raw_data_resid_enduses'].keys() # All endueses with provided fuels

    # Test is Service Switch is implemented
    if len(data['assumptions']['service_tech_by_p']) >= 1:
        service_switch_crit = True
    else:
        service_switch_crit = False
    

    # Sigmoid calculation in case of service switch
    if service_switch_crit:

        data['assumptions']['installed_tech'] = data['assumptions']['tech_increased_service'] # Tech with lager service shares in end year
        data['assumptions']['service_tech_p'] = data['assumptions']['service_tech_by_p'] # Base year service tech

        service_tech_switched_p = data['assumptions']['share_service_tech_ey_p'] # End year service shares (scenaric input)

        # Maximum shares of each technology
        l_values_sig = data['assumptions']['test_assump_max_share_L']


    else:
        # Fuel Switches - Calculate all technologies installed in fuel switches
        data['assumptions']['installed_tech'] = get_tech_installed(data['assumptions']['resid_fuel_switches'])

        # Convert fuel to energy service
        data['assumptions']['service_tech_p'], data['assumptions']['service_fueltype_tech_p'] = calc_service_fueltype_tech(
            data['lu_fueltype'],
            data['fuel_raw_data_resid_enduses'],
            data['assumptions']['fuel_enduse_tech_p_by'],
            data['fuel_raw_data_resid_enduses'],
            data['assumptions']['technologies']
        )

        # ---------------------------------------------------------------------
        # Write out txt file with service shares for each technology per enduse
        # ---------------------------------------------------------------------
        write_out_txt(data['path_dict']['path_txt_service_tech_p'], data['assumptions']['service_tech_p'])
        print("... a file has been generated which shows the shares of each technology per enduse")

        # Calculate service per fueltype in percentage of total service
        data['assumptions']['service_fueltype_p'] = calc_service_fueltype(
            data['lu_fueltype'],
            data['assumptions']['service_tech_p'],
            data['assumptions']['technologies']
        )

        # Calculate energy service demand after fuel switches to future year for each technology
        service_tech_switched_p = calc_service_fuel_switched(
            enduses_with_fuels,
            data['assumptions']['resid_fuel_switches'],
            data['assumptions']['service_fueltype_p'],
            data['assumptions']['service_tech_p'],
            data['assumptions']['fuel_enduse_tech_p_by'],
            data['assumptions']['installed_tech'],
            'actual_switch'
        )

        # Calculate L for every technology for sigmod diffusion
        l_values_sig = tech_L_sigmoid(enduses_with_fuels, data, data['assumptions'])

    # -------------------------------------------------------------
    # Calclulate sigmoid parameters for every installed technology
    # -------------------------------------------------------------
    data['assumptions']['sigm_parameters_tech'] = tech_sigmoid_parameters(
        service_switch_crit,
        data['assumptions']['installed_tech'],
        enduses_with_fuels,
        data['assumptions']['technologies'],
        data['data_ext'],
        l_values_sig,
        data['assumptions']['service_tech_p'],
        service_tech_switched_p,
        data['assumptions']['resid_fuel_switches']
    )

    return data['assumptions']

'''def create_lu_fueltypes(technologies):
    """Create lookup-table for all technologies

    Parameters
    ----------
    technologies : dict
        All defined technologies

    Returns
    -------
    tech_fueltype : dict
        Fueltype of each technology
    """
    tech_fueltype = {}
    for technology in technologies:
        tech_fueltype[technology] = technologies[technology]['fuel_type']

    return tech_fueltype
'''

def calc_service_fueltype_tech(fueltypes_lu, enduses, fuel_p_tech_by, fuels, tech_stock):
    """Calculate total energy service percentage of each technology and energy service percentage within the fueltype

    This calculation converts fuels into energy services (e.g. heating for fuel into heat demand)
    and then calculated how much an invidual technology contributes in percent to total energy
    service demand.

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.

    Parameters
    ----------
    fueltypes_lu : dict
        Fueltypes
    enduses : list
        All enduses to perform calulations
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    tech_stock : object
        Technology stock of base year (region dependent)

    Return
    ------
    service_tech_p : dict
        Percentage of total energy service per technology for base year
    service_fueltype_tech_p : dict
        Percentage of energy service witin a fueltype for all technologies with this fueltype for base year

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region.
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.
    """
    service = init_nested_dict(enduses, fueltypes_lu.values(), 'brackets') # Energy service per technology for base year (e.g. heat demand in joules)
    service_tech_p = init_dict(enduses, 'brackets') # Percentage of total energy service per technology for base year
    service_fueltype_tech_p = init_nested_dict(enduses, fueltypes_lu.values(), 'brackets') # Percentage of energy service for technologies within the fueltypes

    for enduse in enduses: # Iterate enduse
        for fueltype, fuel_fueltype in enumerate(fuels[enduse]): # Iterate fueltype
            tot_service_fueltype = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech in fuel_p_tech_by[enduse][fueltype]:

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_p_tech_by[enduse][fueltype][tech] * fuel_fueltype[0]

                # Energy service of end use: Fuel of technoloy * efficiency == Service (e.g.heat demand in Joules)
                service_fueltype_tech = fuel_tech * tech_stock[tech]['eff_by']

                service[enduse][fueltype][tech] = service_fueltype_tech # Add energy service demand to dict
                tot_service_fueltype += service_fueltype_tech # Total energy service demand within a fueltype

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]: # Iterate technologis in defined tech stock
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_p[enduse][fueltype][tech] = 0
                else:
                    service_fueltype_tech_p[enduse][fueltype][tech] = (1 / tot_service_fueltype) * service[enduse][fueltype][tech] #* (fuel_p_tech_by[enduse][fueltype][tech] * fuel_fueltype[0] * tech_stock[tech]['eff_by'])

        # Calculate percentage of service of all technologies
        total_service = sum_2_level_dict(service[enduse]) #Total service demand

        # Percentage of energy service per technology
        for fueltype in service[enduse]:
            for technology in service[enduse][fueltype]:
                service_tech_p[enduse][technology] = (1 / total_service) * service[enduse][fueltype][technology]

    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    for enduse in service_tech_p:
        print("Enduse: " + str(enduse))
        print(service_tech_p[enduse].values())
        sum_service_p = sum(service_tech_p[enduse].values())
        assert sum_service_p == 1.0, "The energy service for all technologies is not 100% (1.0)"

    # Test if within fueltype always 100 energy service
    for enduse in service_fueltype_tech_p:
        for fueltype in service_fueltype_tech_p[enduse]:
            sum_service_fueltype_p = sum(service_fueltype_tech_p[enduse][fueltype].values())
            print("sum_service_fueltype_p: " + str(sum_service_fueltype_p))
            assert sum_service_fueltype_p == 1.0 or sum_service_fueltype_p == 0.0, "The energy service for all technologies within a fueltype is not 100% (1.0)"
    '''
    return service_tech_p, service_fueltype_tech_p

def calc_service_fuel_switched(enduses, fuel_switches, service_fueltype_p, service_tech_p, fuel_enduse_tech_p_by, installed_tech_switches, switch_type):
    """Calculate energy service demand percentages after fuel switches

    Parameters
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    fuel_switches : dict
        Fuel switches
    service_fueltype_p : dict
        Service demand per fueltype
    fuel_tech_p_by : dict
        Technologies in base year
    service_tech_p : dict
        Percentage of service demand per technology for base year
    tech_fueltype_by : dict
        Technology stock
    fuel_enduse_tech_p_by : dict
        Fuel shares for each technology of an enduse
    installed_tech_switches : dict
        Technologies which are installed in fuel switches
    maximum_switch : crit
        Wheater this function is executed with the switched fuel share or the maximum switchable fuel share

    Return
    ------
    service_tech_switched_p : dict
        Service in future year with added and substracted service demand for every technology

    Notes
    -----
    Implement changes in heat demand (all technolgies within a fueltypes are replaced proportionally)
    """
    service_tech_switched_p = copy.deepcopy(service_tech_p)

    for enduse in enduses: # Iterate enduse
        for fuel_switch in fuel_switches: # Iterate fuel switches
            if fuel_switch['enduse'] == enduse: # If fuel is switched in this enduse

                # Check if installed technology is considered for fuelswitch
                if fuel_switch['technology_install'] in installed_tech_switches[enduse]:

                    # Share of energy service before switch
                    orig_service_p = service_fueltype_p[enduse][fuel_switch['enduse_fueltype_replace']]

                    # Service demand per fueltype that will be switched
                    if switch_type == 'max_switch':
                        change_service_fueltype_p = orig_service_p * fuel_switch['max_theoretical_switch'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent
                    elif switch_type == 'actual_switch':
                        change_service_fueltype_p = orig_service_p * fuel_switch['share_fuel_consumption_switched'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent

                    # ---SERVICE DEMAND ADDITION
                    service_tech_switched_p[enduse][fuel_switch['technology_install']] += change_service_fueltype_p

                    # Get all technologies which are replaced related to this fueltype
                    replaced_tech_fueltype = fuel_enduse_tech_p_by[enduse][fuel_switch['enduse_fueltype_replace']].keys()

                    # Calculate total energy service in this fueltype, Substract service demand for replaced technologies
                    for tech in replaced_tech_fueltype:
                        service_tech_switched_p[enduse][tech] -= change_service_fueltype_p * service_tech_p[enduse][tech]

    return service_tech_switched_p

def calc_regional_service_demand(fuel_shape_yh, fuel_enduse_tech_p_by, fuels, tech_stock):
    """Calculate energy service of each technology based on assumptions about base year fuel shares of an enduse

    This calculation converts fuels into energy services (e.g. fuel for heating into heat demand)
    and then calculates the fraction of an invidual technology to which it contributes to total energy
    service (e.g. how much of total heat demand condensing boilers contribute).

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.
    The diffusion is always relative to the service demand (e.g. 10% of heating is provided by a technology)

    Parameters
    ----------
    fuel_shape_yh : array
        Shape how the fuel is distributed over a year (y to h)
    fuel_enduse_tech_p_by : dict
        Fuel composition of base year for every fueltype for each enduse
    fuels : array
        Base year fuel demand
    tech_stock : object
        Technology stock of region

    Return
    ------
    total_service_yh : array
        Total energy service per technology for base year (365, 24)
    service : dict
        Energy service for every fueltype and technology (dict[fueltype][tech])
    
    Info
    -----
    Energy service = fuel * efficiency
    
    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.
    """
    # Energy service per technology for base year (e.g. heat demand in joules)
    service = {}

    # Iterate fueltype
    for fueltype, fuel_enduse in enumerate(fuels):
        service[fueltype] = {}

        # Iterate technologies to calculate share of energy service depending on fuel and efficiencies (average efficiency across whole year)
        for tech in fuel_enduse_tech_p_by[fueltype]:

            # Fuel share based on defined fuel fraction within fueltype (share of fuel of technology * tot fuel)
            fuel_tech = fuel_enduse_tech_p_by[fueltype][tech] * fuel_enduse[0]

            # Distribute fuel into every hour based on shape how the fuel is distributed over the year
            fuel_tech_h = fuel_shape_yh * fuel_tech

            # Convert to energy service (Energy service = fuel * efficiency)
            service[fueltype][tech] = fuel_tech_h * tech_stock.get_tech_attribute(tech, 'eff_by')

            #print("conerting fuel to heat tech: " + str(tech) + str( "  ") + str(fuel_tech) + str("  ") + str(np.average(tech_stock.get_tech_attribute(tech, 'eff_by'))))
            #print("TESTING SHAPE: "  + str(np.sum(fuel_shape_yh)))

    # Calculate energy service demand over the full year and for every hour
    total_service_yh = np.zeros((365, 24))
    for fueltype in service:
        for tech in service[fueltype]:
            total_service_yh += service[fueltype][tech] # (365 * 365 shapes)

    return total_service_yh, service

def calc_service_fueltype(lu_fueltype, service_tech_p, tech_stock):
    """Calculate service per fueltype in percentage of total service

    Parameters
    ----------
    service_tech_p : dict
        Service demand per technology
    tech_stock : dict
        Technologies with all attributes

    Return
    ------
    energy_service_fueltype : dict
        Percentage of total (iterate over all technologis with this fueltype) service per fueltype

    Example
    -----
    (e.g. 0.5 gas, 0.5 electricity)

    """
    service_fueltype = init_nested_dict(service_tech_p.keys(), range(len(lu_fueltype)), 'zero') # Energy service per technology for base year (e.g. heat demand in joules)

    # Iterate technologies for each enduse and their percentage of total service demand
    for enduse in service_tech_p:

        # Iterate technologies in enduse
        for technology in service_tech_p[enduse]:

            # Add percentage of total enduse to fueltype
            service_fueltype[enduse][tech_stock[technology]['fuel_type']] += service_tech_p[enduse][technology]

    return service_fueltype

def get_tech_installed(fuel_switches):
    """Read out all technologies which are specifically switched to

    Parameter
    ---------
    fuel_switches : dict
        All fuel switches where a share of a fuel of an enduse is switched to a specific technology

    Return
    ------
    installed_tech : list
        List with all technologies where a fuel share is switched to
    """

    # Add technology list for every enduse with affected switches
    installed_tech = {}
    for switch in fuel_switches:
        installed_tech[switch['enduse']] = []

    for switch in fuel_switches:
        enduse_fuelswitch = switch['enduse']
        if switch['technology_install'] not in installed_tech[enduse_fuelswitch]:
            installed_tech[enduse_fuelswitch].append(switch['technology_install'])

    return installed_tech

def tech_L_sigmoid(enduses, data, assumptions):
    """Calculate L value for every installed technology with maximum theoretical replacement value

    Parameters
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    data : dict
        Data
    assumptions : dict
        Assumptions

    Returns
    -------
    l_values_sig : dict
        L value for sigmoid diffusion of all technologies for which a switch is implemented

    Notes
    -----
    Gets second sigmoid point
    """
    l_values_sig = init_dict(enduses, 'brackets')

    for enduse in enduses:
        # Check wheter there are technologies in this enduse which are switched
        if enduse not in assumptions['installed_tech']:
            print("No technologies to calculate sigmoid")
        else:

            # Iterite list with enduses where fuel switches are defined
            for technology in assumptions['installed_tech'][enduse]:

                # Calculate service demand for specific tech
                tech_install_p = calc_service_fuel_switched(
                    data['resid_enduses'],
                    assumptions['resid_fuel_switches'],
                    assumptions['service_fueltype_p'], # Service demand for enduses and fueltypes
                    assumptions['service_tech_p'], # Percentage of service demands for every technology
                    assumptions['fuel_enduse_tech_p_by'],
                    {str(enduse): [technology]},
                    'max_switch'
                    )

                # Read out L-values with calculating sigmoid diffusion with maximum theoretical replacement
                l_values_sig[enduse][technology] = tech_install_p[enduse][technology]

    return l_values_sig

def tech_sigmoid_parameters(service_switch_crit, installed_tech, enduses, tech_stock, data_ext, L_values, service_tech_p, service_tech_switched_p, resid_fuel_switches):
    """Calculate diffusion parameters based on energy service demand in base year and projected future energy service demand

    The future energy servie demand is calculated based on fuel switches. A sigmoid diffusion is fitted.

    Parameters
    ----------
    service_switch_crit : bool
        Criteria whether sigmoid is calculated for service switch or not
    installed_tech : dict
        Technologies for enduses with fuel switch
    enduses : enduses
        enduses
    tech_stock : dict
        Technologies of base year
    data_ext : dict
        External data_ext
    installed_tech : dict
        List with installed technologies in fuel switches
    L_values : dict
        L values for maximum possible diffusion of technologies
    service_tech_p : dict
        Energy service demand for base year (1.sigmoid point)
    service_tech_switched_p : dict
        Service demand after fuelswitch
    resid_fuel_switches : dict
        Fuel switch information

    Returns
    -------
    sigmoid_parameters : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)

    Notes
    -----
    NTH: improve fitting

    Manually the fitting parameters can be defined which are not considered as a good fit: fit_crit_A, fit_crit_B
    """
    sigmoid_parameters = init_nested_dict(enduses, installed_tech, 'brackets')

    for enduse in enduses:
        if enduse not in installed_tech:
            print("No switch to calculate....")
        else:
            for technology in installed_tech[enduse]:

                sigmoid_parameters[enduse][technology] = {} # Initialise

                if service_switch_crit:

                    # Year until service are switched
                    year_until_switched = data_ext['glob_var']['end_yr']
                    #TODO: IMPROVE THAT A FUTURE ENTRY MARKET CAN BE DEFINED FOR EACH TECHNOLOGY
                    #market_entry = 2015
                    market_entry = tech_stock[technology]['market_entry']
                else:
                    # Get year which is furtherst away of all switch to installed technology
                    year_until_switched = 0
                    for switch in resid_fuel_switches:
                        if switch['enduse'] == enduse and switch['technology_install'] == technology:
                            if year_until_switched < switch['year_fuel_consumption_switched']:
                                year_until_switched = switch['year_fuel_consumption_switched']
                    market_entry = tech_stock[technology]['market_entry']

                # Test wheter technology has the market entry before or after base year, If afterwards, set very small number in market entry year
                if market_entry > data_ext['glob_var']['base_yr']:
                    point_x_by = market_entry
                    point_y_by = 0.001 # if market entry in a future year
                else: # If market entry before, set to 2015
                    point_x_by = data_ext['glob_var']['base_yr']
                    point_y_by = service_tech_p[enduse][technology]

                    #If the base year is the market entry year use a very small number (as otherwise the fit does not work)
                    if point_y_by == 0:
                        point_y_by = 0.001

                # Future energy service demand (second point on sigmoid curve for fitting)
                point_x_projected = year_until_switched
                point_y_projected = service_tech_switched_p[enduse][technology]

                # Data of the two points
                xdata = np.array([point_x_by, point_x_projected])
                ydata = np.array([point_y_by, point_y_projected])

                # Parameter fitting
                possible_start_parameters = [0.001, 0.01, 0.1, 1, 2, 3, 4, 5, 10, 12, 15, 20, 40, 60, 100, 200, 400, 500, 1000]

                cnt = 0
                successfull = False
                while not successfull:
                    start_parameters = [possible_start_parameters[cnt], possible_start_parameters[cnt]]

                    try:
                        print("--------------- Technology " + str(technology))
                        print("xdata: " + str(point_x_by) + str("  ") + str(point_x_projected))
                        print("ydata: " + str(point_y_by) + str("  ") + str(point_y_projected))
                        print("Lvalue: " + str(L_values[enduse][technology]))

                        fit_parameter = fit_sigmoid_diffusion(L_values[enduse][technology], xdata, ydata, start_parameters)

                        # Define manually when a fit is not successefful
                        fit_crit_A = 50
                        fit_crit_B = 0.01
                        if fit_parameter[0] > fit_crit_A or fit_parameter[0] < fit_crit_B:
                            successfull = False
                        else:
                            successfull = True
                        print("Fit successful for Technology: {} with fitting parameters: ".format(technology) + str(fit_parameter))
                    except:
                        print("Tried unsuccessfully to do the fit with the following parameters: " + str(start_parameters[1]))
                        cnt += 1

                        if cnt >= len(possible_start_parameters):
                            sys.exit("Error: CURVE FITTING DID NOT WORK")

                # Insert parameters
                sigmoid_parameters[enduse][technology]['midpoint'] = fit_parameter[0] #midpoint (x0)
                sigmoid_parameters[enduse][technology]['steepness'] = fit_parameter[1] #Steepnes (k)
                sigmoid_parameters[enduse][technology]['l_parameter'] = L_values[enduse][technology]
                #print("Insterted parameters: " + str(sigmoid_parameters[enduse][technology]))

                #plot sigmoid curve
                plotout_sigmoid_tech_diff(L_values, technology, enduse, xdata, ydata, fit_parameter)

    return sigmoid_parameters

def sigmoid_function(x, L, midpoint, steepness):
    """Sigmoid function

    Paramters
    ---------
    x : float
        X-Value
    L : float
        The durv'es maximum value
    midpoint : float
        The midpoint x-value of the sigmoid's midpoint
    k : dict
        The steepness of the curve

    Return
    ------
    y : float
        Y-Value

    Notes
    -----
    This function is used for fitting and plotting

    """
    y = L / (1 + np.exp(-steepness * ((x - 2000) - midpoint)))
    return y

def plotout_sigmoid_tech_diff(L_values, technology, enduse, xdata, ydata, fit_parameter):
    """Plot sigmoid diffusion
    """
    L = L_values[enduse][technology]
    x = np.linspace(2015, 2100, 100)
    y = sigmoid_function(x, L, *fit_parameter)

    fig = plt.figure()
    fig.set_size_inches(12, 8)
    pylab.plot(xdata, ydata, 'o', label='base year and future market share')
    pylab.plot(x, y, label='fit')
    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')
    pylab.xlabel('Time')
    pylab.ylabel('Market share of technology on energy service')
    pylab.title("Sigmoid diffusion of technology  {}  in enduse {}".format(technology, enduse))

    pylab.show()

def fit_sigmoid_diffusion(L, x_data, y_data, start_parameters):
    """Fit sigmoid curve based on two points on the diffusion curve

    Parameters
    ----------
    L : float
        The sigmoids curve maximum value (max consumption)
    x_data : array
        X coordinate of two points
    y_data : array
        X coordinate of two points

    Returns
    -------
    popt : dict
        Fitting parameters

    Info
    ----
    The Sigmoid is substacted - 2000 to allow for better fit with low values

    RuntimeWarning is ignored

    """
    def sigmoid_fitting_function(x, x0, k):
        """Sigmoid function used for fitting
        """
        y = np.divide(L, 1 + np.exp(-k * ((x - 2000) - x0)))
        return y

    popt, _ = curve_fit(sigmoid_fitting_function, x_data, y_data, p0=start_parameters)

    return popt

def calc_distance_two_points(long_from, lat_from, long_to, lat_to):
    """Calculate distance between two points

    Parameters
    ----------
    long_from : float
        Longitute coordinate from point
    lat_from : float
        Latitute coordinate from point
    long_to : float
        Longitute coordinate to point
    lat_to : float
        Latitue coordinate to point

    Return
    ------
    distance : float
        Distance
    """
    from_pnt = (long_from, lat_from)
    to_pnt = (long_to, lat_to)
    distance = haversine(from_pnt, to_pnt, miles=False)

    return distance

def search_closest_weater_station(longitude_reg, latitue_reg, weather_stations):
    """Search ID of closest weater station

    Parameters
    ----------
    longitude_reg : float
        Longitute coordinate of Region Object
    latitue_reg : float
        Latitute coordinate of Region Object
    weather_stations : dict
        Weater station data

    Return
    ------
    closest_id : int
        ID of closest weather station
    """
    closest_dist = 99999999999

    for station_id in weather_stations:

        dist_to_station = calc_distance_two_points(
            longitude_reg,
            latitue_reg,
            weather_stations[station_id]['station_latitude'],
            weather_stations[station_id]['station_longitude']
        )

        if dist_to_station < closest_dist:
            closest_dist = dist_to_station
            closest_id = station_id

    return closest_id

def get_fueltype_str(fueltype_lu, fueltype_nr):
    """Read from dict the fueltype string based on fueltype KeyError

    Inputs
    ------
    fueltype_lu : dict
        Fueltype lookup dictionary
    fueltype_nr : int
        Key which is to be found in lookup dict

    Returns
    -------
    fueltype_in_string : str
        Fueltype string
    """
    for fueltype_str in fueltype_lu: # data['lu_fueltype']:
        if fueltype_lu[fueltype_str] == fueltype_nr:
            fueltype_in_string = fueltype_str
            break
    return fueltype_in_string

def generate_heat_pump_from_split(data, temp_dependent_tech_list, technologies, heat_pump_assump):
    """Delete all heat_pump from tech dict and define averaged new heat pump technologies 'av_heat_pump_fueltype' with
    efficiency depending on installed ratio
    
        Parameters
    ----------
    temp_dependent_tech_list : list
        List to store temperature dependent technologies (e.g. heat-pumps)
    technologies : dict
        Technologies
    heat_pump_assump : dict
        The split of the ASHP and GSHP is provided
    
    Returns
    -------
    technologies : dict
        Technologies with added averaged heat pump technologies for every fueltype

    temp_dependent_tech_list : list
        List with added temperature dependent technologies


    Info
    ----
    # Assumptions:
    - Market Entry of different technologies must be the same year! (the lowest is selected if different years)
    - diff method is linear
    """
    # Calculate average efficiency of heat pump depending on installed ratio
    for fueltype in heat_pump_assump:
        av_eff_hps_by = 0
        av_eff_hps_ey = 0
        eff_achieved_av = 0
        market_entry_lowest = 2200

        for heat_pump_type in heat_pump_assump[fueltype]:
            share_heat_pump = heat_pump_assump[fueltype][heat_pump_type]
            eff_heat_pump_by = technologies[heat_pump_type]['eff_by'] #Base year efficiency
            eff_heat_pump_ey = technologies[heat_pump_type]['eff_ey'] #End year efficiency
            eff_achieved = technologies[heat_pump_type]['eff_achieved'] #End year efficiency
            market_entry = technologies[heat_pump_type]['market_entry'] #End year efficiency

            # Calc average values
            av_eff_hps_by += share_heat_pump * eff_heat_pump_by
            av_eff_hps_ey += share_heat_pump * eff_heat_pump_ey
            eff_achieved_av += share_heat_pump * eff_achieved

            if market_entry < market_entry_lowest:
                market_entry_lowest = market_entry

        # Add average 'av_heat_pumps' to technology dict
        fueltype_string = get_fueltype_str(data['lu_fueltype'], fueltype)
        name_av_hp = "av_heat_pump_{}".format(str(fueltype_string))
        print("Create new averaged heat pump technology: " + str(name_av_hp))

        # Add technology to temperature dependent technology list
        temp_dependent_tech_list.append(name_av_hp)
        

        # Add new averaged technology
        technologies[name_av_hp] = {}
        technologies[name_av_hp]['fuel_type'] = fueltype
        technologies[name_av_hp]['eff_by'] = av_eff_hps_by
        technologies[name_av_hp]['eff_ey'] = av_eff_hps_ey
        technologies[name_av_hp]['eff_achieved'] = eff_achieved_av
        technologies[name_av_hp]['diff_method'] = 'linear'
        technologies[name_av_hp]['market_entry'] = market_entry_lowest

    # Remove all heat pumps from tech dict
    for fueltype in heat_pump_assump:
        for heat_pump_type in heat_pump_assump[fueltype]:
            del technologies[heat_pump_type]

    return technologies, temp_dependent_tech_list

def get_diff_direct_installed(service_tech_by_p, share_service_tech_ey_p, assumptions):
    """Get all those technologies with increased service in future

    Parameters
    ----------
    service_tech_by_p : dict
        Share of service per technology of base year of total service
    share_service_tech_ey_p : dict
        Share of service per technology of end year of total service
    assumptions : dict
        assumptions

    Returns
    -------
    assumptions : dict
        assumptions

    Info
    -----
    tech_increased_service : dict
        Technologies with increased future service
    tech_decreased_share : dict
        Technologies with decreased future service
    tech_decreased_share : dict
        Technologies with unchanged future service

    The assumptions are always relative to the simulation end year
    """
    tech_increased_service = {}
    tech_decreased_share = {}
    tech_constant_share = {}

    for enduse in service_tech_by_p:
        tech_increased_service[enduse] = []
        tech_decreased_share[enduse] = []
        tech_constant_share[enduse] = []

        for tech in service_tech_by_p[enduse]: # Calculate fuel for each tech

            # If future larger share
            if service_tech_by_p[enduse][tech] < share_service_tech_ey_p[enduse][tech]:
                tech_increased_service[enduse].append(tech)

            # If future smaller service share
            elif service_tech_by_p[enduse][tech] > share_service_tech_ey_p[enduse][tech]:
                tech_decreased_share[enduse].append(tech)
            else:
                tech_constant_share[enduse].append(tech)
    # Add to data
    assumptions['tech_increased_service'] = tech_increased_service
    assumptions['tech_decreased_share'] = tech_decreased_share
    assumptions['tech_constant_share'] = tech_constant_share

    return assumptions

def get_service_rel_tech_decrease_by(tech_decreased_share, service_tech_by_p):
    """Iterate technologies with future less service demand (replaced tech) and get relative share of service in base year

    Parameters
    ----------
    tech_decreased_share : dict
        Technologies with decreased service
    service_tech_by_p : dict
        Share of service of technologies in by

    Returns
    -------
    relative_share_service_tech_decrease_by : dict
        Relative share of service of replaced technologies
    """
    # Summed share of all diminishing technologies
    sum_service_tech_decrease_p = 0
    for tech in tech_decreased_share:
        sum_service_tech_decrease_p += service_tech_by_p[tech]

    # Relative of each diminishing tech
    relative_share_service_tech_decrease_by = {}
    for tech in tech_decreased_share:
        relative_share_service_tech_decrease_by[tech] = np.divide(1, sum_service_tech_decrease_p) * service_tech_by_p[tech]

    return relative_share_service_tech_decrease_by

def generate_fuel_distribution(enduse_tech_p, technologies, lu_fueltype):
    '''Based on assumptions about energy service delivered by technologies, generate fuel distribution

    As an input, the percentage of energy service (e.g. heating) is provided
    for different technologies. Based on simple efficiency assumptions the
    split within each fueltype is calculated. This can be used to assign
    fuel inputs to different technologies

    # TODO: MAybe do on regional level
    #TODO: Efficiency of base year of heat pumps???
    ALLES NUR GROB GESCHAETZT AUCH MIT EFF VON HEAT PUMPS... ...hybrid tech?
    '''
    fuels_tech_p = {}

    for enduse in enduse_tech_p:

        # Initialise
        initial_service_units = 1000
        fuels_tech_p[enduse] = {}
        for fueltype in lu_fueltype:
            fuels_tech_p[enduse][lu_fueltype[fueltype]] = {}

        # Calculate fuel for each tech
        for tech in enduse_tech_p[enduse]:
            tech_eff_by = technologies[tech]['eff_by'] # Efficiency of technology
            fuel_type = technologies[tech]['fuel_type'] # Fueltype of technology

            # Service of technology (share)
            service_tech_by = enduse_tech_p[enduse][tech] * initial_service_units

            # Fuel of base year
            fuels_tech_p[enduse][fuel_type][tech] = np.divide(service_tech_by, tech_eff_by)

        # Calculate percentage within each fueltype
        for fueltype in fuels_tech_p[enduse]:
            total_fuel_fueltype = sum(fuels_tech_p[enduse][fueltype].values())
            for tech in fuels_tech_p[enduse][fueltype]:

                if total_fuel_fueltype == 0.0: #ALL TO ONE
                    # If no fuel for this technology, assign with 1.0
                    fuels_tech_p[enduse][fueltype][tech] = 1.0 # If not assigned provide 1.0 ()
                else:
                    fuels_tech_p[enduse][fueltype][tech] = np.divide(1, total_fuel_fueltype) * fuels_tech_p[enduse][fueltype][tech]

    return fuels_tech_p


def generate_service_distribution_by(service_tech_by_p, technologies, lu_fueltype):
    """Calculate percentage of service for every fueltype
    """
    service_p = {}

    for enduse in service_tech_by_p:
        service_p[enduse] = {}
        for fueltype in lu_fueltype:
            service_p[enduse][lu_fueltype[fueltype]] = 0

        for tech in service_tech_by_p[enduse]:
            fueltype_tech = technologies[tech]['fuel_type']
            service_p[enduse][fueltype_tech] += service_tech_by_p[enduse][tech]

    return service_p

'''def get_max_fuel_day(fuels):
    """The day with most fuel
    """
    max_fuel = 0
    max_day = None
    for day, fuels_day in enumerate(fuels):
        sum_day_fuel = np.sum(fuels_day)

        if sum_day_fuel > max_fuel:
            max_fuel = sum_day_fuel
            max_day = day

    return max_fuel, max_day
'''

'''def convert_service_tech_to_fuel_p(service_fueltype_tech, tech_stock):
    """ Convert service per technology into fuel percent per technology
    """
    fuel_fueltype_tech = {}

    # Convert service to fuel
    for fueltype in service_fueltype_tech:
        fuel_fueltype_tech[fueltype] = {}
        for tech in service_fueltype_tech[fueltype]:
            service_tech_h = service_fueltype_tech[fueltype][tech]
            fuel_fueltype_tech[fueltype][tech] = service_tech_h / tech_stock.get_tech_attribute(tech, 'eff_cy')

    # Convert to percent within fueltype
    fuel_fueltype_tech_p = {}

    for fueltype in fuel_fueltype_tech:
        fuel_fueltype_tech_p[fueltype] = {}

        # Get sum of fuel within fueltype
        sum_fuel_fueltype = 0
        for tech in fuel_fueltype_tech[fueltype]:
            sum_fuel_fueltype += np.sum(fuel_fueltype_tech[fueltype][tech])
        if sum_fuel_fueltype == 0:
            for tech in fuel_fueltype_tech[fueltype]:
                fuel_fueltype_tech_p[fueltype][tech] = 0
        else:
            for tech in fuel_fueltype_tech[fueltype]:
                fuel_fueltype_tech_p[fueltype][tech] = (1.0 / sum_fuel_fueltype) * np.sum(fuel_fueltype_tech[fueltype][tech])

    return fuel_fueltype_tech_p
'''

'''def calc_age_distribution(age_distr_by, age_distr_ey):
    """ CAlculate share of age distribution of buildings
    DEMOLISHRN RATE?
    """
    # Calculate difference between base yeare and ey
    # --> Add
    assumptions['dwtype_age_distr_by'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    assumptions['dwtype_age_distr_ey'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    return
'''

'''
def convert_to_tech_array(in_dict, tech_lu_resid):
    """Convert dictionary to array

    The input array of efficiency is replaced and technologies are replaced with technology IDs

    # TODO: WRITE DOCUMENTATION
    Parameters
    ----------
    in_dict : dict
        One-level dictionary

    Returns
    -------
    in_dict : array
        Array with identical data of dict

    Example
    -------
    in_dict = {1: "a", 2: "b"} is converted to np.array((1, a), (2,b))
    """
    out_dict = {}

    for fueltype in in_dict:
        a = list(in_dict[fueltype].items())

        # REplace technologies with technology ID
        replaced_tech_with_ID = []
        for enduse_tech_eff in a:
            technology = enduse_tech_eff[0]
            tech_eff = enduse_tech_eff[1]
            replaced_tech_with_ID.append((tech_lu_resid[technology], tech_eff))

        # IF empty replace with 0.0, 0.0) to have an array with length 2
        if replaced_tech_with_ID == []:
            out_dict[fueltype] = []
        else:
            replaced_with_ID = np.array(replaced_tech_with_ID, dtype=float)
            out_dict[fueltype] = replaced_with_ID

    return out_dict
'''

'''def convert_to_array(in_dict):
    """Convert dictionary to array

    As an input the base data is provided and price differences and elasticity

    Parameters
    ----------
    in_dict : dict
        One-level dictionary

    Returns
    -------
    in_dict : array
        Array with identical data of dict

    Example
    -------
    in_dict = {1: "a", 2: "b"} is converted to np.array((1, a), (2,b))
    """
    copy_dict = {}
    for i in in_dict:
        copy_dict[i] = np.array(list(in_dict[i].items()), dtype=float)
    return copy_dict
'''
