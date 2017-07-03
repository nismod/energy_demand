"""This file stores all functions of main.py"""
import csv
from datetime import date
from datetime import timedelta as td
import math as m
import copy
import numpy as np
import yaml

import matplotlib.pyplot as plt
from haversine import haversine # Package to calculate distance between two long/lat points
import unittest

from energy_demand.scripts_geography import weather_station_location as gg
from energy_demand.scripts_diffusion import diffusion_technologies
from energy_demand.scripts_initalisations import initialisations as init

ASSERTIONS = unittest.TestCase('__init__')
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member

def convert_dh_yd_to_yh(shape_yd, shape_y_dh):
    """Convert yd shape and shape for every day (y_dh) into yh

    Parameters
    ----------
    shape_yd : array
        Array with yd shape
    shape_y_dh : array
        Array with y_dh shape
    
    Return
    ------
    shape_yh : array
        Array with yh shape
    """
    shape_yh = np.zeros((365, 24))
    for day, value_yd in enumerate(shape_yd):
        shape_yh[day] = value_yd * shape_y_dh[day]

    return shape_yh


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

    # ------------------------------------------------
    # Testing wheter the provided inputs make sense
    # -------------------------------------------------
    for enduse in assumptions['rs_all_specified_tech_enduse_by']:
        if enduse in rs_service_switch_enduse_crit: #If switch is defined for this enduse
            for tech in assumptions['rs_all_specified_tech_enduse_by'][enduse]:
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
        closest_weatherstation_id = gg.get_closest_weather_station(longitude, latitude, data['weather_stations'])

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
    t_base_frac = diffusion_technologies.sigmoid_diffusion(base_yr, curr_y, end_yr, assumptions['sig_midpoint'], assumptions['sig_steeppness'])

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
            temp_data_climate_change[weather_station_id][current_year] = np.zeros((365, 24))

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




def get_tech_type(tech_name, assumptions, enduse=''):
    """Get technology type of technology
    Either a technology is a hybrid technology, a heat pump,
    a constant heating technology or a regular technolgy
    Parameters
    ----------
    assumptions : dict
        All technology lists are defined in assumptions
    Returns
    ------
    tech_type : string
        Technology type
    """
    # If all technologies for enduse
    if enduse == 'rs_water_heating':
        tech_type = 'water_heating'
    else:
        if tech_name in assumptions['list_tech_heating_hybrid']:
            tech_type = 'hybrid_tech'
        elif tech_name in assumptions['list_tech_heating_temp_dep']:
            tech_type = 'heat_pump'
        elif tech_name in assumptions['list_tech_heating_const']:
            tech_type = 'boiler_heating_tech'
        elif tech_name in assumptions['list_tech_cooling_temp_dep']:
            tech_type = 'cooling_tech'
        elif tech_name in assumptions['list_tech_cooling_const']:
            tech_type = 'cooling_tech_temp_dependent'
        elif tech_name in assumptions['list_tech_rs_lighting']:
            tech_type = 'lighting_technology'
        #elif tech_name in assumptions['list_water_heating']:
        #    tech_type = 'water_heating'
        else:
            tech_type = 'regular_tech'

    return tech_type

