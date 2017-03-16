"""This file stores all functions of main.py"""

import sys
import os
import csv
import traceback

from datetime import date
from datetime import timedelta as td
import numpy as np
print ("Loading main functions")
# pylint: disable=I0011,C0321,C0301,C0103, C0325

def convert_result_to_final_total_format(data, all_Regions):
    """Convert into nested citionary with fueltype, region, hour"""

    timesteps, _ = timesteps_full_year()                                 # Create timesteps for full year (wrapper-timesteps)
    result_dict = init_dict_energy_supply(data['fuel_type_lu'], data['reg_lu'], timesteps)

    for reg in all_Regions:
        print("reg_id " + str(reg))
        region_name = reg.reg_id

        # Get total fuel fuel
        hourly_all_fuels = reg.tot_all_enduses_h()

        # Iterate fueltypes
        for fueltype in data['fuel_type_lu']:

            fuel_total_h_all_end_uses = hourly_all_fuels[fueltype]

            # Convert array into dict for out_read
            out_dict = dict(enumerate(fuel_total_h_all_end_uses))

            result_dict[fueltype][region_name] = out_dict

    return result_dict

def load_data(data, path_main):
    """All base data no provided externally are loaded

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------
    data : dict
        Dict with own data

    Returns
    -------
    data : list
        Returns a list where all datas are wrapped together.

    Notes
    -----

    """
    # As soon as old model is deleted, mode this to data_loader
    import energy_demand.data_loader as dl

    # ------Read in all data from csv files which have to be read in anyway
    data = read_data(data, path_main)

    # --- Execute data generatore
    run_data_collection = True # Otherwise already read out files are read in from txt files
    data = dl.generate_data(data, run_data_collection)


    # ---TESTS
    # Test if numer of fuel types is identical (Fuel lookup needs to have same dimension as end-use fuels)
    for end_use in data['data_residential_by_fuel_end_uses']:
        assert len(data['fuel_type_lu']) == len(data['data_residential_by_fuel_end_uses'][end_use]) # Fuel in fuel distionary does not correspond to len of input fuels

    # test if...
    return data

