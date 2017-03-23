"""This file stores all functions of main.py"""

import os
import csv
from datetime import date
from datetime import timedelta as td
import numpy as np
import data_loader as dl
import yaml

# pylint: disable=I0011,C0321,C0301,C0103, C0325

def convert_out_format_es(data, data_ext, all_regions):
    """Adds total hourly fuel data into nested dict

    Parameters
    ----------
    data : dict
        Dict with own data
    data_ext : dict
        External data
    all_regions : list
        Contains all objects of the region

    Returns
    -------
    out_dict : dict
        Returns a dict for energy supply model with fueltype, region, hour"""

    # Create timesteps for full year (wrapper-timesteps)
    out_dict = initialise_energy_supply_dict(len(data['fuel_type_lu']), len(data['reg_lu']), data_ext['glob_var']['base_year'])

    for reg in all_regions:
        region_name = reg.reg_id # Get object region name
        hourly_all_fuels = reg.tot_all_enduses_h()  # Get total fuel

        # Iterate fueltypes
        for fueltype in data['fuel_type_lu']:
            out_dict[fueltype][region_name] = dict(enumerate(hourly_all_fuels[fueltype])) # Convert array into dict for out_read

    return out_dict

def load_data(data, path_main, data_ext):
    """All base data no provided externally are loaded

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------
    data : dict
        Dict with own data
    path_main : str
        Path to all data of model run which are not provided externally by wrapper

    Returns
    -------
    data : list
        Returns a list where storing all data

    """
    path_dict = {

        # Residential
        # -----------
        'path_main': path_main,
        'path_pop_reg_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_nr_regions.csv'),
        'path_dwtype_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),
        'path_lookup_appliances':os.path.join(path_main, 'residential_model/lookup_appliances_HES.csv'),
        'path_fuel_type_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_fuel_types.csv'),
        'path_day_type_lu': os.path.join(path_main, 'residential_model/lookup_day_type.csv'),
        'path_bd_e_load_profiles': os.path.join(path_main, 'residential_model/HES_base_appliances_eletricity_load_profiles.csv'),
        'path_temp_2015': os.path.join(path_main, 'residential_model/SNCWV_YEAR_2015.csv'),
        'path_hourly_gas_shape_resid': os.path.join(path_main, 'residential_model/SANSOM_residential_gas_hourly_shape.csv'),
        'path_dwtype_dist': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_distribution.csv'),
        'path_dwtype_age': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_age.csv'),
        'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_floorarea.csv'),
        'path_reg_floorarea': os.path.join(path_main, 'residential_model/data_residential_model_floorarea.csv'),
        'path_reg_dw_nr': os.path.join(path_main, 'residential_model/data_residential_model_nr_dwellings.csv'),
        'path_data_residential_by_fuel_end_uses': os.path.join(path_main, 'residential_model/data_residential_by_fuel_end_uses.csv'),
        'path_lu_appliances_HES_matched': os.path.join(path_main, 'residential_model/lookup_appliances_HES_matched.csv'),
        'path_txt_shapes_resid': os.path.join(path_main, 'residential_model/txt_load_shapes'),

        # Service
        # -----------
        'path_temp_2015_service': os.path.join(path_main, 'service_model/CSV_YEAR_2015_service.csv')
        }

    data['path_dict'] = path_dict

    # -- Reads in all csv files and store them in a dictionary
    data['path_main'] = path_main

    # Lookup data
    data['reg_lu'] = read_csv_dict_no_header(path_dict['path_pop_reg_lu'])                # Region lookup table
    data['dwtype_lu'] = read_csv_dict_no_header(path_dict['path_dwtype_lu'])              # Dwelling types lookup table
    data['app_type_lu'] = read_csv(path_dict['path_lookup_appliances'])                   # Appliances types lookup table
    data['fuel_type_lu'] = read_csv_dict_no_header(path_dict['path_fuel_type_lu'])        # Fuel type lookup
    data['day_type_lu'] = read_csv(path_dict['path_day_type_lu'])                         # Day type lookup

    #fuel_bd_data = read_csv_float(path_dict['path_base_data_fuel'])               # All disaggregated fuels for different regions
    data['path_temp_2015'] = read_csv(path_dict['path_temp_2015'])                         # csv_temp_2015 #TODO: Delete because loaded in read_shp_heating_gas
    data['hourly_gas_shape'] = read_csv_float(path_dict['path_hourly_gas_shape_resid'])         # Load hourly shape for gas from Robert Sansom #TODO: REmove because in read_shp_heating_gas

    #path_dwtype_age = read_csv_float(['path_dwtype_age'])
    data['dwtype_distr'] = read_csv_nested_dict(path_dict['path_dwtype_dist'])
    data['dwtype_age_distr'] = read_csv_nested_dict(path_dict['path_dwtype_age'])
    data['dwtype_floorarea']  = read_csv_dict(path_dict['path_dwtype_floorarea_dw_type'])
    data['reg_floorarea'] = read_csv_dict_no_header(path_dict['path_reg_floorarea'])
    data['reg_dw_nr'] = read_csv_dict_no_header(path_dict['path_reg_dw_nr'])

    # load shapes
    data['dict_shp_enduse_h_resid'] = {}
    data['dict_shp_enduse_d_resid'] = {}

    # Data new approach
    data_residential_by_fuel_end_uses = read_csv_base_data_resid(path_dict['path_data_residential_by_fuel_end_uses']) # Yearly end use data

    # Add the yearly fuel data of the external Wrapper to the enduses (RESIDENTIAL HERE)
    ###data = add_yearly_external_fuel_data(data, data_ext, data_residential_by_fuel_end_uses) #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE

    data['lu_appliances_HES_matched'] = read_csv(path_dict['path_lu_appliances_HES_matched'])

    # SERVICE SECTOR
    data['csv_temp_2015_service'] = read_csv(path_dict['path_temp_2015_service']) # csv_temp_2015 #TODO: Dele
    data['dict_shp_enduse_h_service'] = {}
    data['dict_shp_enduse_d_service'] = {}

    # ----------------------------------------
    # --Convert loaded data into correct units
    # ----------------------------------------

    # Fuel residential
    for enduse in data_residential_by_fuel_end_uses:
        data_residential_by_fuel_end_uses[enduse] = conversion_ktoe_gwh(data_residential_by_fuel_end_uses[enduse]) # TODO: Check if ktoe
    data['data_residential_by_fuel_end_uses'] = data_residential_by_fuel_end_uses


    # --- Generate load_shapes ##TODO
    data = dl.generate_data(data) # Otherwise already read out files are read in from txt files

    # -- Read in load shapes from files #TODO::
    data = dl.collect_shapes_from_txts(data)

    # ---TESTS
    # Test if numer of fuel types is identical (Fuel lookup needs to have same dimension as end-use fuels)
    for end_use in data['data_residential_by_fuel_end_uses']:
        assert len(data['fuel_type_lu']) == len(data['data_residential_by_fuel_end_uses'][end_use]) # Fuel in fuel distionary does not correspond to len of input fuels

    return data

