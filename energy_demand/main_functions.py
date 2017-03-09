"""This file stores all functions of main.py"""

import sys
import os
import csv
import traceback
import datetime
from datetime import date
from datetime import timedelta as td
import numpy as np
print ("Loading main functions")
# pylint: disable=I0011,C0321,C0301,C0103, C0325

#from datetime import date, timedelta as td
#from datetime import datetime
#import datetime

def load_data(data_ext):
    """All base data no provided externally are loaded

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------

    Returns
    -------
    data : list
        Returns a list where all datas are wrapped together.

    Notes
    -----

    """
    #path_main = '../data'
    path_main = r'C:/Users/cenv0553/GIT/NISMODII/data/' # Remove

    # ------Read in all data from csv files-------------------
    data, path_dict = read_data(path_main)

    # ------Generate generic load profiles (shapes) [in %]-------------------
    shape_app_elec, shape_hd_gas = get_load_curve_shapes(path_dict['path_bd_e_load_profiles'], data['day_type_lu'], data['app_type_lu'], data_ext['glob_var'], data['csv_temp_2015'], data['hourly_gas_shape'])
    data['shape_app_elec'] = shape_app_elec # add to data dict

    # ------Base demand for the base year for all modelled elements-------------------

    # Base demand of appliances over a full year (electricity)
    bd_app_elec = get_bd_appliances(shape_app_elec, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])
    data['bd_app_elec'] = bd_app_elec # add to data dict

    # Base demand of heating demand (gas)
    bd_hd_gas = get_bd_hd_gas(shape_hd_gas, data['reg_lu'], data['fuel_type_lu'], data['fuel_bd_data'])
    data['bd_hd_gas'] = bd_hd_gas # add to data dict

    print("---Summary Base Demand")
    print("Base Fuel elec appliances total per year (uk):             " + str(data['fuel_bd_data'][:, 1].sum()))
    print("Base Fuel elec appliances total per year (region, hourly): " + str(bd_app_elec.sum()))
    print("  ")
    print("Base gas hd appliances total per year (uk):                " + str(data['fuel_bd_data'][:, 2].sum()))
    print("Base gas hd appliancestotal per year (region, hourly):     " + str(bd_hd_gas.sum()))

    # ---------------------------------------------------------------
    # Generate simulation timesteps and assing base demand (e.g. 1 week in each season, 24 hours)
    # ---------------------------------------------------------------
    timesteps_own_selection = (
        [date(data_ext['glob_var']['base_year'], 1, 12), date(data_ext['glob_var']['base_year'], 1, 18)],     # Week Spring (Jan) Week 03  range(334 : 364) and 0:58
        [date(data_ext['glob_var']['base_year'], 4, 13), date(data_ext['glob_var']['base_year'], 4, 19)],     # Week Summer (April) Week 16  range(59:150)
        [date(data_ext['glob_var']['base_year'], 7, 13), date(data_ext['glob_var']['base_year'], 7, 19)],     # Week Fall (July) Week 25 range(151:242)
        [date(data_ext['glob_var']['base_year'], 10, 12), date(data_ext['glob_var']['base_year'], 10, 18)],   # Week Winter (October) Week 42 range(243:333)
        )
    data['timesteps_own_selection'] = timesteps_own_selection # add to data dict

    # Create own timesteps
    own_timesteps = get_own_timesteps(timesteps_own_selection)

    # Populate timesteps base year data (appliances, electricity)
    timesteps_app_bd = create_timesteps_app(0, timesteps_own_selection, bd_app_elec, data['reg_lu'], data['fuel_type_lu'], data['app_type_lu'], own_timesteps) # [GWh]
    data['timesteps_app_bd'] = timesteps_app_bd # add to data dict

    # Populate timesteps base year data (heating demand, ga)
    timesteps_hd_bd = create_timesteps_hd(1, timesteps_own_selection, bd_hd_gas, data['reg_lu'], data['fuel_type_lu'], own_timesteps) # [GWh]
    data['timesteps_hd_bd'] = timesteps_hd_bd # add to data dict

    print("----------------------Statistics--------------------")
    print("Number of timesteps appliances:          " + str(len(timesteps_app_bd[0][0])))
    print("Number of timestpes heating demand:      " + str(len(timesteps_hd_bd[1][0])))
    print(" ")
    print("Sum Appliances simulation period:        " + str(timesteps_app_bd.sum()))
    print("Sum heating emand simulation period:     " + str(timesteps_hd_bd.sum()))
    print(" ")

    return data


