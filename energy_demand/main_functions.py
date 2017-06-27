"""This file stores all functions of main.py"""
import os
import sys
import csv
#import re
from datetime import date
from datetime import timedelta as td
import math as m
import copy
#import pprint
import numpy as np
import yaml
import pylab
import matplotlib.pyplot as plt
from haversine import haversine # PAckage to calculate distance between two long/lat points
from scipy.optimize import curve_fit
import unittest
ASSERTIONS = unittest.TestCase('__init__')

# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

def add_yearly_external_fuel_data(data, dict_to_add_data):
    """This data check what enduses are provided by wrapper
    and then adds the yearls fule data to data

    #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE
    """
    for external_enduse in data['external_enduses_resid']:
        new_fuel_array = np.zeros((data['nr_of_fueltypes']))
        for fueltype in data['external_enduses_resid'][external_enduse]:
            new_fuel_array[fueltype] = data['external_enduses_resid'][external_enduse][fueltype]
        dict_to_add_data[external_enduse] = new_fuel_array

    return data

def convert_out_format_es(data, object_country, enduses):
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

    for fueltype, fueltype_id in data['lu_fueltype'].items():
        results[fueltype] = []

        for reg_name in data['lu_reg']:
            reg = getattr(object_country, reg_name)
            region_name = reg.reg_name
            hourly_all_fuels = reg.tot_all_enduses_h(data, enduses, 'enduse_fuel_yh')

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
    service_switches = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            service_switches.append(row)

    return np.array(service_switches, float) # Convert list into array

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
    service_switches = []
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            service_switches.append(row)

    return np.array(service_switches) # Convert list into array

def read_csv_base_data_service(path_to_csv, nr_of_fueltypes):
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
    """
    try:
        lines = []
        end_uses_dict = {}

        with open(path_to_csv, 'r') as csvfile:
            read_lines = csv.reader(csvfile, delimiter=',')
            _headings = next(read_lines) # Skip first row
            _secondLine = next(read_lines) # Skip first row

            # All sectors
            all_sectors = set([])
            for sector in _secondLine[1:]: #skip fuel ID:
                #if sector not in all_sectors:
                all_sectors.add(sector)

            # All enduses
            all_enduses = set([])
            for enduse in _headings[1:]: #skip fuel ID:
                #if enduse not in all_enduses:
                all_enduses.add(enduse)

            # Initialise dict
            for sector in all_sectors:
                end_uses_dict[sector] = {}
                for enduse in all_enduses:
                    end_uses_dict[sector][enduse] = np.zeros((nr_of_fueltypes)) #{}

            # Iterate rows
            for row in read_lines:
                lines.append(row)

            for cnt_fueltype, row in enumerate(lines):
                cnt = 1 #skip first
                for entry in row[1:]:
                    enduse = _headings[cnt]
                    sector = _secondLine[cnt]
                    end_uses_dict[sector][enduse][cnt_fueltype] += float(entry)
                    cnt += 1

        return end_uses_dict, list(all_sectors), list(all_enduses)

    except (KeyError, ValueError):
        sys.exit("Error in loading fuel data. Check wheter there are any empty cells in the csv files (instead of 0) for enduse '{}".format(end_use))

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
    """
    try:
        lines = []
        end_uses_dict = {}

        with open(path_to_csv, 'r') as csvfile:
            read_lines = csv.reader(csvfile, delimiter=',')
            _headings = next(read_lines) # Skip first row

            # Iterate rows
            for row in read_lines:
                lines.append(row)

            for i in _headings[1:]: # skip first
                end_uses_dict[i] = np.zeros((len(lines)))

            for cnt_fueltype, row in enumerate(lines):
                cnt = 1 #skip first
                for i in row[1:]:
                    end_use = _headings[cnt]
                    end_uses_dict[end_use][cnt_fueltype] = i
                    cnt += 1
    except (KeyError, ValueError):
        sys.exit("Error in loading fuel data. Check wheter there are any empty cells in the csv files (instead of 0) for enduse '{}".format(end_use))

    # Create list with all rs enduses
    rs_all_enduses = []
    for enduse in end_uses_dict:
        rs_all_enduses.append(enduse)

    return end_uses_dict, rs_all_enduses

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
            print("TechnologyL " + str(technology))
            # Because for hybrid technologies, none needs to be defined
            if row[1] == 'hybrid':
                fueltype = 'None'
            else:
                fueltype = data['lu_fueltype'][str(row[1])]

            dict_technologies[technology] = {
                'fuel_type': fueltype,
                'eff_by': float(row[2]),
                'eff_ey': float(row[3]),
                'eff_achieved': float(row[4]),
                'diff_method': str(row[5]),
                'market_entry': float(row[6])
            }
    #If this function does not work, check if in excel empty rows are loaded in
    return dict_technologies