def initialise_energy_supply_dict(number_fuel_types, number_reg, base_year):
    """Generates nested dictionary for providing results to smif

    Parameters
    ----------
    number_fuel_types : int
        Number of fuel types
    number_reg : int
        Number of regions
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
        for j in range(number_reg):
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

def datetime_range(start=None, end=None):
    """Calculates all dates between a star and end date.

    Parameters
    ----------
    start : date
        Start date
    end : date
        end date
    """
    span = end - start
    for i in range(span.days + 1):
        yield start + td(days=i)

def conversion_ktoe_gwh(data_ktoe):
    """Conversion of ktoe to gwh

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
    list_dates = list(datetime_range(start=date(base_year, 1, 1), end=date(base_year, 12, 31))) # List with every date in a year

    #yaml_list = []
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

            #Add to yaml listyaml
            #yaml_list.append({'id': yearday_h_id, 'start': start_period, 'end': end_period})

    return timesteps

def get_weekday_type(date_from_yearday):
    """Gets the weekday of a date

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

                # Test if float or string
                try:
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

        # Iterate rows
        for row in read_lines:

            # Iterate row entries
            try:
                out_dict[int(row[0])] = float(row[1])
            except ValueError:
                out_dict[int(row[0])] = str(row[1])

    return out_dict


def disaggregate_base_demand_for_reg(data, reg_data_assump_disaggreg, data_ext):
    """This function disaggregates fuel demand based on region specific parameters
    for the base year

    The residential, service and industry demand is disaggregated according to
    different factors

    - floorarea
    - population
    - etc...abs
    TODO: Write disaggregation
    """

    #TODO: So far simple disaggregation by population

    regions = data['reg_lu']
    national_fuel = data['data_residential_by_fuel_end_uses'] # residential data
    reg_fuel = {}
    #reg_data_assump_disaggreg = reg_data_assump_disaggreg
    base_year = data_ext['glob_var']['base_year']

    # Iterate regions
    for region in regions:

        #Scrap improve
        reg_pop = data_ext['population'][base_year][region] # Regional popluation
        total_pop = sum(data_ext['population'][base_year].values()) # Total population
        inter_dict = {} # Disaggregate fuel depending on end_use

        for enduse in national_fuel:

            # So far simply pop
            reg_disaggregate_factor_per_enduse_and_reg = reg_pop / total_pop  #TODO: create dict with disaggregation factors

            #TODO: Get enduse_specific disaggreagtion reg_disaggregate_factor_per_enduse_and_reg
            inter_dict[enduse] = national_fuel[enduse] * reg_disaggregate_factor_per_enduse_and_reg

        reg_fuel[region] = inter_dict

    data['fueldata_disagg'] = reg_fuel

    return data

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

def write_to_csv_will(data, result_dict, reg_lu, crit_YAML):
    """ Write reults for energy supply model
    e.g.

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
                        start_id = "P{}H".format(_day * 24 + _hour)
                        end_id = "P{}H".format(_day * 24 + _hour + 1)
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
        #print("fueltype: " + str(fueltype))
        #print("a: " + str(a))

        # REplace technologies with technology ID
        replaced_tech_with_ID = []
        for enduse_tech_eff in a:
            technology = enduse_tech_eff[0]
            tech_eff = enduse_tech_eff[1]
            replaced_tech_with_ID.append((tech_lu[technology], tech_eff))
        #print("replaced_tech_with_ID: " + str(replaced_tech_with_ID))

        # IF empty replace with 0.0, 0.0) to have an array with length 2
        if replaced_tech_with_ID == []:
            out_dict[fueltype] = []
        else:
            replaced_with_ID = np.array(replaced_tech_with_ID, dtype=float)

            out_dict[fueltype] = replaced_with_ID

    return out_dict