def init_dict_energy_supply(fuel_type_lu, reg_pop, timesteps):
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
        for j in range(len(reg_pop)): #TODO: use region lu
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

def create_timesteps_app(fuel_type, date_list, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu, timestep_dates):
    """Creates the timesteps for which the energy demand of the appliances is calculated.
    Then base energy demand is added for each timestep read in from yearly demand aray.

    Parameters
    ----------
    fuel_type : int
        Fuel type
    date_list : list
        Contaings lists with start and end dates
    bd_app_elec : list
        Base demand applications (electricity)
    reg_lu : list
        Region look-up table
    fuel_type_lu : list
        Fuel type look-up table
        ...

    Returns
    -------
    data_timesteps_elec : array
        Timesteps containing appliances electricity data
            regions
                fuel_type
                    timesteps
                        hours
                            applications
    Notes
    -----

    """

    # Nuber of timesteps containing all days and hours
    timesteps = range(len(timestep_dates))

    # Initialise simulation array
    h_XX = 1 # BEcause for every timstep only one hozrs
    data_timesteps_elec = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), h_XX, len(app_type_lu)), dtype=float)
    #data_timesteps_elec = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), len(hours), len(app_type_lu)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lu)):
        cnt_h = 0

        for t_step in timesteps:

            # Get appliances demand of region for every date of timeperiod
            _info = timestep_dates[t_step].timetuple() # Get date
            yearday_python = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

            # Collect absolute data from
            #print("Add data to timstep container:    Timestep " + str(t_step) + str(" cnt_h: ") + str(cnt_h) + str("  Region_Nr") + str(reg_nr) + str("  Yearday") + str(yearday_python) + ("   ") + str(bd_app_elec[fuel_type][reg_nr][yearday_python][:,cnt_h].sum()))
            #data_timesteps_elec[fuel_type][reg_nr][t_step][:, cnt_h] = bd_app_elec[fuel_type][reg_nr][yearday_python][:, cnt_h] # Iterate over roew
            #print("A:  + " + str(data_timesteps_elec[fuel_type][reg_nr][t_step])) #[cnt_h]))
            #print("B:  + " + str(bd_app_elec[fuel_type][reg_nr][yearday_python][cnt_h]))

            #print(data_timesteps_elec[fuel_type][reg_nr][t_step].shape)
            #print(bd_app_elec[fuel_type][reg_nr][yearday_python][cnt_h].shape)
            data_timesteps_elec[fuel_type][reg_nr][t_step] = bd_app_elec[fuel_type][reg_nr][yearday_python][cnt_h] # Iterate over roew #TODO CHECK
            #print(data_timesteps_elec[fuel_type][reg_nr][t_step][cnt_h])
            #print(data_timesteps_elec[fuel_type][reg_nr][t_step])

            cnt_h += 1
            if cnt_h == 23:
                cnt_h = 0

    return data_timesteps_elec

def create_timesteps_hd(fuel_type, date_list, bd_hd_gas, reg_lu, fuel_type_lu, timestep_dates): # TODO: HIER GIBTS NOCH ERROR
    """This function creates the simulation time steps for which the heating energy is calculated.
    Then it selects energy demand from the yearl list for the simulation period.

    Parameters
    ----------
    date_list : list
        List containing selection of dates the simulation should run
    bd_hd_gas :
        Base demand heating (gas)
    reg_lu : array
        Region look-up table
    fuel_type_lu : array
        Fuel type look-up table

    Returns
    -------
    data_timesteps_hd_gas :
        Returns a nested dictionary for energy supply model. (fueltype/region/timeID)


        -data_timesteps_elec    Timesteps containing appliances electricity data
            regions
                fuel_type
                    timesteps
                        applications
                            hours
    Notes
    -----
    notes
    """
    # Region
    hours = range(24)

    # Number of timesteps
    timesteps = range(len(timestep_dates))

    # Initialise simulation array
    data_timesteps_hd_gas = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), len(hours)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lu)):

        cnt_h = 0
        for t_step in timesteps:

            # Get appliances demand of region for every date of timeperiod
            _info = timestep_dates[t_step].timetuple() # Get date
            yearday_python = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

            #print("DAY SN: " + str(yearday_python) + str("  ") + str(sum(bd_hd_gas[fuel_type][reg_nr][yearday_python])))

            # Get data and copy hour
            data_timesteps_hd_gas[fuel_type][reg_nr][t_step][cnt_h] = bd_hd_gas[fuel_type][reg_nr][yearday_python][cnt_h]

            cnt_h += 1
            if cnt_h == 23:
                cnt_h = 0

    return data_timesteps_hd_gas