def read_csv_assumptions_fuel_switches(path_to_csv, data):
    """This function reads in from CSV file defined fuel switch assumptions

    Parameters
    ----------
    path_to_csv : str
        Path to csv file

    Returns
    -------
    dict_with_switches : dict
        All assumptions about fuel switches provided as input
    """
    service_switches = []

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',') # Read line
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            try:
                service_switches.append(
                    {
                        'enduse': str(row[0]),
                        'enduse_fueltype_replace': data['lu_fueltype'][str(row[1])],
                        'technology_install': str(row[2]),
                        'year_fuel_consumption_switched': float(row[3]),
                        'share_fuel_consumption_switched': float(row[4]),
                        'max_theoretical_switch': float(row[5])
                    }
                )
            except (KeyError, ValueError):
                sys.exit("Error in loading fuel switch: Check if provided data is complete (no emptly csv entries)")

    # -------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for element in service_switches:
        if element['share_fuel_consumption_switched'] > element['max_theoretical_switch']:
            sys.exit("Error while loading fuel switch assumptions: More fuel is switched than theorically possible for enduse '{}' and fueltype '{}".format(element['enduse'], element['enduse_fueltype_replace']))

        if element['share_fuel_consumption_switched'] == 0:
            sys.exit("Error: The share of switched fuel needs to be bigger than than 0 (otherwise delete as this is the standard input)")

    # Test if more than 100% per fueltype is switched
    for element in service_switches:
        enduse = element['enduse']
        fuel_type = element['enduse_fueltype_replace']

        tot_share_fueltype_switched = 0
        # Do check for every entry
        for element_iter in service_switches:

            if enduse == element_iter['enduse'] and fuel_type == element_iter['enduse_fueltype_replace']:
                # Found same fueltypes which is switched
                tot_share_fueltype_switched += element_iter['share_fuel_consumption_switched']

        if tot_share_fueltype_switched > 1.0:
            print("SHARE: " + str(tot_share_fueltype_switched))
            sys.exit("ERROR: The defined fuel switches are larger than 1.0 for enduse {} and fueltype {}".format(enduse, fuel_type))

    # Test whether defined enduse exist
    for element in service_switches:
        if element['enduse'] in data['ss_all_enduses'] or element['enduse'] in data['rs_all_enduses']:
            _ = 0
            #print("allgood")
        else:
            print("enduses")
            print(data['ss_all_enduses'])
            print("  ")
            print(data['rs_all_enduses'])
            sys.exit("ERROR: The defined enduse '{}' to switch fuel from is not defined...".format(element['enduse']))

    return service_switches

def read_csv_assumptions_service_switch(path_to_csv, assumptions):
    """This function reads in service assumptions from csv file

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
    rs_enduse_tech_maxL_by_p : dict
        Maximum service per technology which can be switched
    service_switches : dict
        Service switches
    #rs_service_switch_enduse_crit : dict
    #    Criteria whether service switches are defined in an enduse. If no assumptions about service switches, return empty dicts

    Notes
    -----
    The base year service shares are generated from technology stock definition
    - skips header row
    - It also test if plausible inputs
    While not only loading in all rows, this function as well tests if inputs are plausible (e.g. sum up to 100%)
    """
    service_switches = []
    enduse_tech_by_p = {}
    rs_enduse_tech_maxL_by_p = {}
    rs_service_switch_enduse_crit = {} #Store to list enduse specific switchcriteria (true or false)

    # Read CSV file
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            print(row)
            try:
                service_switches.append(
                    {
                        'enduse': str(row[0]),
                        'tech': str(row[1]),
                        'service_share_ey': float(row[2]),
                        'tech_assum_max_share': float(row[3])
                    }
                )
            except (KeyError, ValueError):
                sys.exit("Error in loading service switch: Check if provided data is complete (no emptly csv entries)")

    # Group all entries according to enduse
    all_enduses = []
    for line in service_switches:
        enduse = line['enduse']
        if enduse not in all_enduses:
            all_enduses.append(enduse)
            enduse_tech_by_p[enduse] = {}
            rs_enduse_tech_maxL_by_p[enduse] = {}

    # Iterate all endusese and assign all lines
    for enduse in all_enduses:
        #rs_service_switch_enduse_crit[enduse] = False #False by default
        for line in service_switches:
            if line['enduse'] == enduse:
                tech = line['tech']
                enduse_tech_by_p[enduse][tech] = line['service_share_ey']
                rs_enduse_tech_maxL_by_p[enduse][tech] = line['tech_assum_max_share']
                #rs_service_switch_enduse_crit[enduse] = True

    # ------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for enduse in assumptions['all_specified_tech_enduse_by']:
        if enduse in rs_service_switch_enduse_crit: #If switch is defined for this enduse
            for tech in assumptions['all_specified_tech_enduse_by'][enduse]:
                if tech not in enduse_tech_by_p[enduse]:
                    sys.exit("Error XY: No end year service share is defined for technology '{}' for the enduse '{}' ".format(tech, enduse))

    # Test if more service is provided as input than possible to maximum switch
    for entry in service_switches:
        if entry['service_share_ey'] > entry['tech_assum_max_share']:
            sys.exit("Error: More service switch is provided for tech '{}' in enduse '{}' than max possible".format(entry['enduse'], entry['tech']))

    # Test if service of all provided technologies sums up to 100% in the end year
    for enduse in enduse_tech_by_p:
        if round(sum(enduse_tech_by_p[enduse].values()), 2) != 1.0:
            sys.exit("Error while loading future services assumptions: The provided ey service switch of enduse '{}' does not sum up to 1.0 (100%) ({})".format(enduse, enduse_tech_by_p[enduse].values()))

    return enduse_tech_by_p, rs_enduse_tech_maxL_by_p, service_switches #rs_service_switch_enduse_crit

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
    for day in range(span.days + 1):
        list_dates.append(start + td(days=day))

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

    for fueltype in data['lu_fueltype'].values():

        # Path to create csv file
        path = os.path.join(main_path, 'model_output/_fueltype_{}_hourly_results.csv'.format(fueltype))

        with open(path, 'w', newline='') as fp:
            csv_writer = csv.writer(fp, delimiter=',')
            data = []
            yaml_list_fuel_type = []

            # Iterate fueltypes
            for reg in result_dict[fueltype]:

                for reg, hour, obs_value, _ in result_dict[fueltype]:
                    start_id = "P{}H".format(hour)
                    end_id = "P{}H".format(hour + 1)
                    data.append((lu_reg[reg], start_id, end_id, obs_value))
                    yaml_list_fuel_type.append({'region':  lu_reg[reg], 'start': start_id, 'end': end_id, 'value': float(obs_value), 'units': 'CHECK GWH', 'year': 'XXXX'})

            csv_writer.writerows(data)

            # Write YAML
            write_YAML(crit_YAML, os.path.join(main_path, 'model_output/YAML_  ----TIMESTEPS_{}.yml'.format(fueltype)), yaml_list_fuel_type)

