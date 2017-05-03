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
import copy

from scipy.optimize import curve_fit


# pylint: disable=I0011,C0321,C0301,C0103, C0325

def get_temp_region(dw_reg_name, coordinates):
    """
    #TODO Reallocation any region input with wheater region (mabe also coordinate inputs)

    """
    coordinates = coordinates

    temperature_region_relocated = 'Midlands'

    return temperature_region_relocated

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
    results : dict
        Returns a list for energy supply model with fueltype, region, hour"""

    # Create timesteps for full year (wrapper-timesteps)
    results = {}

    for fueltype_id, fueltype in data['fuel_type_lu'].items():
        results[fueltype] = []

        for reg_name in data['lu_reg']:
            reg = getattr(resid_object_country, str(reg_name))
            region_name = reg.reg_name  # Get object region name
            hourly_all_fuels = reg.tot_all_enduses_h(data)  # Get total fuel

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

    return end_uses_dict


def read_csv_assumptions_technologies(path_to_csv, data):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------

    Notes
    -----
    #TODO: DESCRIBE FORMAT
    """
    list_elements = []

    dict_with_technologies = {}

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row
        
        # Iterate rows
        for row in read_lines:
            technology = row[0]
            dict_with_technologies[technology] = {

                'fuel_type': data['lu_fueltype'][str(row[1])],
                'eff_by': float(row[2]),
                'eff_ey': float(row[3]),
                'eff_achieved': float(row[4]),
                'diff_method': str(row[5]),
                'market_entry': float(row[6])
                
            }

    return dict_with_technologies


def read_csv_assumptions_fuel_switches(path_to_csv, data):
    """This function reads in CSV files and skips header row.

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------

    Notes
    -----
    #TODO: DESCRIBE FORMAT
    """
    list_elements = []
    dict_with_switches = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row
        
        # Iterate rows
        for row in read_lines:
            #enduse = row[0]
            dict_with_switches.append(
                {
                'enduse': str(row[0]),
                'enduse_fueltype_replace': data['lu_fueltype'][str(row[1])],
                'technology_install': str(row[2]),
                'year_fuel_consumption_switched': float(row[3]),
                'share_fuel_consumption_switched': float(row[4]),
                'max_theoretical_switch': float(row[5])
                }
            )

    return dict_with_switches



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
    list_dates = get_datetime_range(start=date(base_yr, 1, 1), end=date(base_yr, 12, 31)) # List with every date in a year

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
        copy_dict[i] = np.array(list(in_dict[i].items()), dtype=float)
    return copy_dict

def convert_to_tech_array(in_dict, tech_lu):
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
    yearday = date_y.timetuple()[7] - 1 #: correct because of python iterations
    return yearday

def add_yearly_external_fuel_data(data, data_ext, dict_to_add_data):
    """This data check what enduses are provided by wrapper
    and then adds the yearls fule data to data

    #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE
    """
    for external_enduse in data_ext['external_enduses_resid']:

        new_fuel_array = np.zeros((len(data['fuel_type_lu']), 1))
        for fueltype in data_ext['external_enduses_resid'][external_enduse]:
            new_fuel_array[fueltype] = data_ext['external_enduses_resid'][external_enduse][fueltype]
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
    hdd_hitchens = days_per_month * (t_base - t_mean)  / (1 - m.exp(-k_hitchens_location_constant * (t_base-t_mean)))

    return hdd_hitchens

def calc_hdd(t_base, temp_every_h_year):
    """Heating Degree Days for every day in a year

    Parameters
    ----------
    t_base : int
        Base temperature
    temp_every_h_year : array
        Array containing daily temperatures for each day (shape 365, 24)

    Returns
    -------
    hdd_d : array
        An array containing the Heating Degree Days for every day (shape 365, 1)
    """
    hdd_d = np.zeros((365, 1))

    for i, day in enumerate(temp_every_h_year):
        hdd = 0
        for h_temp in day:
            diff = t_base - h_temp 
            if diff > 0:
                hdd += t_base - h_temp
        hdd_d[i] = hdd / 24
        
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
    temp_data = data['temp_mean']

    hdd_country = 0
    hdd_regions = {}
    t_base = data['assumptions']['t_base_heating']['base_yr']

    for region in regions:

        coordinates_of_region = "TODO"
        #reclassify region #TODO         # Regional HDD #CREATE DICT WHICH POINT IS IN WHICH REGION (e.g. do with closest)
        temperature_region_relocated = get_temp_region(region, coordinates_of_region)
        t_mean_reg_months = data['temp_mean'][temperature_region_relocated]

        hdd_reg = get_tot_y_hdd_reg(t_mean_reg_months, t_base)

        hdd_regions[region] = hdd_reg # get regional temp over year
        hdd_country += hdd_reg # Sum regions

    return hdd_regions