def shape_bd_app(path_bd_e_load_profiles, daytypee_lu, app_type_lu, base_year):
    '''
    This function reads in the HES eletricity load profiles
    of the base year and stores them in form of an array.
    First the absolute values are stored in a HES dictionary
    for the different month and day-types. Then the total
    demand of the year is calculated and all array entries
    calculated as percentage of the total demand.

    #TODO: expand for different regions, different dwelling types, fuels...

    Input:
    -path_bd_e_load_profiles   Path to .csv file with HSE data
    -season_lookup                  Lookup dictionary with seasons
    -daytypee_lu                    Lookup dictionary with type of days
    -app_type_lu              Looup dictionary containing all appliances
    -base_year                      Base year

    Output:
    -appliances_shape               [%] Array containing the shape of appliances
                                    for every day in the base year
                                    Within each month, the same load curves are
                                    used for every working/holiday day.
        year_days of base year
            hour
                appliance_typ
    '''
    # --------Read in HES data----------
    # Initilaise array to store all values for a year
    year_days, month_nr, hours = range(365), range(12), range(24)
    year_raw_values = np.zeros((len(year_days), len(hours), len(app_type_lu)), dtype=float)

    # Initialise HES dictionary with every month and day-type
    hes_data = np.zeros((len(daytypee_lu), len(month_nr), len(hours), len(app_type_lu)), dtype=float)

    # Read in energy profiles of base_year
    raw_elec_data = read_csv(path_bd_e_load_profiles)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month, daytype, appliance_typ = int(row[0]), int(row[1]), int(row[2])
        k_header = 3    # TODO: Check if in excel data starts here

        # iterate over hour
        for hour in hours:
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000)) # [kWH electric] Converts the summed watt into kWH
            hes_data[daytype][month][hour][appliance_typ] = _value
            k_header += 1

    # Create list with all dates of a whole year
    start_date, end_date = date(base_year, 1, 1), date(base_year, 12, 31)
    list_dates = list(datetime_range(start=start_date, end=end_date))

    # Error because of leap year
    if len(list_dates) != 365:
        a = "Error: Leap year has 366 day and not 365.... "
        raise Exception(a)

    # Assign every date to the place in the array of the year
    for date_in_year in list_dates:
        _info = date_in_year.timetuple()
        month_python = _info[1] - 1       # - 1 because in _info: Month 1 = Jan
        yearday_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        daytype = get_weekday_type(date_in_year)

        _data = hes_data[daytype][month_python] # Get day from HES raw data array

        # Add values to yearly array
        year_raw_values[yearday_python] = _data

    # Calculate yearly total demand over all day years and all appliances
    total_y_demand = year_raw_values.sum()

    # Calculate Shape of the eletrictiy distribution of the appliances by assigning percent values each
    appliances_shape = np.zeros((len(year_days), len(hours), len(app_type_lu)), dtype=float)
    appliances_shape = (1.0/total_y_demand) * year_raw_values

    # Test for errors
    # ---------------
    try:
        _control = float(appliances_shape.sum())
        _control = round(_control, 4) # round for 4 digits
        if _control == 1.0:
            print("Sum of shape is 100 % - good")
        else:
            _err = "Error: The shape calculation is not 100%. Something went wrong... "
            raise Exception(_err)
    except _err:
        _val = sys.exc_info()
        print (_val)
        sys.exit()

    return appliances_shape