def write_out_txt(path_to_txt, enduses_service):
    """Generate a txt file with base year service for each technology according to provided fuel split input
    """
    file = open(path_to_txt, "w")

    file.write("---------------------------------------------------------------" + '\n')
    file.write("Base year energy service (as share of total per enduse)" + '\n')
    file.write("---------------------------------------------------------------" + '\n')

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
    hdd_d = np.zeros((365))

    for day, temp_day in enumerate(temp_yh):
        hdd = 0
        for temp_h in temp_day:
            diff = t_base - temp_h
            if diff > 0:
                hdd += diff
        hdd_d[day] = np.divide(hdd, 24.0)

    return hdd_d

def get_hdd_country(regions, data, t_base_type):
    """Calculate total number of heating degree days in a region for the base year

    Parameters
    ----------
    regions : dict
        Dictionary containing regions
    data : dict
        Dictionary with data
    """
    hdd_regions = {}

    for region in regions:
        longitude = data['region_coordinates'][region]['longitude']
        latitude = data['region_coordinates'][region]['latitude']

        # Get closest weather station and temperatures
        closest_weatherstation_id = get_closest_weather_station(longitude, latitude, data['weather_stations'])

        # Temp data
        temperatures = data['temperature_data'][closest_weatherstation_id][data['base_yr']]

        # Base temperature for base year
        t_base_heating_cy = t_base_sigm(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], t_base_type)

        # Calc HDD
        hdd_reg = calc_hdd(t_base_heating_cy, temperatures)
        hdd_regions[region] = np.sum(hdd_reg) # get regional temp over year

    return hdd_regions

def t_base_sigm(curr_y, assumptions, base_yr, end_yr, t_base_type):
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
    t_base_diff = assumptions[t_base_type]['end_yr'] - assumptions[t_base_type]['base_yr']

    # Sigmoid diffusion
    t_base_frac = sigmoid_diffusion(base_yr, curr_y, end_yr, assumptions['sig_midpoint'], assumptions['sig_steeppness'])

    # Temp diff until current year
    t_diff_cy = t_base_diff * t_base_frac

    # Add temp change to base year temp
    t_base_cy = t_diff_cy + assumptions[t_base_type]['base_yr']

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