'''def get_hdd_individ_reg(region, data):
    """Calculate total number of heating degree days in a region for the base year

    Parameters
    ----------
    regions : dict
        Dictionary containing regions
    data : dict
        Dictionary with data
    """
    #reclassify region #TODO         # Regional HDD #CREATE DICT WHICH POINT IS IN WHICH REGION (e.g. do with closest)
    temperature_region_relocated = 'Midlands' #mf.get_temp_region(region)

    t_mean_reg_months = data['temp_mean'][temperature_region_relocated]
    t_base = data['assumptions']['t_base_heating']['base_yr'] #t_base of base_yr

    hdd_reg = get_tot_y_hdd_reg(t_mean_reg_months, t_base)

    return hdd_reg
'''

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


def sigmoid_diffusion_saturation_year_invention_year(base_yr, curr_yr, year_end, sig_midpoint, sig_steeppness, saturation_yr, invention_yr):
    """Saturation level needs to be defined
    Always return 1 if saturated --> but satured may be any share of the technology or fuel enduse"""
    # Year invention can't be before base year --> if technology existist, put invention year as model base year

    if curr_yr < invention_yr or curr_yr == base_yr:
        return 0 #Technology has not been invented, 0 penetration

    if curr_yr >= saturation_yr: #Technology is saturated
        return 1
    else:
        if curr_yr >= saturation_yr: # After saturation
            #years_availalbe = saturation_yr - base_yr # Number of years --> saturation point - base year --> Saturation == 100*
            return 1
        else:
            years_availalbe = curr_yr - invention_yr

            y_trans = -6.0 + (12.0 / (saturation_yr - invention_yr)) * years_availalbe

            # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
            cy_p = 1 / (1 + m.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

            return cy_p

""" Functions for fuel_enduse_switch stock"""

'''def frac_sy_sigm(base_yr, curr_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate sigmoid diffusion of a share in fuels of a current year

    Parameters
    ----------
    base_yr : float
        Base year
    curr_yr : float
        Current year
    year_end : float
        Simulation End year
    assumptions : dictionary
        Assumptions
    fuel_enduse_switch : float
        Base year
    Returns
    -------
    fract_cy : float
        Share of fuel switch in simluation year
    """
    fract_by = assumptions['fuel_type_p_by'][fuel_enduse_switch] # Fuel share of total ED in base year
    fract_ey = assumptions['fuel_type_p_ey'][fuel_enduse_switch] # Fuel share af total ED in end year

    # Difference
    if fract_by > fract_ey:
        diff_frac = -1 * (fract_by - fract_ey) # minus
    else:
        diff_frac = fract_ey -fract_by

    # How far the diffusion has progressed
    p_of_diffusion = round(sigmoid_diffusion(base_yr, curr_yr, year_end, assumptions['sig_midpoint'], assumptions['sig_steeppness']), 2)

    # Fraction of current year
    fract_cy = fract_by + (diff_frac * p_of_diffusion)

    return fract_cy
'''

def linear_diff(base_yr, curr_yr, eff_by, eff_ey, sim_years):
    """This function assumes a linear fuel_enduse_switch diffusion.
    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.
    Parameters
    ----------
    curr_yr : int
        The year of the current simulation.
    base_yr : int
        The year of the current simulation.
    eff_by : float
        Fraction of population served with fuel_enduse_switch in base year
    eff_ey : float
        Fraction of population served with fuel_enduse_switch in end year
    sim_years : str
        Total number of simulated years.
    Returns
    -------
    fract_sy : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    if curr_yr == base_yr or sim_years == 0:
        fract_sy = 0 #return zero
    else:
        fract_sy = ((eff_ey - eff_by) / sim_years) * (curr_yr - base_yr)

    return fract_sy

def sigmoid_diffusion(base_yr, curr_yr, end_yr, sig_midpoint, sig_steeppness):
    """Calculates a sigmoid diffusion path of a lower to a higher value
    (saturation is assumed at the endyear)

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
        The fraction of the fuel_enduse_switch in the current year

    Infos
    -------

    It is always assuemed that for the simulation year the share is 
    replaced with technologies having the efficencis of the current year. For technologies
    which get replaced fast (e.g. lightbulb) this is corret assumption, for longer lsting
    technologies, thie is more problematic (in this case, over every year would need to be iterated
    and calculate share replaced with efficiency of technology in each year).

    # INFOS

    # What also could be impleneted is a technology specific diffusion (parameters for diffusion)
        year_invention : int
        The year where a fuel_enduse_switch gets on the market

    # Always return positive value. Needs to be considered for changes in negative 
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

        # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
        cy_p = 1 / (1 + m.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

        return cy_p

def calc_cdd(t_base_cooling, temperatures):
    """Calculate cooling degree days 

    The Cooling Degree Days are calculated based on
    cooling degree hours with temperatures of a full year

    Parameters
    ----------
    t_base_cooling : float
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
        for h_temp in day:
            diff_t = h_temp - t_base_cooling

            if diff_t > 0: # Only if cooling is necessary
                sum_d +=  diff_t

        cdd_d[day_nr] = sum_d / 24

    return cdd_d


def wheater_generator(data):
    """Load weather data
    
    
    
    """

    # ----------------------------------------------------------
    # Read in temperatures for every year for every region
    # ----------------------------------------------------------

    # Check how the input data of the year 2015 compare to other years? (e.g. with heating days?) Wheater correction?

    return data

def get_heatpump_eff(temp_yr, m_slope, b, t_base):
    """Calculate efficiency according to temperatur difference of base year

    For every hour the temperature difference is calculated and the efficiency of the heat pump calculated
    based on efficiency assumptions
    return (365,24)

    Parameters
    ----------
    temp_yr : array
        Temperatures for every hour in a year (365, 24)
    m_slope : float
        Slope of efficiency of heat pump
    b : float
        Intercept
    t_base : float
        Base temperature for heating

    Return
    ------
    out : array
        Efficiency for every hour in a year

    Info
    -----

    The efficiency of the heat pump is taken from x.x.x TODO:
    """
    out = np.zeros((365, 24))
    for day_nr, day_temp in enumerate(temp_yr):
        for h_nr, h_temp in enumerate(day_temp):
            if t_base < h_temp:
                h_diff = 0
            else:
                if h_temp < 0: #below zero temp
                    h_diff = t_base + abs(h_temp)
                else:
                    h_diff = abs(t_base - h_temp)
            out[day_nr][h_nr] = m_slope * h_diff + b

    return out

def create_efficiency_array(input_eff):
    """Assing a constante efficiency to every hour in a year

    Parameters
    ----------
    input_eff : float
        Efficiency of a technology

    Return
    ------
    out : array
        Array with efficency for every hour in a year (365,24)
    """
    out = np.zeros((365, 24))
    for i in range(365):
        for j in range(24):
            out[i][j] = input_eff
    return out

def heat_pump_efficiency_y():
    """Sum over every hour in a year the efficiency * temp¨"""
    return

def calc_age_distribution(age_distr_by, age_distr_ey):
    """ CAlculate share of age distribution of buildings
    DEMOLISHRN RATE?
    """
    # Calculate difference between base yeare and ey
    # --> Add 
    assumptions['dwtype_age_distr_by'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    assumptions['dwtype_age_distr_ey'] = {'1918': 20.8, '1941': 36.3, '1977.5': 29.5, '1996.5': 8.0, '2002': 5.4}
    return

'''def sigmoidfuel_enduse_switchdiffusion(base_yr, curr_yr, saturate_year, year_invention):
    """This function assumes "S"-Curve fuel_enduse_switch diffusion (logistic function).
    The function reads in the following assumptions about the fuel_enduse_switch to calculate the
    current distribution of the simulated year:
    Parameters
    ----------
    curr_yr : int
        The year of the current simulation
    saturate_year : int
        The year a fuel_enduse_switch saturaes
    year_invention : int
        The year where a fuel_enduse_switch gets on the market
    base_yr : int
        Base year of simulation period
    Returns
    -------
    val_yr : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    # Check how many years fuel_enduse_switch in the market
    if curr_yr < year_invention:
        val_yr = 0
        return val_yr
    else:
        if curr_yr >= saturate_year:
            years_availalbe = saturate_year - base_yr
        else:
            years_availalbe = curr_yr - year_invention

    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    print("years_availalbe: " + str(years_availalbe))
    year_translated = -6 + ((12 / (saturate_year - year_invention)) * years_availalbe)

    # Convert x-value into y value on sigmoid curve reaching from -6 to 6
    sig_midpoint = 0  # Can be used to shift curve to the left or right (standard value: 0)
    sig_steeppness = 1 # The steepness of the sigmoid curve (standard value: 1)

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    val_yr = 1 / (1 + m.exp(-1 * sig_steeppness * (year_translated - sig_midpoint)))

    return val_yr
'''

'''def frac_sy_sigm_new_fuel_enduse_switch(base_yr, curr_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate share of a fuel_enduse_switch in a year based on assumptions
        Parameters
        ----------
        base_yr : float
            Base year
        curr_yr : float
            Base year
        year_end : float
            Base year
        assumptions : float
            Base year
        fuel_enduse_switch : float
            The end use energy demand of a fueltype (e.g. space_heating_gas)
        Out:
    """
    fract_by = assumptions['p_tech_by'][fuel_enduse_switch]
    fract_ey = assumptions['p_tech_ey'][fuel_enduse_switch]
    market_year = assumptions['tech_market_year'][fuel_enduse_switch]
    saturation_year = assumptions['tech_saturation_year'][fuel_enduse_switch]
    # EV: MAX_SHARE POSSIBLE
    #max_possible
    # How far the fuel_enduse_switch has diffused
    p_of_diffusion = round(sigmoidfuel_enduse_switchdiffusion(base_yr, curr_yr, saturation_year, market_year), 2)
    print("p_of_diffusion: " + str(p_of_diffusion))
    #fract_cy = p_of_diffusion * max_possible
    return p_of_diffusion
'''
def initialise_1_level_dict(first_level_data):
    """Initialise a nested dictionary with two levels and insert curly brackets
    """
    init_dict = {}

    # Iterate first level
    for first_level in first_level_data:
        init_dict[first_level] = {}

    return init_dict

def initialise_2_level_dict(first_level_data, second_level_data, crit):
    """Initialise a nested dictionary with two levels and insert curly brackets
    """
    init_dict = {}

    # Iterate first level
    for first_level in first_level_data:
        init_dict[first_level] = {}

        for second_level in second_level_data:
            if crit == 'brackets':
                init_dict[first_level][second_level] = {}
            if crit == 'zero':
                init_dict[first_level][second_level] = 0

    return init_dict

def sum_1_level_dict(two_level_dict):
    """Sum all entries in a two level dict
    """
    tot_sum = 0
    for i in two_level_dict:
        for j in two_level_dict[i]:
            tot_sum += two_level_dict[i][j]

    return tot_sum

def generate_sig_diffusion(data, data_external):
    """ CALCULATE DIFFUSION CURVES
    
    
    """

    # Step 1. Convert fuel to energy service demand per enduse and technology (For whole UK as technology diffusion is assumed to be the same)
    data['assumptions']['service_demand_p'], data['assumptions']['energy_service_p_fueltype'] = calc_service_demand(data['lu_fueltype'], data['resid_enduses'], data['assumptions']['tech_enduse_by'], data['fuel_raw_data_resid_enduses'], data['assumptions']['technologies'])
    print("STEP 1: Service_demands_p:" + str(data['assumptions']['service_demand_p']))
    print("energy_service_p_fueltype: " + str(data['assumptions']['energy_service_p_fueltype']))

    # Step 2: Calculate energy service per enduse and fueltype
    data['assumptions']['service_demands_fueltypes'] = service_demand_fueltype(data['lu_fueltype'], data['assumptions']['service_demand_p'], data['assumptions']['technologies'], data['fuel_raw_data_resid_enduses'])

    # Step 3: Read out all technologies which are switched to
    data['assumptions']['installed_tech_switch'] = get_installed_technologies(data['assumptions']['resid_fuel_switches'])

    # Step 4: Calculate energy service demand after fuel switches per enduse and technology
    service_demands_after_fuelswitch = calc_service_demand_fuel_switched(data['resid_enduses'], data['assumptions']['resid_fuel_switches'], data['assumptions']['service_demands_fueltypes'], data['assumptions']['technologies'], data['assumptions']['service_demand_p'], data['assumptions']['tech_enduse_by'], data['assumptions']['installed_tech_switch'], 'actual_switch')
    print(service_demands_after_fuelswitch)

    # Step 5: Calculate L for every technology for sigmod diffusion
    l_values_sig = calculate_L_for_sigmoid(data['resid_enduses'], data, data['assumptions'])

    # Step 6: Calclulate sigmoid parameters
    data['assumptions']['sigm_parameters_tech'] = calc_technology_sigmoid_curve(data['resid_enduses'], data['assumptions']['technologies'], data_external, data['assumptions']['installed_tech_switch'], l_values_sig, data['assumptions']['service_demand_p'], service_demands_after_fuelswitch, data['assumptions']['resid_fuel_switches'])
    print("sigm_parameters_tech:" + str(data['assumptions']['sigm_parameters_tech']))

    # --Technological split in end_yr  # FOR END YEAR ALWAYS SAME NR OF TECHNOLOGIES AS INITIAL YEAR (TODO: ASSERT IF ALWAYS 100%)
    data['assumptions']['tech_enduse_ey'] = copy.deepcopy(data['assumptions']['tech_enduse_by'])



    return data

def calc_service_demand(fueltypes_lu, enduses, fuel_p_tech_by, fuels, tech_stock_by):
    """Calculate total energy service percentage of each technology and energy service percentage within the fueltype

    This calculation converts fuels into energy services (e.g. heating for fuel into heat demand)
    and then calculated how much an invidual technology contributes in percent to total energy
    service demand.

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.

    Parameters
    ----------
    enduses : list
        All enduses to perform calulations
    fuel_p_tech_by : dict
        Fuel composition of base year for every fueltype for each enduse
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    tech_stock_by : object assumptions['technologies']
        Technology stock of base year (region dependent)

    Return
    ------
    energy_service_p : dict
        Percentage of total energy service per technology for base year
    energy_service_p_fueltype : dict
        Percentage of energy service witin a fueltype for all technologies with this fueltype for base year

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.
    """
    energy_service = initialise_2_level_dict(enduses, fueltypes_lu.values(), 'brackets') # Energy service per technology for base year (e.g. heat demand in joules)
    energy_service_p = initialise_1_level_dict(enduses) # Percentage of total energy service per technology for base year
    energy_service_p_fueltype = initialise_2_level_dict(enduses, fueltypes_lu.values(), 'brackets') # Percentage of energy service for technologies within the fueltypes

    # Iterate enduse
    for enduse in enduses:

        # Iterate fueltype
        for fueltype, fuel_fueltype in enumerate(fuels[enduse]):
            tot_energy_service_fueltype = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech in fuel_p_tech_by[enduse][fueltype]:

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_p_tech_by[enduse][fueltype][tech] * fuel_fueltype[0]

                # Energy service of end use: Fuel of technoloy * efficiency == Service (e.g.heat demand in Joules)
                energy_service_demand_tech = fuel_tech * tech_stock_by[tech]['eff_by']

                energy_service[enduse][fueltype][tech] = energy_service_demand_tech
                tot_energy_service_fueltype += energy_service_demand_tech # Total energy service demand within a fueltype

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]:
                if tot_energy_service_fueltype == 0: # No fuel in this fueltype
                    energy_service_p_fueltype[enduse][fueltype][tech] = 0
                else:
                    energy_demand_tech = fuel_p_tech_by[enduse][fueltype][tech] * fuel_fueltype[0] * tech_stock_by[tech]['eff_by']
                    energy_service_p_fueltype[enduse][fueltype][tech] = (1 / tot_energy_service_fueltype) * energy_demand_tech

        # Calculate percentage of service of all technologies
        total_service = sum_1_level_dict(energy_service[enduse]) #Total service demand

        # Percentage of energy service per technology
        for fueltype in energy_service[enduse]:
            for technology in energy_service[enduse][fueltype]:
                energy_service_p[enduse][technology] = (1 / total_service) * energy_service[enduse][fueltype][technology]

    # Assert
    # --------
    print("TEST ASSERTIONS")
    for enduse in energy_service_p:
        print(energy_service_p[enduse].values())
        sum_p_service = sum(energy_service_p[enduse].values())
        print("Enduse: " + str(sum_p_service))
        #assert sum_p_service == 1.0, "The energy service for all technologies is not 100% (1.0)"

    # Test if within fueltype always 100 energy service
    for enduse in energy_service_p_fueltype:
        for fueltype in energy_service_p_fueltype[enduse]:
            sum_p_service_fueltype = sum(energy_service_p_fueltype[enduse][fueltype].values())
            print("sum_p_service_fueltype: " + str(sum_p_service_fueltype))
            assert sum_p_service_fueltype == 1.0 or sum_p_service_fueltype == 0.0, "The energy service for all technologies within a fueltype is not 100% (1.0)"

    return energy_service_p, energy_service_p_fueltype

def calc_service_demand_REGION(data, fuel_shape_y_h_hdd_boilers_cy, fuel_p_tech_by, fuels, tech_stock_by):
    """Calculate energy service share of each technology based on assumptions about base year fuel shares/ENERGY SERVICE SHARE?

    This calculation converts fuels into energy services (e.g. heating for fuel into heat demand)
    and then calculated how much an invidual technology contributes in percent to total energy
    service demand.

    This is calculated to determine how much the technology has already diffused up
    to the base year to define the first point on the sigmoid technology diffusion curve.

    Parameters
    ----------
    fuel_shape_y_h_hdd_boilers_cy : array
        Fuel share distribtion of heat #TODO NOT ONLY HEAT
    fuel_p_tech_by : dict
        Fuel composition of base year for every fueltype for each enduse
    fuels : array
        Base year fuel demand
    tech_stock_by : object assumptions['technologies']
        Technology stock of base year (region dependent)

    Return
    ------
    energy_service_p : dict
        Percetnage of total energy service per technology for base year

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.
    """
    energy_service = {} # Energy service per technology for base year (e.g. heat demand in joules)

    # Iterate fueltype
    for fueltype, fuel_enduse in enumerate(fuels):
        energy_service[fueltype] = {}

        # Iterate technologies to calculate share of energy service depending on fuel and efficiencies (average efficiency across whole year)
        for tech in fuel_p_tech_by[fueltype]:

            # Technology efficiency
            technology_efficiency = tech_stock_by[tech]['eff_by']
            #print("F: " + str(technology_efficiency))

            # NEW: Create constant efficiency
            technology_efficiency = create_efficiency_array(technology_efficiency)
            #print("FF: " + str(technology_efficiency))

            # Fuel share in ktoe based on defined fuel shares within fueltype
            fuel_of_tech = fuel_p_tech_by[fueltype][tech] * fuel_enduse[0] # share * tot fuel
            #print("G: " + str(fuel_of_tech))

            # NEW
            fuel_of_tech = fuel_shape_y_h_hdd_boilers_cy * fuel_of_tech
            #print("GG: " + str(fuel_of_tech))

            # Energy service of end use: Fuel of technoloy * efficiency == Service (e.g.heat demand in Joulres)
            energy_service[fueltype][tech] = fuel_of_tech * technology_efficiency

    # Calculate service demand over the full year and for every hour
    total_service = 0
    total_service_h = np.zeros((365, 24))

    for fueltype in energy_service:
        for technology in energy_service[fueltype]:
            total_service += np.sum(energy_service[fueltype][technology]) # y
            total_service_h = total_service_h + energy_service[fueltype][technology] # h

    return energy_service, total_service, total_service_h

def service_demand_fueltype(lu_fueltype, service_demand_p, tech_stock, fuels):
    """Calculate energy service per fueltype

    Parameters
    ----------
    service_demand_p : dict
        Service demand per technology
    tech_stock : dict
        Technologies with all attributes
    fuels : dict
        Fuels

    Return
    ------
    energy_service_fueltype : dict
        Percentage of total energy service per fueltype
        (e.g. 0.5 gas, 0.5 electricity)

    Example
    -----


    """
    energy_service_fueltype = initialise_2_level_dict(service_demand_p.keys(), range(len(lu_fueltype)), 'zero') # Energy service per technology for base year (e.g. heat demand in joules)

    # Iterate technologies for each enduse and their percentage of total service demand
    for enduse in service_demand_p:

        # Iterate technologies in enduse
        for technology in service_demand_p[enduse]:

            # Read fuel type of technology
            fueltype_technology = tech_stock[technology]['fuel_type']

            # Add percentage of total enduse to fueltype
            energy_service_fueltype[enduse][fueltype_technology] += service_demand_p[enduse][technology]

    return energy_service_fueltype

def get_installed_technologies(fuel_switches):
    """Read out all technologies which are specifically switched to

    Parameter
    ---------
    fuel_switches : dict
        All fuel switches where a share of a fuel of an enduse is switched to a specific technology

    Return
    ------
    installed_tech : list
        List with all technologies which where a fuel share is switched to
    """
    installed_tech = []
    for switch in fuel_switches:
        if switch['technology_install'] not in installed_tech:
            installed_tech.append(switch['technology_install'])

    return installed_tech

def calc_service_demand_fuel_switched(enduses, fuel_switches, service_demands_fueltypes, tech_stock_by, calc_service_demand, fuel_enduse_tech_p, technologies_in_fuelswitch, switch_type):
    """Calculate energy service demand percentages after fuel switches

    Parameters
    ----------
    enduses : list
        List with enduses where fuel switches are defined
    fuel_switches : dict
        Fuel switches
    service_demands_fueltypes : dict
        Service demand per fueltype
    tech_stock_by : dict
        Technologies
    fuel_tech_p_by : dict
        Technologies in base year
    calc_service_demand : dict
        Percentage of service demand per technology for base year
    tech_fueltype_by : dict
        Technology stock
    fuel_enduse_tech_p : dict
        Fuel shares for each technology of an enduse
    technologies_in_fuelswitch : dict
        Technologies which are installed in fuel switches
    maximum_switch : crit
        Wheater this function is executed with the switched fuel share or the maximum switchable fuel share

    Return
    ------
    service_demand_switched : dict
        Service demand with added and substracted service demand for every technology

    Notes
    -----
    Implement changes in heat demand (all technolgies within a fueltypes are replaced proportionally)
    # Substract percentages and add percentages of service demand
    """
    service_demand_switched = copy.deepcopy(calc_service_demand)

    for enduse in enduses: # Iterate enduse
        for fuel_switch in fuel_switches: # Iterate fuel switches
            if fuel_switch['enduse'] == enduse: # If fuel is switched in this enduse

                # Fuel switch parameters
                installed_tech = fuel_switch['technology_install']
                replaced_fueltype = fuel_switch['enduse_fueltype_replace']

                # Check if installed technology is considered for fuelswitch
                if installed_tech in technologies_in_fuelswitch:

                    # Share of energy service before switch
                    orig_service_p = service_demands_fueltypes[enduse][replaced_fueltype]

                    # Calculate change in energy service demand
                    if switch_type == 'max_switch':
                        change_service_p = orig_service_p * fuel_switch['max_theoretical_switch'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent

                    if switch_type == 'actual_switch':
                        change_service_p = orig_service_p * fuel_switch['share_fuel_consumption_switched'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent

                    # Calculate fraction of energy service which is replaced for a fueltype by iterating all technologies with this fueltype
                    replaced_tech_fueltype = fuel_enduse_tech_p[enduse][replaced_fueltype].keys() # get all technologies which are replaced related to this fueltype

                    # Calculate total energy service in this fueltype
                    tot_service_fueltype_p = 0
                    for tech in replaced_tech_fueltype:
                        tot_service_fueltype_p += calc_service_demand[enduse][tech]

                    # Substract service demand for replaced technologies
                    for tech in replaced_tech_fueltype:
                        relative_service_p = (1 / tot_service_fueltype_p) * calc_service_demand[enduse][tech] # Relative service demand within fueltype
                        service_demand_switched[enduse][tech] -= change_service_p * relative_service_p

                    # Add service demand for installed technologies
                    service_demand_switched[enduse][installed_tech] += change_service_p

    return service_demand_switched

def calculate_L_for_sigmoid(enduses, data, assumptions):
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

    # Initialise
    l_values_sig = initialise_2_level_dict(enduses, assumptions['installed_tech_switch'], 'brackets')

    for enduse in enduses:

        # Iterite list with enduses where fuel switches are defined
        for technology in assumptions['installed_tech_switch']:

            # Calculate service demand
            tech_install_p = calc_service_demand_fuel_switched(
                data['resid_enduses'],
                assumptions['resid_fuel_switches'],
                assumptions['service_demands_fueltypes'], # Service demand for enduses and fueltypes
                assumptions['technologies'],
                assumptions['service_demand_p'], # Percentage of service demands for every technology
                assumptions['tech_enduse_by'],
                [technology],
                'max_switch'
                )

            # Read out L-values with calculating sigmoid diffusion with maximum theoretical replacement
            l_values_sig[enduse][technology] = tech_install_p[enduse][technology]

    return l_values_sig

def calc_technology_sigmoid_curve(enduses, tech_stock_by, data_ext, installed_tech, L_values, base_year_service_demand, set_service_demand, fuel_switches):
    """Based on energy service demand in base year and projected future energy service demand because of fuel switched the a sigmoid difufsion curve is fitted
    
    Parameters
    ----------
    enduses : enduses
        enduses
    tech_stock_by : dict
        Technologies of base year
    data_ext : dict
        External data_ext
    installed_tech : dict
        List with installed technologies in fuel switches
    L_values : dict
        L values for maximum possible diffusion of technologies
    base_year_service_demand : dict
        Energy service demand for base year (1.sigmoid point)
    fuel_switches : dict
        Fuel switch information

    Returns
    -------
    sigmoid_parameters : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)

    Notes
    -----
    # IDENTIAL FUEL SWITCH YEAR
    in a given year sigmoid
    diffusion curve is generated

    """
    sigmoid_parameters = initialise_2_level_dict(enduses, installed_tech, 'brackets')

    for enduse in enduses:

        # Year until swictheds (must be identical for all switches) (read out from frist switch)
        # #TODO
        for switch in fuel_switches:
            if switch['enduse'] == enduse:
                year_until_switched = switch['year_fuel_consumption_switched']
                break

        for technology in installed_tech:

            # Test wheter technology has the market entry before or after base year. If wafterwards --> set very small number in market entry year
            if tech_stock_by[technology]['market_entry'] > data_ext['glob_var']['base_yr']:
                point_x_by = tech_stock_by[technology]['market_entry']
                point_y_by = 0.001 # if market entry in a future year
            else: # If market entry before, set to 2015
                point_x_by = data_ext['glob_var']['base_yr']
                point_y_by = base_year_service_demand[enduse][technology]

                if point_y_by == 0:
                    point_y_by = 0.001 #IF the base year is the market entry year use a very small number (as otherwise the fit does not work)

            # If point_y_by is 0 --> insert very small number
            point_x_projected = year_until_switched
            point_y_projected = set_service_demand[enduse][technology]

            xdata = np.array([point_x_by, point_x_projected])
            ydata = np.array([point_y_by, point_y_projected])
            #print("xdata: " + str(xdata))
            #print("ydata: " + str(ydata))

            # Start paramters for fitting
            start_parameters = [data_ext['glob_var']['base_yr'] + 0.5 * (data_ext['glob_var']['end_yr'] - data_ext['glob_var']['base_yr']), 1]

            # Fit sigmoid diffusion curve based on assumptions until when technologies are replaced
            fit_parameter = fit_sigmoid_diffusion(L_values[enduse][technology], xdata, ydata, start_parameters)
            '''
            try:
                possible_start_parameters = [0.001, 0.01, 0.1, 1, 2, 3, 4, 5, 10]
                for parameter_steepness in possible_start_parameters:
                    start_parameters = [year_middle_simulation_period, parameter_steepness]

                    fit_parameter = fit_sigmoid_diffusion(L_values[enduse][technology], xdata, ydata, start_parameters)
                    print("fit_parameter: " + str(fit_parameter))

                    if len(fit_parameter) == 2:
                        break #fit was succesful
            except:
                print("COULD NO DO THE FIT")
            '''
            # Insert parameters
            sigmoid_parameters[enduse][technology]['midpoint'] = fit_parameter[0] #midpoint (x0)
            sigmoid_parameters[enduse][technology]['steepness'] = fit_parameter[1] #Steepnes (k)
            sigmoid_parameters[enduse][technology]['l_parameter'] = L_values[enduse][technology]

            #plot
            #plotout_sigmoid_tech_diff(data_ext, L_values, technology, enduse, xdata, ydata, fit_parameter, market_entry)

    return sigmoid_parameters

def sigmoid_function(x, L, midpoint, steepness):
    """
    """
    y = L / (1 + np.exp(-steepness * (x - midpoint)))
    return y

def plotout_sigmoid_tech_diff(data_ext, L_values, technology, enduse, xdata, ydata, fit_parameter, market_entry):
    """
    """
    import pylab
    import matplotlib.pyplot as plt

    L = L_values[enduse][technology]

    def sigmoid(x, x0, k):
        y = L/ (1 + np.exp(-k*(x-x0)))
        return y

    x = np.linspace(2000, 2100, 100)
    y = sigmoid(x, *fit_parameter)

    fig = plt.figure()
    fig.set_size_inches(12, 8)
    pylab.plot(xdata, ydata, 'o', label='data')
    pylab.plot(x, y, label='fit')
    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')
    pylab.show()

def fit_sigmoid_diffusion(L, xdata, ydata, start_parameters):
    """Fit sigmoid curve based on two points on the diffusion curve

    Parameters
    ----------
    L : float
        The sigmoids curve maximum value (max consumption )
    """
    def sigmoid(x, x0, k):
        y = L/ (1 + np.exp(-k*(x-x0)))
        return y

    popt, pcov = curve_fit(sigmoid, xdata, ydata, p0=start_parameters)

    '''x = np.linspace(2000, 2100, 50)
    y = sigmoid(x, *popt)

    fig = plt.figure()
    fig.set_size_inches(12,8)
    pylab.plot(xdata, ydata, 'o', label='data')
    pylab.plot(x,y, label='fit')
    pylab.ylim(0, 1.05)
    pylab.legend(loc='best')
    pylab.show()
    '''

    return popt









def get_fuel_fract_wihin_fueltpe(tech_enduse_fueltype, technologies):
    """ Calculate share fractioon within fueltype
    
    tech_enduse: Shares of fuel for enduse per fueltype

    #TODO: Beispiel
    e.g.: 0.5 fuel tech A & 0.5 fuel tech A 
    eff_A: 0.7
    eff_B: 0.2
    --> Fuel out tech A: (1 / (0.5/0.7 + 0.5/0.2)) * 0.5/0.7 
    """
    out_fuel_share_technologies = {}

    # Factor over all technologies
    overall_tech_share = 0
    for tech in tech_enduse_fueltype:
        overall_tech_share += tech_enduse_fueltype[tech] / technologies[tech]['eff_by']
    print("overall_tech_share: " + str(overall_tech_share))
    print(tech_enduse_fueltype)

    if overall_tech_share == 0:
        for tech in tech_enduse_fueltype:
            out_fuel_share_technologies[tech] = 0
    else:
        # Calculate fuel share for technology
        for tech in tech_enduse_fueltype: # Calculate fuel within tech in fueltype

            # Calculate share per fueltype
            share_tech_fueltype = (1.0 / overall_tech_share) * tech_enduse_fueltype[tech] / technologies[tech]['eff_by']

            out_fuel_share_technologies[tech] = share_tech_fueltype
        #print("SHARE: " + str(out_fuel_share_technologies))
    return out_fuel_share_technologies