def init_dict_energy_supply(fuel_type_lu, reg_lu, timesteps):
    """Generates nested dictionary for providing results to smif

    Parameters
    ----------
    fuel_type_lu : array
        Contains all fuel types
    reg_pop : array
        Containes all population of different regions
    timesteps : ??
        Contaings all timesteps for the full year

    Returns
    -------
    result_dict : dict
        Returns a nested dictionary for energy supply model. (fueltype/region/timeID)

    Notes
    -----
    notes
    """
    result_dict = {}
    for i in range(len(fuel_type_lu)):
        result_dict[i] = {}
        for j in range(len(reg_lu)):
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
    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines:
            list_elements.append(row)

    # Convert list into array
    elements_array = np.array(list_elements, float)
    return elements_array

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

    # Convert list into array
    elements_array = np.array(list_elements)
    return elements_array

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
    """
    l = []
    end_uses_dict = {}

    with open(path_to_csv, 'r') as csvfile:               # Read CSV file
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines)                      # Skip first row

        # Iterate rows
        for row in read_lines: # select row
            l.append(row)

        for i in _headings[1:]: # skip first
            end_uses_dict[i] = np.zeros((len(l), 1)) # len fuel_ids

        cnt_fueltype = 0
        for row in l:
            cnt = 1 #skip first
            for i in row[1:]:
                end_use = _headings[cnt]
                end_uses_dict[end_use][cnt_fueltype] = i
                cnt += 1

            cnt_fueltype += 1

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

def writeToEnergySupply(path_out_csv, fueltype, in_data):
    '''
    REads out results (which still need to be preared) to list of energy supply model.

    Input:
    -path_out_csv   Path to energy supply resulting table
    -in_data        Data input

    Output:
    -               Print results
    '''
    outData = []

    # NEW: Create ID

    # WRITE TO YAMAL FILE

    print("Data for energy supply model")

    for region_nr in range(len(in_data[fueltype])):
        supplyTimeStep = 0
        for timestep in range(len(in_data[fueltype][region_nr])): #Iterate over timesteps

            if timestep == (1 * 7 * 24) or timestep == (2 * 7 * 24) or timestep == (3 * 7 * 24) or timestep == (4 * 7 * 24):
                supplyTimeStep = 0

            outData.append([region_nr, timestep, supplyTimeStep, in_data[fueltype][region_nr][timestep].sum()]) # List with data out

            print(" Region: " + str(region_nr) + str("   Demand teimstep:  ") + str(timestep) + str("   supplyTimeStep: " + str(supplyTimeStep) + str("   Sum: " + str(in_data[fueltype][region_nr][timestep].sum()))))
            supplyTimeStep += 1

    '''# Read existing CSV
    existing_data = read_csv(path_dictpath_out_csv)
    print(existing_data)

    for i, j in zip(existing_data, new_data):
        i[5] = j[5]

    print("---")
    print(existing_data)
    '''
    with open(path_out_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for row in outData: #existing_data:
            writer.writerow(row)
    return

def shape_bd_hd(csv_temp_2015, hourly_gas_shape):
    """
    This function creates the shape of the base year heating demand over the full year

    #Todo: Different shapes depending on workingday/holiday

    Input:
    -csv_temp_2015      SNCWV temperatures for every gas-year day
    -hourly_gas_shape   Shape of hourly gas for Day, weekday, weekend (Data from Robert Sansom)

    """

    # Initilaise array to store all values for a year
    year_days, hours = range(365), range(24)

    # Get hourly distribution (Sansom Data)
    # ------------------------------------
    hourly_hd = np.zeros((1, len(hours)), dtype=float)

    # Hourly gas shape
    hourly_gas_shape_day = hourly_gas_shape[0]
    hourly_gas_shape_wkday = hourly_gas_shape[1]
    hourly_gas_shape_wkend = hourly_gas_shape[2]

    # Initialistion
    year_raw_values = np.zeros((len(year_days), len(hours)), dtype=float)

    # Initialise dictionary with every day and hour
    hd_data = np.zeros((len(year_days), len(hours)), dtype=float)

    # Read in SNCWV and calculate heatin demand for every yearday
    for row in csv_temp_2015:
        sncwv = float(row[1])

        row_split = row[0].split("/")
        _day = int(row_split[0])
        _month = int(row_split[1])
        _year = int(row_split[2])

        date_gas_day = date(_year, _month, _day)

        # Calculate demand based on correlation
        heating_demand_correlation = -158.15 * sncwv + 3622.5

        _info = date_gas_day.timetuple()
        #month_python = _info[1] - 1       # - 1 because in _info: Month 1 = Jan
        yearday_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        weekday = _info[6]                # 0: Monday

        # Distribute daily deamd into hourly demand
        if weekday == 5 or weekday == 6:
            _data = hourly_gas_shape_wkend * heating_demand_correlation
            hd_data[yearday_python] = _data  # DATA ARRAY
        else:
            _data = hourly_gas_shape_wkday * heating_demand_correlation
            hd_data[yearday_python] = _data  # DATA ARRAY

    # Convert yearly data into percentages (create shape). Calculate Shape of the eletrictiy distribution of the appliances by assigning percent values each
    total_y_hd = hd_data.sum()  # Calculate yearly total demand over all day years and all appliances
    shape_hd = np.zeros((len(year_days), len(hours)), dtype=float)
    shape_hd = (1.0/total_y_hd) * hd_data

    # Error #TODO: write seperately
    try:
        _control = round(float(shape_hd.sum()), 4) # Sum of input energy data, rounded to 4 digits
        if _control == 1:
            print("Sum of shape is 100 % - good")
        else:
            _err = "Error: Something with the shape curve creation went wrong "
            raise Exception(_err)

    except _err:
        _val = sys.exc_info()
        _, _value, _tb = sys.exc_info()
        print("Errors from function shape curve gas:")
        traceback.print_tb(_tb)         # Print errors
        print (_value)
        sys.exit()

    print("Sum appliances_shape: " + str(shape_hd.sum()))
    return shape_hd

def get_bd_hd_gas(shape_hd_gas, reg_lu, fuel_type_lu, fuel_bd_data):
    '''This function calculates absolut heating demands with help of shape for all regions

    out:
    -fuel_type_per_region_hourly        Fueltype per region per appliance per hour
        fueltype
            region
                year_days
                    appliances
                        hours
    '''
    fuelType_gas = 1 # gas

    fuel_bd_data_gs = fuel_bd_data[:, 2] # Gas data heating deamnd

    dim_appliance = shape_hd_gas.shape

    # Initialise array
    fuel_type_per_region = np.zeros((len(fuel_type_lu), len(reg_lu)), dtype=float) # To store absolute demand values
    fuel_type_per_region_hourly = np.zeros((len(fuel_type_lu), len(reg_lu), dim_appliance[0], dim_appliance[1]), dtype=float) # To store absolute demand values of hourly appliances

    # Add gas base data
    for region_nr in range(len(reg_lu)):
        fuel_type_per_region[fuelType_gas][region_nr] = fuel_bd_data_gs[region_nr]

    # Appliances per region
    for region_nr in range(len(reg_lu)):
        reg_demand = fuel_type_per_region[fuelType_gas][region_nr]
        reg_hd_gas = shape_hd_gas * reg_demand # heating demand shape * regional demand in [GWh]

        fuel_type_per_region_hourly[fuelType_gas][region_nr] = reg_hd_gas

    # Test for errors
    try:
        _control = round(float(fuel_bd_data_gs.sum()), 4) # Sum of input energy data, rounded to 4 digits
        _control2 = round(float(fuel_type_per_region_hourly.sum()), 4)   # Sum of output energy data, rounded to 4 digits

        if _control == _control2:
            print("Input total energy demand has been correctly disaggregated.")
        else:
            _err = "Error: Something with the disaggregation went wrong.. "
            raise Exception(_err)

    except _err:
        _val = sys.exc_info()
        _, _value, _tb = sys.exc_info()
        print("Errors from function bd_hd_gas:")
        traceback.print_tb(_tb)         # Print errors
        print (_value)
        sys.exit()

    return fuel_type_per_region_hourly

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

def timesteps_full_year():
    """This function generates a single list from a list with start and end dates
    and adds the same date into the list according to the number of hours in a day.

    Parameters
    ----------


    Returns
    -------
    timestep : list
        List containing all dates according to number of hours
    """
    #TODO: improve

    full_year_date = [date(2015, 1, 1), date(2015, 12, 31)] # Base Year
    start_date, end_date = full_year_date[0], full_year_date[1]
    list_dates = list(datetime_range(start=start_date, end=end_date)) # List with every date in a year

    hours, days = 24, range(365)
    yaml_list = [] ## l = [{'id': value, 'start': 'p', 'end': 'P2',   }

    timestep_full_year_dict = {} #  YEARDAY_H
    timestep_dates = []

    #Add to list
    #h_year_id = 0
    for day_date in list_dates:
        _info = day_date.timetuple() # Get date
        day_of_that_year = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

        # Interate hours
        for h_id in range(hours):
            #Create ID (yearday_hour of day)
            start_period = "P{}H".format(day_of_that_year * 24 + h_id)
            end_period = "P{}H".format(day_of_that_year * 24 + h_id + 1)

            yearday_h_id = str(str(day_of_that_year) + str("_") + str(h_id))

            #start_period = str("P" + str(h_year_id) + str("H"))
            #end_period = str("P" + str(h_year_id + 1) + str("H"))

            # Add to dict
            timestep_full_year_dict[yearday_h_id] = {'start': start_period, 'end': end_period}

            #Add to yaml listyaml
            yaml_list.append({'id': yearday_h_id, 'start': start_period, 'end': end_period})

    return timestep_full_year_dict, yaml_list

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
    _info = date_from_yearday.timetuple()
    weekday = _info[6]                # 0: Monday
    if weekday == 5 or weekday == 6:
        daytype = 1 # Holiday
    else:
        daytype = 0 # Working day
    return daytype

def get_season_yearday(yearday):
    """
    Gets the season from yearday.

    """
    winter1, winter2 = range(334, 365), range(0, 60)
    spring = range(59, 152)
    summer = range(151, 243)
    autumn = range(243, 334)

    if yearday in winter1 or yearday in winter2:
        season = 0 # Winter
    elif yearday in spring:
        season = 1
    elif yearday in summer:
        season = 2
    elif yearday in autumn:
        season = 3
    return season

def get_own_position(daytype, _season, hour_container, timesteps_own_selection):
    """ Get position in own container of yearly wrapper container"""

    # TODO: Improvea a lot....dirty

    season_lengths = []
    hours = 24

    # Get length of each period selected
    for i in timesteps_own_selection:
        start_date, end_date = i[0], i[1]
        list_dates = list(datetime_range(start=start_date, end=end_date))
        season_lengths.append(len(list_dates))
    #print("season_lengths: " + str(season_lengths))

    if _season == 0:
        if daytype == 0:

            # Get day
            yearday_position_data_array = 0 #1. Jan monday
            position_own_container = (season_lengths[0]-3) * 24 + hour_container
        else:
            yearday_position_data_array = 1
            position_own_container = season_lengths[0] * 24 + hour_container

    if _season == 1:
        if daytype == 0:
            yearday_position_data_array = 2 #1. Jan monday
            position_own_container = (season_lengths[1]-3) * 24 + hour_container
        else:
            yearday_position_data_array = 3
            position_own_container = season_lengths[1] * 24 + hour_container

    if _season == 2:
        if daytype == 0:
            yearday_position_data_array = 4 #1. Jan monday
            position_own_container = (season_lengths[2]-3) * 24 + hour_container
        else:
            yearday_position_data_array = 5
            position_own_container = season_lengths[2] * 24 + hour_container

    if _season == 3:
        if daytype == 0:
            yearday_position_data_array = 6 #1. Jan monday
            position_own_container = (season_lengths[3]-3) * 24 + hour_container
        else:
            yearday_position_data_array = 7
            position_own_container = season_lengths[3] * 24 + hour_container

    return position_own_container

def get_own_timesteps(date_list):
    """Create own timesteps. "Generets a list with all dates from a list containing start and end dates.

    Parameters
    ----------
    date_list : list
        List with start and end dates

    Returns
    -------
    timestep_dates : list
        List with all own timesteps (24 dates for every day)

    Notes
    -----
    If e.g. 2 days are found in the interval, 24 times the first and 24
    times the second day are added to a list.
    """
    # Create timestep dates
    hours = range(24)
    timestep_dates = []

    for i in date_list:
        start_date, end_date = i[0], i[1]
        list_dates = list(datetime_range(start=start_date, end=end_date))

        #Add to list
        for j in list_dates:

            #Append 24 time steps per day
            for _ in hours:
                timestep_dates.append(j)
    return timestep_dates

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

def read_data(data, path_main):
    """Reads in all csv files and stores them in a dictionary

    Parameters
    ----------
    path_main : str
        Path to main model folder
    path_dict : dict
        Dictionary containing all path to individual files

    Returns
    -------
    data : dict
        Dictionary containing read in data from csv files


    #Todo: Iterate every row and test if string or float value and then only write one write in function
    """
    path_dict = {'path_pop_reg_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_nr_regions.csv'),
                 'path_pop_reg_base': os.path.join(path_main, 'scenario_and_base_data/population_regions.csv'),
                 'path_dwtype_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),
                 'path_lookup_appliances':os.path.join(path_main, 'residential_model/lookup_appliances_HES.csv'),
                 'path_fuel_type_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_fuel_types.csv'),
                 'path_day_type_lu': os.path.join(path_main, 'residential_model/lookup_day_type.csv'),
                 'path_bd_e_load_profiles': os.path.join(path_main, 'residential_model/base_appliances_eletricity_load_profiles.csv'),
                 'path_base_data_fuel': os.path.join(path_main, 'scenario_and_base_data/base_data_fuel.csv'),
                 'path_temp_2015': os.path.join(path_main, 'residential_model/CSV_YEAR_2015.csv'),
                 'path_hourly_gas_shape': os.path.join(path_main, 'residential_model/residential_gas_hourly_shape.csv'),
                 'path_dwtype_dist': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_distribution.csv'),
                 'path_dwtype_age': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_age.csv'),
                 'path_dwtype_floorarea_dw_type': os.path.join(path_main, 'residential_model/data_residential_model_dwtype_floorarea.csv'),
                 'path_reg_floorarea': os.path.join(path_main, 'residential_model/data_residential_model_floorarea.csv'),
                 'path_reg_dw_nr': os.path.join(path_main, 'residential_model/data_residential_model_nr_dwellings.csv'),

                 'path_data_residential_by_fuel_end_uses': os.path.join(path_main, 'residential_model/data_residential_by_fuel_end_uses.csv'),
                 'path_lu_appliances_HES_matched': os.path.join(path_main, 'residential_model/lookup_appliances_HES_matched.csv')

                }

    data['path_dict'] = path_dict
    # TODO: Convert from percentage where necssary (einheitlich machen)

    # Read data
    reg_lu = read_csv_dict_no_header(path_dict['path_pop_reg_lu'])                # Region lookup table
    dwtype_lu = read_csv_dict_no_header(path_dict['path_dwtype_lu'])              # Dwelling types lookup table
    app_type_lu = read_csv(path_dict['path_lookup_appliances'])                   # Appliances types lookup table
    #fuel_type_lu = read_csv(path_dict['path_fuel_type_lu'])                       # Fuel type lookup
    fuel_type_lu = read_csv_dict_no_header(path_dict['path_fuel_type_lu'])                       # Fuel type lookup

    day_type_lu = read_csv(path_dict['path_day_type_lu'])                         # Day type lookup
    #season_lookup = read_csv(path_dict[]'path_season's_lookup'])                 # Season lookup

    reg_pop = read_csv_dict_no_header(path_dict['path_pop_reg_base'])             # Population data
    reg_pop_array = read_csv_float(path_dict['path_pop_reg_base'])               # Population data
    fuel_bd_data = read_csv_float(path_dict['path_base_data_fuel'])               # All disaggregated fuels for different regions
    csv_temp_2015 = read_csv(path_dict['path_temp_2015'])                         # csv_temp_2015 #TODO: Delete because loaded in shape_residential_heating_gas
    hourly_gas_shape = read_csv_float(path_dict['path_hourly_gas_shape'])         # Load hourly shape for gas from Robert Sansom #TODO: REmove because in shape_residential_heating_gas

    #path_dwtype_age = read_csv_float(['path_dwtype_age'])
    dwtype_distr = read_csv_nested_dict(path_dict['path_dwtype_dist'])
    dwtype_age_distr = read_csv_nested_dict(path_dict['path_dwtype_age'])
    dwtype_floorarea = read_csv_dict(path_dict['path_dwtype_floorarea_dw_type'])

    reg_floorarea = read_csv_dict_no_header(path_dict['path_reg_floorarea'])
    reg_dw_nr = read_csv_dict_no_header(path_dict['path_reg_dw_nr'])


    # Data new approach
    #print(path_dict['path_data_residential_by_fuel_end_uses']) #TODO: Maybe store end_uses_more directly
    data_residential_by_fuel_end_uses = read_csv_base_data_resid(path_dict['path_data_residential_by_fuel_end_uses']) # Yearly end use data


    lu_appliances_HES_matched = read_csv(path_dict['path_lu_appliances_HES_matched'])







    # ---------Insert into dictionary
    data['reg_lu'] = reg_lu
    data['dwtype_lu'] = dwtype_lu
    data['app_type_lu'] = app_type_lu
    data['fuel_type_lu'] = fuel_type_lu
    data['day_type_lu'] = day_type_lu

    data['reg_pop'] = reg_pop
    data['reg_pop_array'] = reg_pop_array
    data['fuel_bd_data'] = fuel_bd_data
    data['csv_temp_2015'] = csv_temp_2015
    data['hourly_gas_shape'] = hourly_gas_shape

    data['dwtype_distr'] = dwtype_distr
    data['dwtype_age_distr'] = dwtype_age_distr
    data['dwtype_floorarea'] = dwtype_floorarea
    data['reg_floorarea'] = reg_floorarea
    data['reg_dw_nr'] = reg_dw_nr

    data['data_residential_by_fuel_end_uses'] = data_residential_by_fuel_end_uses
    data['lu_appliances_HES_matched'] = lu_appliances_HES_matched

    # load shapes
    data['dict_shapes_end_use_h'] = {}
    data['dict_shapes_end_use_d'] = {}
    return data

def disaggregate_base_demand_for_reg(data, reg_data_assump_disaggreg):
    """This function disaggregates fuel demand based on region specific parameters"""

    regions = data['reg_lu']
    national_fuel = data['data_residential_by_fuel_end_uses'] # residential data
    dict_with_reg_fuel_data = {}

    # Iterate regions
    for i in regions:
        reg_disaggregate_factor_per_enduse_and_reg = 1 #TODO: create dict with disaggregation factors

        # Disaggregate fuel depending on end_use
        __ = {}
        for enduse in national_fuel:
            __[enduse] = national_fuel[enduse] * reg_disaggregate_factor_per_enduse_and_reg


        dict_with_reg_fuel_data[i] = __

    data['fueldata_disagg'] = dict_with_reg_fuel_data

    return data

def write_YAML(yaml_write, path_YAML):
    """Creates a YAML file with the timesteps IDs

    Parameters
    ----------
    yaml_write : int
        Whether a yaml file should be written or not (1 or 0)
    path_YAML : str
        Path to write out YAML file

    """
    if yaml_write:
        import yaml
        _, yaml_list = timesteps_full_year()  # Create timesteps for full year (wrapper-timesteps)

        with open(path_YAML, 'w') as outfile:
            yaml.dump(yaml_list, outfile, default_flow_style=False)
    return

def write_to_csv_will(data, reesult_dict, reg_lu):
    """ Write reults for energy supply model
    e.g.

    england, P0H, P1H, 139.42, 123.49

    """

    for fueltype in data['fuel_type_lu']:

        #TODO: Give relative path stored in data[pathdict]
        path = 'C:/Users/cenv0553/GIT/NISMODII/model_output/_fueltype_{}_hourly_results'.format(fueltype)

        yaml_list = []
        with open(path, 'w', newline='') as fp:
            a = csv.writer(fp, delimiter=',')
            data = []

            for reg in reesult_dict[fueltype]:
                region_name = reg_lu[reg]


                for _day in reesult_dict[fueltype][reg]:
                    for _hour in range(24):

                        start_id = "P{}H".format(_day * 24 + _hour)
                        end_id = "P{}H".format(_day * 24 + _hour + 1)
                        yaml_list.append({'region': region_name, 'start': start_id, 'end': end_id, 'value': reesult_dict[fueltype][reg][_day][_hour], 'units': 'CHECK GWH', 'year': 'XXXX'})

                        data.append([region_name, start_id, end_id, reesult_dict[fueltype][reg][_day][_hour]])

            a.writerows(data)

        #with open(path, 'w') as outfile:
        #    yaml.dump(yaml_list, outfile, default_flow_style=False)

def convert_to_array(fuel_type_p_ey):
    """Convert dictionary to array"""
    for i in fuel_type_p_ey:
        a = fuel_type_p_ey[i].items()
        a = list(a)
        fuel_type_p_ey[i] = np.array(a, dtype=float)
    return fuel_type_p_ey

def calc_peak_from_average(daily_loads):
    max_load = average_load / load_factor

    return max_load


"""A one-line summary that does not use variable names or the
    function name.
    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    long_var_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).
    This can have multiple paragraphs.
    You may include some math:

"""