def calc_cdd(rs_t_base_cooling, temperatures):
    """Calculate cooling degree days

    The Cooling Degree Days are calculated based on
    cooling degree hours with temperatures of a full year

    Parameters
    ----------
    rs_t_base_cooling : float
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
    cdd_d = np.zeros((365))

    for day_nr, day in enumerate(temperatures):
        sum_d = 0
        for temp_h in day:
            diff_t = temp_h - rs_t_base_cooling
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
        for current_year in data['sim_period']:
            temp_data_climate_change[weather_station_id][current_year] = np.zeros((365, 24)) # Initialise

            # Iterate every month and substract
            for yearday in range(365):

                # Create datetime object
                date_object = convert_yearday_to_date(data['base_yr'], yearday)

                # Get month of yearday
                month_yearday = date_object.timetuple().tm_mon - 1

                # Get linear diffusion of current year
                temp_by = 0
                temp_ey = data['assumptions']['climate_change_temp_diff_month'][month_yearday]

                lin_diff_current_year = linear_diff(
                    data['base_yr'],
                    current_year,
                    temp_by,
                    temp_ey,
                    len(data['sim_period'])
                )

                # Iterate hours of base year
                for h, temp_old in enumerate(data['temperature_data'][weather_station_id][yearday]):
                    temp_data_climate_change[weather_station_id][current_year][yearday][h] = temp_old + lin_diff_current_year

    return temp_data_climate_change

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

def generate_sig_diffusion(data, service_switches, fuel_switches, enduse_sector, fuels_enduse, tech_increased_service, share_service_tech_ey_p, enduse_tech_maxL_by_p, service_fueltype_by_p, service_tech_by_p, fuel_enduse_tech_p_by):
    """Calculates parameters for sigmoid diffusion of technologies which are switched to/installed.

    Parameters
    ----------
    data : dict
        Data

    Return
    ------
    data : dict
        Data dictionary containing all calculated parameters in assumptions

    Info
    ----
    It is assumed that the technology diffusion is the same over all the uk (no regional different diffusion)
    """
    installed_tech = {}
    sigm_parameters_tech = {}

    #1. test if switc
    for enduse in enduse_sector:

        enduses_with_fuels = fuels_enduse.keys() # All endueses with provided fuels

        # Test is Service Switch is implemented
        if len(service_switches) > 0:
            service_switch_crit = True
        else:
            service_switch_crit = False
        print("SERVICE SWITHC IS IMPEMENTED OR NOT: " + str(service_switch_crit))

        '''
        if True in data['assumptions']['rs_service_switch_enduse_crit'].values(): # If a switch is defined for an enduse
            service_switch_crit = True
        else:
            service_switch_crit = False
        '''

        if service_switch_crit:
            # ---------------------------------------------
            # Sigmoid calculation in case of 'service switch'
            # ---------------------------------------------

            # Tech with lager service shares in end year
            installed_tech[enduse] = tech_increased_service


            # End year service shares (scenaric input)
            service_tech_switched_p = share_service_tech_ey_p

            # Maximum shares of each technology
            l_values_sig = enduse_tech_maxL_by_p

        else:
            # ---------------------------------------------
            # Sigmoid calculation in case of 'fuel switch'
            # ---------------------------------------------
            # Tech with lager service shares in end year (installed in fuel switch)
            installed_tech[enduse] = get_tech_installed(fuel_switches)


            # Calculate energy service demand after fuel switches to future year for each technology
            service_tech_switched_p = calc_service_fuel_switched(
                enduses_with_fuels,
                fuel_switches,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_enduse_tech_p_by,
                installed_tech[enduse],
                'actual_switch'
            )

            # Calculate L for every technology for sigmod diffusion
            l_values_sig = tech_L_sigmoid(
                enduses_with_fuels,
                fuel_switches,
                enduse_sector,
                installed_tech,
                service_fueltype_by_p,
                service_tech_by_p,
                fuel_enduse_tech_p_by
                )

        # -------------------------------------------------------------
        # Calclulate sigmoid parameters for every installed technology
        # -------------------------------------------------------------
        sigm_parameters_tech[enduse] = tech_sigmoid_parameters(
            service_switch_crit,
            installed_tech[enduse],
            enduses_with_fuels,
            data,
            l_values_sig,
            service_tech_by_p,
            service_tech_switched_p,
            fuel_switches
        )

    return installed_tech, sigm_parameters_tech

def calc_service_fueltype_tech(assumptions, fueltypes_lu, fuel_p_tech_by, fuels, tech_stock):
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
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    tech_stock : object
        Technology stock of base year (region dependent)

    Return
    ------
    service_tech_by_p : dict
        Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p : dict
        Percentage of energy service witin a fueltype for all technologies with this fueltype for base year
    service_fueltype_by_p : dict
        Percentage of energy service per fueltype

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region.
    Therfore a constant technology efficiency of the full year needs to be assumed for all technologies.

    Because regional efficiencies may differ within regions, the fuel distribution within
    the fueltypes may also differ
    """
    service = init_nested_dict(fuels, fueltypes_lu.values(), 'brackets') # Energy service per technology for base year (e.g. heat demand in joules)
    service_tech_by_p = init_dict(fuels, 'brackets') # Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p = init_nested_dict(fuels, fueltypes_lu.values(), 'brackets') # Percentage of service per technologies within the fueltypes
    service_fueltype_by_p = init_nested_dict(service_tech_by_p.keys(), range(len(fueltypes_lu)), 'zero') # Percentage of service per fueltype

    for enduse in fuels:
        for fueltype_input_data, fuel_fueltype in enumerate(fuels[enduse]):
            tot_service_fueltype = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype_input_data].items():
                #print("------------Tech: " + str(tech))

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype

                # --------------------------------------------------------------
                # Get efficiency depending whether hybrid or regular technology or heat pumps for base year #TODO: WRITE AS SEPARATE FUNCTION
                # --------------------------------------------------------------
                if tech in assumptions['list_tech_heating_hybrid']:
                    eff_tech = assumptions['technologies']['hybrid_tech']['hybrid_gas_elec']['average_efficiency_national_by']
                elif tech in assumptions['list_tech_heating_temp_dep']:
                    average_h_diff_by = 10
                    eff_tech = eff_heat_pump(
                        m_slope=assumptions['hp_slope_assumpt'],
                        h_diff=average_h_diff_by,
                        b=tech_stock[tech]['eff_by']
                    )
                else:
                    eff_tech = tech_stock[tech]['eff_by']

                # Energy service of end use: Fuel of technoloy * efficiency == Service (e.g.heat demand in Joules)
                service_fueltype_tech = fuel_tech * eff_tech

                # Add energy service demand
                service[enduse][fueltype_input_data][tech] = service_fueltype_tech

                # Total energy service demand within a fueltype
                tot_service_fueltype += service_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype_input_data]:
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_by_p[enduse][fueltype_input_data][tech] = 0
                    service_fueltype_by_p[enduse][fueltype_input_data] += 0
                else:
                    service_fueltype_tech_by_p[enduse][fueltype_input_data][tech] = np.divide(1, tot_service_fueltype) * service[enduse][fueltype_input_data][tech]
                    service_fueltype_by_p[enduse][fueltype_input_data] += service[enduse][fueltype_input_data][tech]

        # Calculate percentage of service of all technologies
        total_service = sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        #_a = 0
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():
                service_tech_by_p[enduse][technology] = np.divide(1, total_service) * service_tech
                #print("Technology_enduse: " + str(technology) + str("  ") + str(service_tech))
                #_a += service_tech

        #print("Total Service base year for enduse {}  :  {}".format(enduse, _a))

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:
            service_fueltype_by_p[enduse][fueltype] = np.divide(1, total_service) * service_fueltype_by_p[enduse][fueltype]
    print("FINISHED")
    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    '''
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p

def calc_service_fuel_switched(enduses, fuel_switches, service_fueltype_p, service_tech_by_p, fuel_enduse_tech_p_by, installed_tech_switches, switch_type):
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
    service_tech_by_p : dict
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
    service_tech_switched_p = copy.deepcopy(service_tech_by_p)

    for enduse in enduses:
        for fuel_switch in fuel_switches:
            if fuel_switch['enduse'] == enduse: # If fuel is switched in this enduse
                tech_install = fuel_switch['technology_install']
                fueltype_tech_replace = fuel_switch['enduse_fueltype_replace']

                # Check if installed technology is considered for fuelswitch
                if tech_install in installed_tech_switches[enduse]:

                    # Share of energy service before switch
                    orig_service_p = service_fueltype_p[enduse][fueltype_tech_replace]

                    # Service demand per fueltype that will be switched
                    if switch_type == 'max_switch':
                        change_service_fueltype_p = orig_service_p * fuel_switch['max_theoretical_switch'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent
                    elif switch_type == 'actual_switch':
                        change_service_fueltype_p = orig_service_p * fuel_switch['share_fuel_consumption_switched'] # e.g. 10% of service is gas ---> if we replace 50% --> minus 5 percent

                    # ---SERVICE DEMAND ADDITION
                    service_tech_switched_p[enduse][tech_install] += change_service_fueltype_p

                    # Get all technologies which are replaced related to this fueltype
                    replaced_tech_fueltype = fuel_enduse_tech_p_by[enduse][fueltype_tech_replace].keys()

                    # Calculate total energy service in this fueltype, Substract service demand for replaced technologies
                    for tech in replaced_tech_fueltype:
                        service_tech_switched_p[enduse][tech] -= change_service_fueltype_p * service_tech_by_p[enduse][tech]

    return service_tech_switched_p

def calc_service_fueltype(lu_fueltype, service_tech_by_p, technologies_assumptions):
    """Calculate service per fueltype in percentage of total service

    Parameters
    ----------
    service_tech_by_p : dict
        Service demand per technology
    technologies_assumptions : dict
        Technologies with all attributes

    Return
    ------
    energy_service_fueltype : dict
        Percentage of total (iterate over all technologis with this fueltype) service per fueltype

    Example
    -----
    (e.g. 0.5 gas, 0.5 electricity)

    """
    service_fueltype = init_nested_dict(service_tech_by_p.keys(), range(len(lu_fueltype)), 'zero') # Energy service per technology for base year (e.g. heat demand in joules)

    # Iterate technologies for each enduse and their percentage of total service demand
    for enduse in service_tech_by_p:
        for technology in service_tech_by_p[enduse]:

            # Add percentage of total enduse to fueltype
            fueltype = technologies_assumptions[technology]['fuel_type']
            service_fueltype[enduse][fueltype] += service_tech_by_p[enduse][technology]

            # TODO:  Add dependingon fueltype HYBRID --> If hybrid, get base year assumption split--> Assumption how much service for each fueltype
            ##fueltypes_tech = technology]['fuel_type']

            #service_fueltype[enduse][fueltype]

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
        installed_tech[switch['enduse']] = set([])

    for switch in fuel_switches:
        enduse_fuelswitch = switch['enduse']
        installed_tech[enduse_fuelswitch].add(switch['technology_install'])

    # Convert set to lists
    for enduse in installed_tech:
        installed_tech[enduse] = list(installed_tech[enduse])

    return installed_tech

def tech_L_sigmoid(enduses, fuel_switches, all_enduses, installed_tech, service_fueltype_p, service_tech_by_p, fuel_enduse_tech_p_by):
    """Calculate L value for every installed technology with maximum theoretical replacement value

    Parameters
    ----------
    enduses : list
        List with enduses where fuel switches are defined
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
        if enduse not in installed_tech:
            print("No technologies to calculate sigmoid")
        else:

            # Iterite list with enduses where fuel switches are defined
            for technology in installed_tech[enduse]:

                # Calculate service demand for specific tech
                tech_install_p = calc_service_fuel_switched(
                    all_enduses,
                    fuel_switches,
                    service_fueltype_p,
                    service_tech_by_p, # Percentage of service demands for every technology
                    fuel_enduse_tech_p_by,
                    {str(enduse): [technology]},
                    'max_switch'
                    )

                # Read out L-values with calculating sigmoid diffusion with maximum theoretical replacement
                l_values_sig[enduse][technology] = tech_install_p[enduse][technology]

    return l_values_sig

def tech_sigmoid_parameters(service_switch_crit, installed_tech, enduses, data, L_values, service_tech_by_p, service_tech_switched_p, rs_fuel_switches):
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
    data : dict
        data
    installed_tech : dict
        List with installed technologies in fuel switches
    L_values : dict
        L values for maximum possible diffusion of technologies
    service_tech_by_p : dict
        Energy service demand for base year (1.sigmoid point)
    service_tech_switched_p : dict
        Service demand after fuelswitch
    rs_fuel_switches : dict
        Fuel switch information

    Returns
    -------
    sigmoid_parameters : dict
        Sigmoid diffusion parameters to read energy service demand percentage (not fuel!)

    Notes
    -----
    NTH: improve fitting

    Manually the fitting parameters can be defined which are not considered as a good fit: fit_crit_A, fit_crit_B
    If service definition, the year until switched is the end model year

    """
    sigmoid_parameters = init_nested_dict(enduses, installed_tech, 'brackets')

    #-----------------
    # Fitting criteria where the calculated sigmoid slope and midpoint can be provided limits
    #-----------------
    fit_crit_A = 200
    fit_crit_B = 0.001

    for enduse in enduses:
        if enduse in installed_tech: # If technologies are defined for switch
            for technology in installed_tech[enduse]:
                sigmoid_parameters[technology] = {}

                if service_switch_crit:
                    year_until_switched = data['end_yr'] # Year until service are switched
                    market_entry = data['assumptions']['technologies'][technology]['market_entry']
                else:
                    # Get year which is furtherst away of all switch to installed technology
                    year_until_switched = 0
                    for switch in rs_fuel_switches:
                        if switch['enduse'] == enduse and switch['technology_install'] == technology:
                            if year_until_switched < switch['year_fuel_consumption_switched']:
                                year_until_switched = switch['year_fuel_consumption_switched']

                    market_entry = data['assumptions']['technologies'][technology]['market_entry']

                # Test wheter technology has the market entry before or after base year, If afterwards, set very small number in market entry year
                if market_entry > data['base_yr']:
                    point_x_by = market_entry
                    point_y_by = 0.001 # if market entry in a future year
                else: # If market entry before, set to 2015
                    point_x_by = data['base_yr']
                    point_y_by = service_tech_by_p[enduse][technology]

                    #If the base year is the market entry year use a very small number (as otherwise the fit does not work)
                    if point_y_by == 0:
                        point_y_by = 0.001

                # Future energy service demand (second point on sigmoid curve for fitting)
                point_x_projected = year_until_switched
                point_y_projected = service_tech_switched_p[enduse][technology]

                # Data of the two points
                xdata = np.array([point_x_by, point_x_projected])
                ydata = np.array([point_y_by, point_y_projected])

                # ----------------
                # Parameter fitting
                # ----------------
                # Generate possible starting parameters for fit
                possible_start_parameters = [1.0, 0.001, 0.01, 0.1, 60, 100, 200, 400, 500, 1000]
                for start in [x * 0.05 for x in range(0, 100)]:
                    possible_start_parameters.append(start)
                for start in range(1, 59):
                    possible_start_parameters.append(start)

                cnt = 0
                successfull = False
                while not successfull:
                    start_parameters = [possible_start_parameters[cnt], possible_start_parameters[cnt]]

                    try:
                        '''print("--------------- Technology " + str(technology) + str("  ") + str(cnt))
                        print("xdata: " + str(point_x_by) + str("  ") + str(point_x_projected))
                        print("ydata: " + str(point_y_by) + str("  ") + str(point_y_projected))
                        print("Lvalue: " + str(L_values[enduse][technology]))
                        print("start_parameters: " + str(start_parameters))
                        '''
                        fit_parameter = fit_sigmoid_diffusion(L_values[enduse][technology], xdata, ydata, start_parameters)
                        #print("fit_parameter: " + str(fit_parameter))

                        # Criteria when fit did not work
                        if fit_parameter[0] > fit_crit_A or fit_parameter[0] < fit_crit_B or fit_parameter[1] > fit_crit_A or fit_parameter[1] < 0  or fit_parameter[0] == start_parameters[0] or fit_parameter[1] == start_parameters[1]:
                            successfull = False
                            cnt += 1
                            if cnt >= len(possible_start_parameters):
                                sys.exit("Error2: CURVE FITTING DID NOT WORK")
                        else:
                            successfull = True
                            print("Fit successful {} for Technology: {} with fitting parameters: {} ".format(successfull, technology, fit_parameter))
                    except:
                        print("Tried unsuccessfully to do the fit with the following parameters: " + str(start_parameters[1]))
                        cnt += 1

                        if cnt >= len(possible_start_parameters):
                            sys.exit("Error: CURVE FITTING DID NOT WORK. Try changing fit_crit_A and fit_crit_B")
                print("INSTER PAARAMETERS")
                # Insert parameters
                sigmoid_parameters[technology]['midpoint'] = fit_parameter[0] #midpoint (x0)
                sigmoid_parameters[technology]['steepness'] = fit_parameter[1] #Steepnes (k)
                sigmoid_parameters[technology]['l_parameter'] = L_values[enduse][technology]

                #plot sigmoid curve
                plotout_sigmoid_tech_diff(L_values, technology, enduse, xdata, ydata, fit_parameter)

    print("finished...")
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

def get_closest_weather_station(longitude_reg, latitue_reg, weather_stations):
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
    for fueltype_str in fueltype_lu:
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

def get_technology_services_scenario(service_tech_by_p, share_service_tech_ey_p):
    """Get all those technologies with increased service in future

    Parameters
    ----------
    service_tech_by_p : dict
        Share of service per technology of base year of total service
    share_service_tech_ey_p : dict
        Share of service per technology of end year of total service

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

    if share_service_tech_ey_p == {}: # If no service switch defined
        tech_increased_service = []
        tech_decreased_share = []
        tech_constant_share = []
    else:
        for enduse in service_tech_by_p:
            tech_increased_service[enduse] = []
            tech_decreased_share[enduse] = []
            tech_constant_share[enduse] = []

            # Calculate fuel for each tech
            for tech in service_tech_by_p[enduse]:

                # If future larger share
                if service_tech_by_p[enduse][tech] < share_service_tech_ey_p[enduse][tech]:
                    tech_increased_service[enduse].append(tech)

                # If future smaller service share
                elif service_tech_by_p[enduse][tech] > share_service_tech_ey_p[enduse][tech]:
                    tech_decreased_share[enduse].append(tech)
                else:
                    tech_constant_share[enduse].append(tech)
        # Add to data
        #assumptions['rs_tech_increased_service'] = tech_increased_service
        #assumptions['rs_tech_decreased_share'] = tech_decreased_share
        #assumptions['rs_tech_constant_share'] = tech_constant_share
        print("   ")
        print("tech_increased_service:  " + str(tech_increased_service))
        print("tech_decreased_share:    " + str(tech_decreased_share))
        print("tech_constant_share:     " + str(tech_constant_share))
    return tech_increased_service, tech_decreased_share, tech_constant_share

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
    relative_share_service_tech_decrease_by = {}

    # Summed share of all diminishing technologies
    sum_service_tech_decrease_p = 0
    for tech in tech_decreased_share:
        sum_service_tech_decrease_p += service_tech_by_p[tech]

    # Relative of each diminishing tech
    for tech in tech_decreased_share:
        relative_share_service_tech_decrease_by[tech] = np.divide(1, sum_service_tech_decrease_p) * service_tech_by_p[tech]

    return relative_share_service_tech_decrease_by

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

def calc_hybrid_fuel_shapes_y_dh(fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, tech_low_high_p, eff_low_tech, eff_high_tech):
    """Calculate y_dh fuel shapes for hybrid technologies for every day in a year

    Depending on the share of servide each hybrid technology in every hour,
    the daily fuelshapes of each technology are taken for every hour respectively

    Parameters
    ----------
    fuel_shape_boilers_y_dh : array
        Fuel shape of low temperature technology (boiler technology)
    fuel_shape_hp_y_dh : array
        Fuel shape of high temp technology (y_dh) (heat pump technology)
    tech_low_high_p : array
        Share of service of technology in every hour (heat pump technology)
    eff_low_tech : array
        Efficiency of low temperature technology
    eff_high_tech : array
        Efficiency of high temperature technology

    Return
    ------
    fuel_shapes_hybrid_y_dh : array
        Fuel shape (y_dh) for hybrid technology

    Example
    --------
    E.g. 0-12, 16-24:   TechA
         12-16          TechA 50%, TechB 50%

    The daily shape is taken for TechA for 0-12 and weighted according to efficency
    Between 12 and Tech A and TechB are taken with 50% shares and weighted with either efficiency

    Info
    ----
    In case no fuel is provided for a day 'fuel_shapes_hybrid_y_dh' for this day is zero. Therfore
    the total sum of 'fuel_shapes_hybrid_y_dh not necessarily 365.
    """
    fuel_shapes_hybrid_y_dh = np.zeros((365, 24))

    for day in tech_low_high_p:
        dh_fuel_hybrid = np.zeros(24)

        for hour in range(24):

            # Shares of each technology for every hour
            low_p = tech_low_high_p[day][hour]['low']
            high_p = tech_low_high_p[day][hour]['high']

            # Efficiencies to weight dh shape
            eff_low = eff_low_tech[day][hour]
            eff_high = eff_high_tech[day][hour]

            # Calculate fuel for every hour
            if low_p == 0:
                fuel_boiler = 0
            else:
                fuel_boiler = np.divide(low_p * fuel_shape_boilers_y_dh[day][hour], eff_low)

            if high_p == 0:
                fuel_hp = 0
            else:
                fuel_hp = np.divide(high_p * fuel_shape_hp_y_dh[day][hour], eff_high)

            '''print("****hour")
            print(low_p)
            print(high_p)
            print(eff_low)
            print(eff_high)
            print(fuel_shape_boilers_y_dh[day][hour])
            print(fuel_shape_hp_y_dh[day][hour])
            print(np.divide(low_p * fuel_shape_boilers_y_dh[day][hour], eff_low))
            print(np.divide(high_p * fuel_shape_hp_y_dh[day][hour], eff_high))
            print("iff")
            print(fuel_boiler)
            print(fuel_hp)
            #if fuel_boiler + fuel_hp == 0:
            #    prit("eee")
            '''

            # Weighted hourly dh shape with efficiencies
            dh_fuel_hybrid[hour] = fuel_boiler + fuel_hp

        # Normalise dh shape
        fuel_shapes_hybrid_y_dh[day] = absolute_to_relative(dh_fuel_hybrid)

        ########
        '''plt.plot(dh_shape_hybrid)
        plt.show()
        '''
    # Testing
    #np.testing.assert_array_almost_equal(np.sum(fuel_shapes_hybrid_y_dh), 365, decimal=4, err_msg='Error in shapes')

    return fuel_shapes_hybrid_y_dh

def eff_heat_pump(m_slope, h_diff, b):
    """Calculate efficiency of heat pump

    Parameters
    ----------
    m_slope : float
        Slope of heat pump
    h_diff : float
        Temperature difference
    b : float
        Extrapolated intersect at temp diff of 10 degree (which is treated as efficiency)

    Returns
    efficiency_hp : float
        Efficiency of heat pump

    Notes
    -----
    Because the efficieny of heat pumps is temperature dependent, the efficiency needs to
    be calculated based on slope and intersect which is provided as input for temp difference 10
    and treated as efficiency

    The intersect (b) at temp differenc 10 is for ASHP about 6, for GSHP about 9
    """
    efficiency_hp = m_slope * h_diff + (b + (-1 * m_slope*10))

    return efficiency_hp

def initialise_service_fueltype_tech_by_p(fueltypes_lu, fuel_enduse_tech_p_by):
    service_fueltype_tech_by_p = {}

    for fueltype_int in fueltypes_lu.values():
        service_fueltype_tech_by_p[fueltype_int] = {}
        for tech in fuel_enduse_tech_p_by[fueltype_int]:
            service_fueltype_tech_by_p[fueltype_int][tech] = 0

    return service_fueltype_tech_by_p

def absolute_to_relative(absolute_array):
    """Convert absolute numbers in an array to relative

    If the total sum is zero, return an array with zeros and raise a warning

    Parameters
    ----------
    absolute_array : array
        Contains absolute numbers in it

    Returns
    -------
    relative_array : array
        Contains relative numbers


    """
    # If the total sum is zero, return same array
    if np.sum(absolute_array) == 0:
        relative_array = absolute_array
        #print("Warning: The sum was zero")
    else:
        #relative_array = np.divide(1, np.sum(absolute_array)) * absolute_array
        relative_array = np.nan_to_num(np.divide(1, np.sum(absolute_array)) * absolute_array)

    #assert np.sum(absolute_array) > 0
    return relative_array

def ss_summarise_fuel_per_enduse_all_sectors(ss_fuel_raw_data_enduses, ss_enduses, nr_fueltypes):
    """Aggregated fuel for all sectors according to enduse
    """
    aggregated_fuel_enduse = {}

    # Initialise
    for enduse in ss_enduses:
        aggregated_fuel_enduse[str(enduse)] = np.zeros((nr_fueltypes))

    # Iterate and sum fuel per enduse
    for _, fuels_sector in ss_fuel_raw_data_enduses.items():
        for enduse, fuels_enduse in fuels_sector.items():
            aggregated_fuel_enduse[enduse] += fuels_enduse

    return aggregated_fuel_enduse