def get_bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, fuel_bd_data):
    '''
    This function uses the generic shapes of the load profiles to hourly disaggregate energy demand
    for all regions and fuel types

    # So far only eletricity appliances

    out:
    -fuel_type_per_region_hourly        Fueltype per region per appliance per hour
        fueltype
            region
                year_days
                    appliances
                        hours
    '''
    fuelType_elec = 0 # Electrcitiy
    fuel_bd_data_electricity = fuel_bd_data[:, 1] # Base fuel per region

    dim_appliance = shape_app_elec.shape

    # Initialise array
    fuel_type_per_region = np.zeros((len(fuel_type_lu), len(reg_lu)), dtype=float) # To store absolute demand values
    fuel_type_per_region_hourly = np.zeros((len(fuel_type_lu), len(reg_lu), dim_appliance[0], dim_appliance[1], dim_appliance[2]), dtype=float) # To store absolute demand values of hourly appliances

    '''# Add electricity base data
    for region_nr in range(len(reg_lu)):
        fuel_type_per_region[fuelType_elec][region_nr] = fuel_bd_data_electricity[region_nr]

    # Appliances per region
    for region_nr in range(len(reg_lu)):
        reg_demand = fuel_type_per_region[fuelType_elec][region_nr]
        reg_elec_appliance = shape_app_elec * reg_demand # Shape elec appliance * regional demand in [GWh]
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance
    '''
    #'''
    # Add electricity base data per region
    for region_nr in range(len(reg_lu)):

        reg_demand = fuel_bd_data_electricity[region_nr]
        reg_elec_appliance = shape_app_elec * reg_demand # Shape elec appliance * regional demand in [GWh]
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance
    #'''

    # Test for errors
    try:
        _control = round(float(fuel_type_per_region_hourly.sum()), 4) # Sum of input energy data, rounded to 4 digits
        _control2 = round(float(fuel_bd_data_electricity.sum()), 4)   # Sum of output energy data, rounded to 4 digits

        if _control == _control2:
            print("Input total energy demand has been correctly disaggregated.")
        else:
            _err = "Error: Something with the disaggregation went wrong.. "
            raise Exception(_err)

    except _err:
        _val = sys.exc_info()
        _, _value, _tb = sys.exc_info()
        print("Errors from function db_appliances:")
        traceback.print_tb(_tb)
        print (_value)
        sys.exit()

    return fuel_type_per_region_hourly

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

    full_year_date = [date(2015, 1, 1), date(2015, 12, 31)] # Base Year
    start_date, end_date = full_year_date[0], full_year_date[1]
    list_dates = list(datetime_range(start=start_date, end=end_date)) # List with every date in a year

    hours, days = range(24), range(365)
    yaml_list = [] ## l = [{'id': value, 'start': 'p', 'end': 'P2',   }

    timestep_full_year_dict = {} #  YEARDAY_H
    timestep_dates = []

    #Add to list
    #h_year_id = 0
    for day_date in list_dates:
        _info = day_date.timetuple() # Get date
        day_of_that_year = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

        h_id = 0
        # Interate hours
        for _ in hours:
            #Create ID (yearday_hour of day)
            start_period = "P{}H".format(day_of_that_year * 24 + h_id)
            end_period = "P{}H".format(day_of_that_year * 24 + h_id + 1)

            yearday_h_id = str(str(day_of_that_year) + str("_") + str(h_id))

            #start_period = str("P" + str(h_year_id) + str("H"))
            #end_period = str("P" + str(h_year_id + 1) + str("H"))

            # Add to dict
            timestep_full_year_dict[yearday_h_id] = {'start': start_period, 'end': end_period}

            h_id += 1
            #h_year_id += 1

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

