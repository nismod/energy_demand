"""This file stores all functions of main.py"""
import os
import csv
import re
from datetime import date
from datetime import timedelta as td
import math as m
import unittest
import numpy as np
import yaml
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def read_txt_t_base_by(path_temp_txt, base_yr):
    """Read out mean temperatures for all regions and store in dict

    Parameters
    ----------
    path_temp_txt : str
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
    all_txt_files = os.listdir(path_temp_txt)
    out_dict = {}

    # Iterate files in folder
    for file_name in all_txt_files:
        reg_name = file_name[:-4] # remove .txt
        file_name = os.path.join(path_temp_txt, file_name)
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

def convert_out_format_es(data, data_ext, resid_object_country):
    """Adds total hourly fuel data into nested dict

    Parameters
    ----------
    data : dict
        Dict with own data
    data_ext : dict
        External data
    resid_object_country : object
        Contains objects of the region

    Returns
    -------
    out_dict : dict
        Returns a dict for energy supply model with fueltype, region, hour"""

    # Create timesteps for full year (wrapper-timesteps)
    out_dict = init_energy_supply_dict(len(data['fuel_type_lu']), data['reg_lu'], data_ext['glob_var']['base_year'])

    for reg_id in data['reg_lu']:
        reg = getattr(resid_object_country, str(reg_id))
        region_name = reg.reg_id # Get object region name
        hourly_all_fuels = reg.tot_all_enduses_h()  # Get total fuel

        # Iterate fueltypes
        for fueltype in data['fuel_type_lu']:
            out_dict[fueltype][region_name] = dict(enumerate(hourly_all_fuels[fueltype])) # Convert array into dict for out_read

    return out_dict

def init_energy_supply_dict(number_fuel_types, reg_dict, base_year):
    """Generates nested dictionary for providing results to smif

    Parameters
    ----------
    number_fuel_types : int
        Number of fuel types
    reg_dict : dict
        Dictionary with number of regions
    base_year : int
        Base year of simulation

    Returns
    -------
    result_dict : dict
        Returns a nested dictionary for energy supply model (fueltype/region/timeID)
    """
    # Create timesteps for full year (wrapper-timesteps)
    timesteps = timesteps_full_year(base_year)

    result_dict = {}
    for i in range(number_fuel_types):
        result_dict[i] = {}
        for j in reg_dict:
            result_dict[i][j] = {}
            for k in timesteps:
                result_dict[i][j][k] = {}
    return result_dict

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

                #if type(i) == str:
                #    print("Error: All fuel input varaibles must be a int or float value (not empty excel row)")

                end_use = _headings[cnt]
                end_uses_dict[end_use][cnt_fueltype] = i
                cnt += 1

    return end_uses_dict

def get_datetime_range(start=None, end=None):
    """Calculates all dates between a star and end date.
    TESTED_PYTEST
    Parameters
    ----------
    start : date
        Start date
    end : date
        end date
    """
    a = []
    span = end - start
    for i in range(span.days + 1):
        a.append(start + td(days=i))
    return list(a)

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

def timesteps_full_year(base_year):
    """A list is generated from the first hour of the base year to the last hour of teh base year

    This function generates a single list from a list with
    containg start and end dates of the base year

    Parameters
    ----------
    base_year : int
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
    list_dates = get_datetime_range(start=date(base_year, 1, 1), end=date(base_year, 12, 31)) # List with every date in a year

    timesteps = {}

    #Add to list
    for day_date in list_dates:
        yearday = day_date.timetuple()[7] - 1 # -1 because in _info yearday 1: 1. Jan    ((tm_year=2015, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=-1))

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
    weekday = date_from_yearday.timetuple()[6] # (tm_year=2015, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=-1)

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

        # Iterate rows
        for row in read_lines:

            # Iterate row entries
            for k, i in enumerate(row):
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
        print("Write YAML file with length: " + str(len(yaml_list)))
        #_, yaml_list = timesteps_full_year(base_year)  # Create timesteps for full year (wrapper-timesteps)
        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)
    return