def apply_elasticity(base_demand, elasticity, price_base, price_curr):
    """Calculate current demand based on demand elasticity

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
    pricediff_p = (price_base - price_curr) / price_base                   # Absolute price difference (e.g. 20 - 15 --> 5)

    # New current demand
    current_demand = -1 * ((elasticity * pricediff_p * base_demand) - base_demand)

    return current_demand

def convert_date_to_yearday(date_base_year, month, day):
    """Converts a base year day to yearday of baseyear"""

    date_base_year = date(date_base_year, month, day)
    yearday = date_base_year.timetuple()[7] - 1
    return yearday

def add_yearly_external_fuel_data(data, data_ext, dict_to_add_data): #TODO: ALSO IMPORT ALL OTHER END USE RELATED THINS SUCH AS SHAPE
    """ This data check what enduses are provided by wrapper
    and then adds the yearls fule data to data"""
    for external_enduse in data_ext['external_enduses']:

        new_fuel_array = np.zeros((len(data['fuel_type_lu']), 1))
        for fueltype in data_ext['external_enduses'][external_enduse]:
            new_fuel_array[fueltype] = data_ext['external_enduses'][external_enduse][fueltype]
        dict_to_add_data[external_enduse] = new_fuel_array
    return data


'''
# Description: Degree days calculator
# Aurthors: Pranab Baruah; Scott Thacker

import math as m

# estimate mean temperature from base temp
def DD_HITCHIN_BASE(d_days, t_base, days):

    k       = 0.8
    t_mean  = 1.0
    DD  = days * (t_base - t_mean) / (1 - m.exp(-k*(t_base-t_mean)))
    while DD >= d_days:
        DD  = days * (t_base - t_mean) / (1 - m.exp(-k*(t_base-t_mean)))
        t_prev = t_mean - 0.001
        t_mean = t_mean + 0.001
        
    return t_prev

# function to calculate degree days
def DD_HITCHIN(t_mean, t_base, days):
    
    k   = 0.8
    DD  = days * (t_base - t_mean) / (1 - m.exp(-k*(t_base-t_mean)))
    
    return DD
'''