def add_demand_result_dict(fuel_type, e_app_bd, fuel_type_lu, reg_pop, timesteps, result_dict, timesteps_own_selection):
    """Add data to wrapper timesteps

    """

    # Iteratue fuels
    for _ftyp in range(len(fuel_type_lu)):

        if _ftyp is not fuel_type: # IF other fueltype
            continue

        for region_nr in range(len(reg_pop)):
            year_hour = 0
            for timestep in timesteps: #Iterate over timesteps of full year
                timestep_id = str(timestep)
                _yearday = int(timestep.split("_")[0])   # Yearday
                _h = int(timestep.split("_")[1])         # Hour
                #start_period, end_period = timesteps[timestep]['start'], timesteps[timestep]['end']

                # Assign correct data from selection
                # Get season
                _season = get_season_yearday(_yearday)

                # Get daytype
                _yeardayReal = _yearday + 1 #Plus one from python
                date_from_yearday = datetime.datetime.strptime('2015 ' + str(_yeardayReal), '%Y %j')
                daytype = get_weekday_type(date_from_yearday)
                #daytype = 1

                # Get position in own timesteps
                hour_own_container = year_hour - _yearday * 24 #Hour of the day
                day_own_container_position = get_own_position(daytype, _season, hour_own_container, timesteps_own_selection) # AS input should
                #day_own_container_position = 1
                #print("day_own_container: " + str(day_own_container))

                #result_array[fuel_type][region_nr][timestep_id] = e_app_bd[fuel_elec][region_nr][_h].sum() # List with data out
                #result_dict[fuel_type][region_nr][timestep_id] = e_app_bd[fuel_elec][region_nr][_yearday][_h].sum()

                # DUMMY DATA
                #print("...---...")
                #print(fuel_type)
                #print(region_nr)
                #print(day_own_container)
                #print(_h) # Is missing!
                #print("EE:G " + str(e_app_bd[fuel_type][region_nr][day_own_container]))
                #print("---")
                result_dict[fuel_type][region_nr][timestep_id] = e_app_bd[fuel_type][region_nr][day_own_container_position].sum()  # Problem: Timesteps in are in fuel, region, TIMESTEP, appliances, hours
                year_hour += 1

    return result_dict

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


def get_load_curve_shapes(path_bd_e_load_profiles, day_type_lu, app_type_lu, glob_var, csv_temp_2015, hourly_gas_shape):
    """ Gets load curve shapes

    Parameters
    ----------
     : dict
        Dictionary containing paths

    Returns
    -------
    shape_app_elec : array
        Array with shape of electricity demand of appliances (full year)
    shape_hd_gas : array
        Array with shape of heating demand (full year)

    Info
    -------
    More Info
    """
    # Shape of base year for a full year for appliances (electricity) from HES data [%]
    shape_app_elec = shape_bd_app(path_bd_e_load_profiles, day_type_lu, app_type_lu, glob_var['base_year'])

    # Shape of base year for a full year for heating demand derived from XX [%]
    shape_hd_gas = shape_bd_hd(csv_temp_2015, hourly_gas_shape)

    return  shape_app_elec, shape_hd_gas

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
            cnt = 0
            # Iterate row entries
            for i in row:

                # Test if float or string
                try:
                    out_dict[_headings[cnt]] = float(i)
                except ValueError:
                    out_dict[_headings[cnt]] = str(i)

                #if isinstance(float(i), str):
                cnt += 1

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

def read_data(path_main):
    """Reads in all csv files and stores them in a dictionary

    Parameters
    ----------
    path_main : str
        Path to main model folder

    Returns
    -------
    data : dict
        Dictionary containing read in data from csv files
    path_dict : dict
        Dictionary containing all path to individual files

    #Todo: Iterate every row and test if string or float value and then only write one write in function
    """
    path_dict = {'path_pop_reg_lu': os.path.join(path_main, 'scenario_and_base_data/lookup_nr_regions.csv'),
                 'path_pop_reg_base': os.path.join(path_main, 'scenario_and_base_data/population_regions.csv'),
                 'path_dwtype_lu': os.path.join(path_main, 'residential_model/lookup_dwelling_type.csv'),
                 'path_lookup_appliances':os.path.join(path_main, 'residential_model/lookup_appliances.csv'),
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
                 'path_reg_dw_nr': os.path.join(path_main, 'residential_model/data_residential_model_nr_dwellings.csv')
                }

    data = {}

    # TODO: Convert from percentage where necssary (einheitlich machen)

    # Read data
    reg_lu = read_csv_dict_no_header(path_dict['path_pop_reg_lu'])                # Region lookup table
    dwtype_lu = read_csv_dict_no_header(path_dict['path_dwtype_lu'])              # Dwelling types lookup table
    app_type_lu = read_csv(path_dict['path_lookup_appliances'])                   # Appliances types lookup table
    fuel_type_lu = read_csv(path_dict['path_fuel_type_lu'])                       # Fuel type lookup
    day_type_lu = read_csv(path_dict['path_day_type_lu'])                         # Day type lookup
    #season_lookup = read_csv(path_dict[]'path_season's_lookup'])                 # Season lookup

    reg_pop = read_csv_dict_no_header(path_dict['path_pop_reg_base'])             # Population data
    reg_pop_array = read_csv_float(path_dict['path_pop_reg_base'])             # Population data
    fuel_bd_data = read_csv_float(path_dict['path_base_data_fuel'])               # All disaggregated fuels for different regions
    csv_temp_2015 = read_csv(path_dict['path_temp_2015'])                         # csv_temp_2015
    hourly_gas_shape = read_csv_float(path_dict['path_hourly_gas_shape'])         # Load hourly shape for gas from Robert Sansom

    #path_dwtype_age = read_csv_float(['path_dwtype_age'])
    dwtype_distr = read_csv_nested_dict(path_dict['path_dwtype_dist'])
    dwtype_age_distr = read_csv_nested_dict(path_dict['path_dwtype_age'])
    dwtype_floorarea = read_csv_dict(path_dict['path_dwtype_floorarea_dw_type'])

    reg_floorarea = read_csv_dict_no_header(path_dict['path_reg_floorarea'])
    reg_dw_nr = read_csv_dict_no_header(path_dict['path_reg_dw_nr'])













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

    return data, path_dict