def write_final_result(data, result_dict, reg_lu, crit_YAML):
    """Write reults for energy supply model

    Parameters
    ----------
    data : dict
        Whether a yaml file should be written or not (1 or 0)
    result_dict : dict
        Dictionary which is stored to txt
    reg_lu : dict
        Look up dictionar for regions
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

                for _day in result_dict[fueltype][reg]:
                    for _hour in range(24):
                        start_id = "P{}H".format(str(_day * 24) + str(_hour))
                        end_id = "P{}H".format(str(_day * 24) + str(_hour + 1))
                        data.append([reg_lu[reg], start_id, end_id, result_dict[fueltype][reg][_day][_hour]])

                        yaml_list_fuel_type.append({'region':  reg_lu[reg], 'start': start_id, 'end': end_id, 'value': float(result_dict[fueltype][reg][_day][_hour]), 'units': 'CHECK GWH', 'year': 'XXXX'})

            csv_writer.writerows(data)

            # Write YAML
            write_YAML(crit_YAML, os.path.join(main_path, 'model_output/YAML_TIMESTEPS_{}.yml'.format(fueltype)), yaml_list_fuel_type)

def convert_to_array(in_dict):
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
        a = list(in_dict[i].items())
        copy_dict[i] = np.array(a, dtype=float)
    return copy_dict

def convert_to_array_technologies(in_dict, tech_lu):
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
            replaced_tech_with_ID.append((tech_lu[technology], tech_eff))

        # IF empty replace with 0.0, 0.0) to have an array with length 2
        if replaced_tech_with_ID == []:
            out_dict[fueltype] = []
        else:
            replaced_with_ID = np.array(replaced_tech_with_ID, dtype=float)
            out_dict[fueltype] = replaced_with_ID

    return out_dict

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

        Q_curr = -1 * ((elasticity * ((P_base - P_curr) / P_base)) * Q_base)  - Q_base)

    """
    pricediff_p = (price_base - price_curr) / price_base

    # New current demand
    current_demand = -1 * ((elasticity * pricediff_p * base_demand) - base_demand)

    return current_demand

def convert_date_to_yearday(year, month, day):
    """Gets the yearday (julian year day) of a year minus one to correct because of python iteration
    TESTED_PYTEST

    Parameters
    ----------
    date_base_year : int
        Year
    date_base_year : int
        Month
    day : int
        Day

    Example
    -------
    5. January 2015 --> Day nr 5 in year --> -1 because of python --> Out: 4
    """
    date_y = date(year, month, day)
    yearday = date_y.timetuple()[7] - 1 #: correct because of python iterations
    return yearday

def add_yearly_external_fuel_data(data, data_ext, dict_to_add_data): #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE
    """This data check what enduses are provided by wrapper
    and then adds the yearls fule data to data"""
    for external_enduse in data_ext['external_enduses']:

        new_fuel_array = np.zeros((len(data['fuel_type_lu']), 1))
        for fueltype in data_ext['external_enduses'][external_enduse]:
            new_fuel_array[fueltype] = data_ext['external_enduses'][external_enduse][fueltype]
        dict_to_add_data[external_enduse] = new_fuel_array
    return data

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
    hdd = days_per_month * (t_base - t_mean)  / (1 - m.exp(-k_hitchens_location_constant * (t_base-t_mean)))

    return hdd


def get_tot_y_hdd_reg(region, t_mean_reg_months):
    """ Calculate total and regional HDD"""

    month_days = {0: 31, 1: 28, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 31, 8: 30, 9: 31, 10: 30, 11: 31}
    hdd_tot = 0

    for month in range(12):

        t_mean_reg = t_mean_reg_months[month]

        days_per_month = month_days[month]
        k_hitchens_location_constant = 0.71
        t_base = 15.5
        t_mean = t_mean_reg

        hdd = hdd_hitchens(days_per_month, k_hitchens_location_constant, t_base, t_mean)
        hdd_tot += hdd

    return hdd_tot

def get_hdd_country(regions, data):

    temp_data = data['temp_mean']
    hdd_country = 0
    hdd_regions = {}

    for region in regions:

        #reclassify region #TODO         # Regional HDD #CREATE DICT WHICH POINT IS IN WHICH REGION
        temperature_region_relocated = 'Midlands' #mf.get_temp_region(region)

        t_mean_reg_months = data['temp_mean'][temperature_region_relocated]
        hdd_reg = get_tot_y_hdd_reg(region, t_mean_reg_months)

        hdd_regions[region] = hdd_reg # get regional temp over year
        hdd_country += hdd_reg # Sum regions
        
    return hdd_country, hdd_regions
