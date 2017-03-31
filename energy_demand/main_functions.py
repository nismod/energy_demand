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

def get_temp_region(dw_reg_id, coordinates):
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
        #print("Write YAML file with length: " + str(len(yaml_list)))
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

        Q_curr = Q_base * (1 - e * ((P_base - P_curr)/ P_base))

    The function prevents demand becoming negative as in extreme cases this
    would otherwise be possibe.
    """
     # New current demand
    current_demand = base_demand * (1 - elasticity * ((price_base - price_curr) / price_base))


    if current_demand < 0:
        # Print Attention: Demand is minus....(elasticity might be unrealistic?)
        #TODO: CHECK IF REALLY POSSIBLE
        print(current_demand)
        return 0
    else:
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

def get_tot_y_hdd_reg(t_mean_reg_months, t_base):
    """Calculate total number of heating degree days in a region

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

def get_hdd_country(regions, data, base_year):
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
    t_base = data['assumptions']['t_base']['base_year']

    for region in regions:

        coordinates_of_region = "TODO"
        #reclassify region #TODO         # Regional HDD #CREATE DICT WHICH POINT IS IN WHICH REGION (e.g. do with closest)
        temperature_region_relocated = get_temp_region(region, coordinates_of_region)
        t_mean_reg_months = data['temp_mean'][temperature_region_relocated]

        hdd_reg = get_tot_y_hdd_reg(t_mean_reg_months, t_base)

        hdd_regions[region] = hdd_reg # get regional temp over year
        hdd_country += hdd_reg # Sum regions

    return hdd_regions

def get_hdd_individ_reg(region, data):
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
    t_base = data['assumptions']['t_base']['base_year'] #t_base of base_year

    hdd_reg = get_tot_y_hdd_reg(t_mean_reg_months, t_base)

    return hdd_reg

def get_t_base(curr_y, assumptions, base_yr, end_yr):
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
        tbd
    """

    # Base temperature of end year minus base temp of base year 
    t_base_diff = assumptions['t_base']['end_yr'] - assumptions['t_base']['base_year']

    # Sigmoid diffusion
    t_base_frac = sigmoid_diffusion(base_yr, curr_y, end_yr, assumptions['sig_midpoint'], assumptions['sig_steeppness'])

    # Temp diff until current year
    t_diff_cy = t_base_diff * t_base_frac

    # Add temp change to base year temp
    t_base_cy = assumptions['t_base']['base_year'] + t_diff_cy

    return t_base_cy

""" Functions for fuel_enduse_switch stock"""
import math as m

'''def eff_sy_lin(base_year, current_yr, year_end, assumptions, technology):
    """ Calculates lineare diffusion
    Parameters
    ----------
    base_year : float
        Base year

    Returns
    -------
    diffusion : float
        Share of fuel switch in simluation year
    """
    eff_by = assumptions['eff_by'][technology]
    eff_ey = assumptions['eff_ey'][technology]
    sim_years = year_end - base_year


    # How far the diffusion is
    diffusion = round(linear_diff(base_year, current_yr, eff_by, eff_ey, sim_years), 2)

    return diffusion
'''

def frac_sy_sigm(base_year, current_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate sigmoid diffusion of a fuel type share of a current year
    Parameters
    ----------
    base_year : float
        Base year
    current_yr : float
        Base year
    year_end : float
        Base year
    assumptions : float
        Base year
    fuel_enduse_switch : float
        Base year
    Returns
    -------
    fract_cy : float
        Share of fuel switch in simluation year
    """
    # Fuel share of total ED in base year
    fract_by = assumptions['fuel_type_p_by'][fuel_enduse_switch]

    # Fuel share af total ED in end year
    fract_ey = assumptions['fuel_type_p_ey'][fuel_enduse_switch]

    sig_midpoint = assumptions['sig_midpoint']
    sig_steeppness = assumptions['sig_steeppness']

    # Difference
    if fract_by > fract_ey:
        diff_frac = -1 * (fract_by - fract_ey) # minus
    else:
        diff_frac = fract_ey -fract_by

    # How far the diffusion has progressed
    p_of_diffusion = round(sigmoid_diffusion(base_year, current_yr, year_end, sig_midpoint, sig_steeppness), 2)

    # Fraction of current year
    fract_cy = fract_by + (diff_frac * p_of_diffusion)

    return fract_cy

def linear_diff(base_year, current_yr, eff_by, eff_ey, sim_years):
    """This function assumes a linear fuel_enduse_switch diffusion.
    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.
    Parameters
    ----------
    current_yr : int
        The year of the current simulation.
    base_year : int
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
    if current_yr == base_year or sim_years == 0:
        fract_sy = eff_by
    else:
        fract_sy = eff_by + ((eff_ey - eff_by) / sim_years) * (current_yr - base_year)

    return fract_sy

def sigmoid_diffusion(base_year, current_yr, year_end, sig_midpoint, sig_steeppness):
    """Calculates a sigmoid diffusion path of a lower to a higher value
    (saturation is assumed at the endyear)

    Parameters
    ----------
    base_year : int
        Base year of simulation period
    current_yr : int
        The year of the current simulation
    year_end : int
        The year a fuel_enduse_switch saturaes
    sig_midpoint : float
        Mid point of sigmoid diffusion function
    sig_steeppness : float
        Steepness of sigmoid diffusion function

    Returns
    -------
    cy_p : float
        The fraction of the fuel_enduse_switch in the current year

    Infos
    -------
        sig_midpoint:    can be used to shift curve to the left or right (standard value: 0) 
        sig_steeppness:    The steepness of the sigmoid curve (standard value: 1) 
    # INFOS

    # What also could be impleneted is a technology specific diffusion (parameters for diffusion)
        year_invention : int
        The year where a fuel_enduse_switch gets on the market

    """
    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    if year_end == base_year:
        y_trans = 6.0
    else:
        y_trans = -6.0 + (12.0 / (year_end - base_year)) * (current_yr - base_year)

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    cy_p = 1 / (1 + m.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

    return cy_p


def wheater_generator(data):
    """ TODO """
    return data

'''def sigmoidfuel_enduse_switchdiffusion(base_year, current_yr, saturate_year, year_invention):
    """This function assumes "S"-Curve fuel_enduse_switch diffusion (logistic function).
    The function reads in the following assumptions about the fuel_enduse_switch to calculate the
    current distribution of the simulated year:
    Parameters
    ----------
    current_yr : int
        The year of the current simulation
    saturate_year : int
        The year a fuel_enduse_switch saturaes
    year_invention : int
        The year where a fuel_enduse_switch gets on the market
    base_year : int
        Base year of simulation period
    Returns
    -------
    val_yr : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    # Check how many years fuel_enduse_switch in the market
    if current_yr < year_invention:
        val_yr = 0
        return val_yr
    else:
        if current_yr >= saturate_year:
            years_availalbe = saturate_year - base_year
        else:
            years_availalbe = current_yr - year_invention

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

'''def frac_sy_sigm_new_fuel_enduse_switch(base_year, current_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate share of a fuel_enduse_switch in a year based on assumptions
        Parameters
        ----------
        base_year : float
            Base year
        current_yr : float
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
    p_of_diffusion = round(sigmoidfuel_enduse_switchdiffusion(base_year, current_yr, saturation_year, market_year), 2)
    print("p_of_diffusion: " + str(p_of_diffusion))
    #fract_cy = p_of_diffusion * max_possible
    return p_of_diffusion
'''