def add_to_data(data, pop_data_external): # Convert to array, store in data
    """ All all data received externally to main data dictionars. Convert also to array"""

    # Add population data
    reg_pop_array = {}
    for pop_year in pop_data_external:

        _t = pop_data_external[pop_year].items()
        l = []
        for i in _t:
            l.append(i)
        reg_pop_array[pop_year] = np.array(l, dtype=float)
    data['reg_pop_external_array'] = reg_pop_array
        #data['reg_pop_external'] = pop_data_external

        #print(data['reg_pop'][0])
        #print(isinstance(data['reg_pop'][0], int))
        #prin("kk")

    # Add other data
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


def write_to_csv_will(reesult_dict, reg_lu):
    """ Write reults for energy supply model
    e.g.

    england, P0H, P1H, 139.42, 123.49

    """

    path_csvs = ['C:/Users/cenv0553/GIT/NISMODII/model_output/will_file_elec.csv', 'C:/Users/cenv0553/GIT/NISMODII/model_output/will_file_gas.csv']
    cnt = 0
    for path in path_csvs:
        print("path: " + str(path))
        #yaml_list = []
        with open(path, 'w', newline='') as fp:

            a = csv.writer(fp, delimiter=',')
            data = []
            #for i in range(len(reesult_dict)): # Iterate over fuel type

            for reg in reesult_dict[cnt]:
                print("Region: " + str(reg))
                region_name = reg_lu[reg]

                # iterate timesteps
                for ts in reesult_dict[cnt][reg]:
                    _day = int(ts.split('_')[0])
                    _hour = int(ts.split('_')[1])

                    start_id = "P{}H".format(_day * 24 + _hour)
                    end_id = "P{}H".format(_day * 24 + _hour + 1)

                    #yaml_list.append({'region': region_name, 'start': _start, 'end': _end, 'value': reesult_dict[i][reg][ts], 'units': 'GWh', 'year': 'XXXX'})
                    data.append([region_name, start_id, end_id, reesult_dict[cnt][reg][ts]])

            a.writerows(data)
        cnt += 1

        #with open(path, 'w') as outfile:
        #    yaml.dump(yaml_list, outfile, default_flow_style=False)

'''
def calc_daily_load_factor(daily_loads):
    """Calculates load factor of a day

    Parameters
    ----------
    daily_loads : ??
        Load for every hours

    Returns
    -------
    load_factor : float
        Daily load factor
    """
    sum_load, max_load = 0, 0

    # Iterate hours to get max and average demand
    for i in daily_loads:
        h_load = ..
        sum_load += ..

        if h_load > max_load:
            max_load = h_load
    
    average_load = sum_load / len(daily_loads)

    load_factor = average_load / max_load
    

    return load_factor
'''

def calc_peak_from_average(daily_loads):
    
    # 
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