def get_service_fueltype_tech(assumptions, fueltypes_lu, fuel_p_tech_by, fuels, tech_stock):
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
    # Initialise
    service = init.init_nested_dict(fuels, fueltypes_lu.values(), 'brackets') # Energy service per technology for base year
    service_tech_by_p = init.init_dict(fuels, 'brackets') # Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p = init.init_nested_dict(fuels, fueltypes_lu.values(), 'brackets') # Percentage of service per technologies within the fueltypes
    service_fueltype_by_p = init.init_nested_dict(service_tech_by_p.keys(), range(len(fueltypes_lu)), 'zero') # Percentage of service per fueltype

    for enduse, fuel in fuels.items():
        for fueltype, fuel_fueltype in enumerate(fuel):
            tot_service_fueltype = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype].items():
                #print("------------Tech: " + str(tech))

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype

                # Get technology type
                tech_type = get_tech_type(tech, assumptions)

                # Get efficiency depending whether hybrid or regular technology or heat pumps for base year
                if tech_type == 'hybrid_tech':
                    eff_tech = assumptions['technologies']['hybrid_gas_elec']['average_efficiency_national_by'] #TODO: CONTROL
                elif tech_type == 'heat_pump':
                    eff_tech = eff_heat_pump(m_slope=assumptions['hp_slope_assumption'], h_diff=10, b=tech_stock[tech]['eff_by'])
                else:
                    eff_tech = tech_stock[tech]['eff_by']

                # Energy service of end use: Service == Fuel of technoloy * efficiency
                service_fueltype_tech = fuel_tech * eff_tech

                # Add energy service demand
                service[enduse][fueltype][tech] = service_fueltype_tech

                # Total energy service demand within a fueltype
                tot_service_fueltype += service_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]:
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = 0
                    service_fueltype_by_p[enduse][fueltype] += 0
                else:
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = np.divide(1, tot_service_fueltype) * service[enduse][fueltype][tech]
                    service_fueltype_by_p[enduse][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_service = init.sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():
                service_tech_by_p[enduse][technology] = np.divide(1, total_service) * service_tech
                #print("Technology_enduse: " + str(technology) + str("  ") + str(service_tech))

        #print("Total Service base year for enduse {}  :  {}".format(enduse, _a))

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:
            service_fueltype_by_p[enduse][fueltype] = np.divide(1, total_service) * service_fueltype_by_p[enduse][fueltype]

    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    '''
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p



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
            eff_heat_pump_by = technologies[heat_pump_type]['eff_by']
            eff_heat_pump_ey = technologies[heat_pump_type]['eff_ey']
            eff_achieved = technologies[heat_pump_type]['eff_achieved']
            market_entry = technologies[heat_pump_type]['market_entry']

            # Calc average values
            av_eff_hps_by += share_heat_pump * eff_heat_pump_by
            av_eff_hps_ey += share_heat_pump * eff_heat_pump_ey
            eff_achieved_av += share_heat_pump * eff_achieved

            if market_entry < market_entry_lowest:
                market_entry_lowest = market_entry

        # Add average 'av_heat_pumps' to technology dict
        fueltype_string = get_fueltype_str(data['lu_fueltype'], fueltype)
        #name_av_hp = "av_heat_pump_{}".format(str(fueltype_string))
        name_av_hp = "{}_heat_pumps".format(str(fueltype_string))
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
        #print("tech_increased_service:  " + str(tech_increased_service))
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

    Depending on the share of service each hybrid technology in every hour,
    the daily fuelshapes of each technology are taken for every hour respectively

    #TODO: IMPROVE DESCRITPION

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








def plot_x_days(all_hours_year, region, days):
    """With input 2 dim array plot daily load"""

    x_values = range(days * 24)
    y_values = []
    #y_values = all_hours_year[region].values()

    for day, daily_values in enumerate(all_hours_year[region].values()):

        # ONLY PLOT HALF A YEAR
        if day < days:
            for hour in daily_values:
                y_values.append(hour)

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Energy demand in kWh")
    plt.title("Energy Demand")
    plt.legend()
    plt.show()


def plot_load_shape_yd(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 0] * 100) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("Hours")
    plt.ylabel("Percentage of daily demand")
    plt.title("Load curve of a day")
    plt.legend()
    plt.show()


def plot_load_shape_yd_non_resid(daily_load_shape):
    """With input 2 dim array plot daily load"""

    x_values = range(24)
    y_values = list(daily_load_shape[:, 1]) # to get percentages

    plt.plot(x_values, y_values)

    plt.xlabel("ABSOLUTE VALUES TEST NONRESID")
    plt.legend()
    plt.show()

def plot_stacked_Country_end_use(results_resid, enduses_data, attribute_to_get): # nr_of_day_to_plot, fueltype, yearday, reg_name):
    """Plots stacked end_use for a region

    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """
    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years

    x = range(nr_y_to_plot)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((len(enduses_data), nr_y_to_plot))

    for k, enduse in enumerate(enduses_data):
        legend_entries.append(enduse)
        data_over_years = []

        for model_year_object in results_resid:
            tot_fuel = getattr(model_year_object, attribute_to_get) # Hourly fuel data
            data_over_years.append(tot_fuel[enduse])

        Y_init[k] = data_over_years

    #print("Y_init:" + str(Y_init))
    #color_list = ["green", "red", "#6E5160"]

    sp = ax.stackplot(x, Y_init)
    proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]

    ax.legend(proxy, legend_entries)

    #ticks x axis
    #ticks_x = range(2015, 2015 + nr_y_to_plot)
    #plt.xticks(ticks_x)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='red')
    plt.axis('tight')

    plt.xlabel("Simulation years")
    plt.title("Stacked energy demand for simulation years for whole UK")

    plt.show()

def plot_load_curves_fueltype(results_resid, data): # nr_of_day_to_plot, fueltype, yearday, reg_name):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years

    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        for fueltype_str in data['lu_fueltype']:
            if data['lu_fueltype'][fueltype_str] == fueltype:
                fueltype_in_string = fueltype_str
        legend_entries.append(fueltype_in_string)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_resid:
            # Max hourly load curve of fueltype
            fueltype_load_max_h = model_year_object.tot_country_fuel_load_max_h

            data_over_years.append(fueltype_load_max_h[fueltype][0])

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='red')
    plt.axis('tight')

    plt.ylabel("Percent %")
    plt.xlabel("Simulation years")
    plt.title("Load factor of maximum hour across all enduses")

    plt.show()

def plot_fuels_tot_all_enduses_week(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    # Number of days to plot
    days_to_plot = range(10, 17)

    # Which year in simulation (2015 = 0)
    year_to_plot = 2

    fig, ax = plt.subplots()
    nr_of_h_to_plot = len(days_to_plot) * 24

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_of_h_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        fueltype_in_string = mf.get_fueltype_str(data['lu_fueltype'], fueltype)
        legend_entries.append(fueltype_in_string)

        # Read out fueltype specific max h load
        tot_fuels = getattr(results_resid[year_to_plot], attribute_to_get)
        print("TEESTFUL : " + str(np.sum(tot_fuels[fueltype])))
        data_over_day = []
        for day, daily_values in enumerate(tot_fuels[fueltype]):
            if day in days_to_plot:
                for hour in daily_values:
                    data_over_day.append(hour)

        Y_init[fueltype] = data_over_day

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    x_tick_pos = []
    for day in range(len(days_to_plot)):
        x_tick_pos.append(day * 24)
    plt.xticks(x_tick_pos, days_to_plot, color='black')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("days")
    plt.title("Total yearly fuels of all enduses per fueltype for simulation year {} ".format(year_to_plot + 2050))
    plt.show()

def plot_fuels_tot_all_enduses(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots()
    nr_y_to_plot = len(results_resid) #number of simluated years
    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        fueltype_in_string = mf.get_fueltype_str(data['lu_fueltype'], fueltype)
        legend_entries.append(fueltype_in_string)

        # Read out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_resid:

            tot_fuels = getattr(model_year_object, attribute_to_get)

            #for every hour is summed to have yearl fuel
            tot_fuel_fueltype_y = np.sum(tot_fuels[fueltype]) 
            data_over_years.append(tot_fuel_fueltype_y)

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Total yearly fuels of all enduses per fueltype")
    plt.show()


def plot_fuels_peak_hour(results_resid, data, attribute_to_get):
    """Plots stacked end_use for a region


    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    # INFO Cannot plot a single year?
    """

    fig, ax = plt.subplots() #fig is needed
    nr_y_to_plot = len(results_resid) #number of simluated years
    x = range(nr_y_to_plot)
    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((data['nr_of_fueltypes'], nr_y_to_plot))

    for fueltype, _ in enumerate(data['lu_fueltype']):

        # Legend
        fueltype_in_string = mf.get_fueltype_str(data['lu_fueltype'], fueltype)

        legend_entries.append(fueltype_in_string)

        # REad out fueltype specific max h load
        data_over_years = []
        for model_year_object in results_resid:
            fueltype_load_max_h = getattr(model_year_object, attribute_to_get)
            data_over_years.append(fueltype_load_max_h[fueltype])

        Y_init[fueltype] = data_over_years

    # Plot lines
    for line, _ in enumerate(Y_init):
        plt.plot(Y_init[line])

    ax.legend(legend_entries)

    plt.xticks(range(nr_y_to_plot), range(2015, 2015 + nr_y_to_plot), color='green')
    plt.axis('tight')

    plt.ylabel("Fuel")
    plt.xlabel("Simulation years")
    plt.title("Fuels for peak hour in a year across all enduses")
    plt.show()