"""
This file stores all functions of main.py

"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
print ("Loading main functions")

import csv
import sys
import traceback
import datetime
from datetime import date, timedelta as td
import numpy as np
from datetime import datetime  
from datetime import timedelta

def read_csv(path_to_csv, _dt=()):
    """
    This function reads in CSV files and skip header row.

    Arguments
    =========
    -path_to_csv            Path to CSV file
    -_dt                    Array type: default: float, otherweise

    Returns
    =========
    -elements_array         Array containing whole CSV file entries
    """
    with open(path_to_csv, 'r') as csvfile:              # Read CSV file
        list_elements = []
        read_lines = csv.reader(csvfile, delimiter=',')   # Read line
        _headings = next(read_lines) # Skip first row

        # Rows
        for row in read_lines:
            list_elements.append(row)

    if _dt == float:
        elements_array = np.array(list_elements, dtype=_dt)    # Convert list into array
    else:
        elements_array = np.array(list_elements)
    return elements_array

def get_dates_datelist(date_list):
    """This function generates a single list from a list with start and end dates
    and adds the same date into the list according to the number of hours in a day.

    Arguments
    =========
    -date_list      [dates] List containing start and end dates

    Returns
    =========
    -timestep-date  [dates] List containing all dates according to number of hours
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

def create_timesteps_app(date_list, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu):
    '''Creates the timesteps for which the energy demand of the appliances is calculated.
    Then base energy demand is added for each timestep read in from yearly demand aray.

    Arguments
    =========
    -date_list              [dates] List containing selection of dates the simulation should run
    -bd_app_elec            Base demand applications (electricity)
    -reg_lu                 Region look-up table
    -fuel_type_lu           Fuel type look-up table
    -app_type_lu            Appliance look-up table

    Returns
    =========
    -data_timesteps_elec    Timesteps containing appliances electricity data
        regions
            fuel_type
                timesteps
                    hours
                        applications

    '''
    # Region, Fuel
    hours = range(24)
    fuel_type = 0 #elec

    # Generate a list with all dates (the same date is added 24 times each because of 24 hours)
    timestep_dates = get_dates_datelist(date_list)

    # Nuber of timesteps containing all days and hours
    timesteps = range(len(timestep_dates))

    # Initialise simulation array
    h_XX = 1 # BEcause for every timstep only one hozrs
    data_timesteps_elec = np.zeros((len(fuel_type_lu), len(reg_lu), len(timesteps), h_XX, len(app_type_lu)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lu)):
        cnt_h = 0

        for t_step in timesteps:

            # Get appliances demand of region for every date of timeperiod
            _info = timestep_dates[t_step].timetuple() # Get date
            year_day_python = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

            # Collect absolute data from
            data_timesteps_elec[fuel_type][reg_nr][t_step] = bd_app_elec[fuel_type][reg_nr][year_day_python][cnt_h] # Iterate over roew #TODO CHECK

            cnt_h += 1
            if cnt_h == 23:
                cnt_h = 0

    return data_timesteps_elec

def create_timesteps_hd(date_list, bd_hd_gas, reg_lu, fuel_type_lu): # TODO: HIER GIBTS NOCH ERROR
    '''
    This function creates the simulation time steps for which the heating energy is calculated.
    Then it selects energy demand from the yearl list for the simulation period.

    Input:
    -date_list              List containing selection of dates the simulation should run
    -bd_hd_gas              Base demand heating (gas)
    -reg_lu                 Region look-up table
    -fuel_type_lu           Fuel type look-up table

    Output:
    -data_timesteps_elec    Timesteps containing appliances electricity data
        regions
            fuel_type
                timesteps
                    applications
                        hours
    '''
    # Region, Fuel
    hours = range(24)
    fuel_type = 1 #gas

    # Generate a list with all dates (the same date is added 24 times each because of 24 hours)
    timestep_dates = get_dates_datelist(date_list)

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
            year_day_python = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

            #print("DAY SN: " + str(year_day_python) + str("  ") + str(sum(bd_hd_gas[fuel_type][reg_nr][year_day_python])))

            # Get data and copy hour
            data_timesteps_hd_gas[fuel_type][reg_nr][t_step][cnt_h] = bd_hd_gas[fuel_type][reg_nr][year_day_python][cnt_h]

            cnt_h += 1
            if cnt_h == 23:
                cnt_h = 0

    return data_timesteps_hd_gas


def shape_bd_app(path_base_elec_load_profiles, daytypee_lu, app_type_lu, base_year):
    '''
    This function reads in the HES eletricity load profiles
    of the base year and stores them in form of an array.
    First the absolute values are stored in a HES dictionary
    for the different month and day-types. Then the total
    demand of the year is calculated and all array entries
    calculated as percentage of the total demand.

    #TODO: expand for different regions, different dwelling types, fuels...

    Input:
    -path_base_elec_load_profiles   Path to .csv file with HSE data
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
    # Initilaise array to store all values for a year
    year_days, month_nr, hours = range(365), range(12), range(24)
    year_raw_values = np.zeros((len(year_days), len(hours), len(app_type_lu)), dtype=float)

    # Initialise HES dictionary with every month and day-type
    hes_data = np.zeros((len(daytypee_lu), len(month_nr), len(hours), len(app_type_lu)), dtype=float)

    # Read in energy profiles of base_year
    raw_elec_data = read_csv(path_base_elec_load_profiles)

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
        year_day_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        daytype = get_weekday_type(date_in_year)

        _data = hes_data[daytype][month_python] # Get day from HES raw data array

        # Add values to yearly array
        year_raw_values[year_day_python] = _data

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

def datetime_range(start=None, end=None):
    '''
    This function calculates all dates between a star and end date.
    '''

    span = end - start
    for i in range(span.days + 1):
        yield start + td(days=i)

def bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, fuel_bd_data):
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
    print("DIM: " + str(dim_appliance))
    # Initialise array
    fuel_type_per_region = np.zeros((len(fuel_type_lu), len(reg_lu)), dtype=float) # To store absolute demand values
    fuel_type_per_region_hourly = np.zeros((len(fuel_type_lu), len(reg_lu), dim_appliance[0], dim_appliance[1], dim_appliance[2]), dtype=float) # To store absolute demand values of hourly appliances

    # Add electricity base data
    for region_nr in range(len(reg_lu)):
        fuel_type_per_region[fuelType_elec][region_nr] = fuel_bd_data_electricity[region_nr]

    # Appliances per region
    for region_nr in range(len(reg_lu)):
        reg_demand = fuel_type_per_region[fuelType_elec][region_nr]
        reg_elec_appliance = shape_app_elec * reg_demand # Shape elec appliance * regional demand in [GWh]
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance

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

def writeToEnergySupply(path_out_csv, fueltype, in_data):
    '''
    REads out results (which still need to be preared) to list of energy supply model.

    Input:
    -path_out_csv   Path to energy supply resulting table
    -in_data        Data input

    Output:
    -               Print results
    '''
    # Prepare data that as follows:
    outData = []

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
    existing_data = read_csv(path_out_csv)
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
        year_day_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        weekday = _info[6]                # 0: Monday

        # Distribute daily deamd into hourly demand
        if weekday == 5 or weekday == 6:
            _data = hourly_gas_shape_wkend * heating_demand_correlation
            hd_data[year_day_python] = _data  # DATA ARRAY
        else:
            _data = hourly_gas_shape_wkday * heating_demand_correlation
            hd_data[year_day_python] = _data  # DATA ARRAY

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

def bd_hd_gas(shape_hd_gas, reg_lu, fuel_type_lu, fuel_bd_data):
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
    """ Conversion of ktoe to gwh according to
    https://www.iea.org/statistics/resources/unitconverter/

    Arguments
    =========
    -data_ktoe  [float] Energy demand in ktoe

    Returns
    =========
    -data_gwh   [float] Energy demand in GWh
    """

    data_gwh = data_ktoe * 11.6300000

    return data_gwh


def timesteps_full_year():
    """Dictionary with all hourly time periods of the base year (total 8760).

    Arguments
    =========

    Returns
    =========
    -timestep_full_year_dict
    """
    full_year_date = [date(2015, 1, 1), date(2015, 12, 31)] # Base Year
    start_date, end_date = full_year_date[0], full_year_date[1]
    list_dates = list(datetime_range(start=start_date, end=end_date)) # List with every date in a year

    hours, days = range(24), range(365)
    timestep_full_year_dict = {}
    timestep_dates = []

    #Add to list
    h_year_id = 0
    for day_date in list_dates:
        _info = day_date.timetuple() # Get date
        day_of_that_year = _info[7] - 1             # -1 because in _info yearday 1: 1. Jan

        h_id = 0
        # Interate hours
        for _ in hours:
            #Create ID (yearday_hour of day)
            yearday_h_id = str(str(day_of_that_year) + str("_") + str(h_id))
            start_period = str("P" + str(h_year_id) + str("H"))
            end_period = str("P" + str(h_year_id + 1) + str("H"))

            # Add to dict
            timestep_full_year_dict[yearday_h_id] = {'start': start_period, 'end': end_period}

            h_id += 1
            h_year_id += 1

    return timestep_full_year_dict

def get_weekday_type(date_from_yearday):
    """Gets the weekday of a date

    input:
    -date_from_yearday      date

    output:
    -daytype: 1: holiday, 0; working day
    """
    _info = date_from_yearday.timetuple()
    weekday = _info[6]                # 0: Monday
    if weekday == 5 or weekday == 6:
        daytype = 1 # Holiday
    else:
        daytype = 0 # Working day
    return daytype

def get_season(yearday):
    """
    Gets the season from yearday.

    """
    winter1, winter2 = range(334, 365), range(0, 60)
    spring = range(59, 152)
    summer = range(151, 243)
    autumn = range(243, 334)

    if yearday in winter1 or yearday in winter2:
        season = 0 # Winter
    if yearday in spring:
        season = 1
    if yearday in summer:
        season = 2
    if yearday in autumn:
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

def get_wrapper_result_nested_dict(fuel_type_lu, reg_pop, timesteps):
    """ Generates nested dictionary for providing results to smif
    """
    result_dict = {}
    for i in range(len(fuel_type_lu)):
        result_dict[i] = {}
        for j in range(len(reg_pop)):
            result_dict[i][j] = {}
            for k in timesteps:
                result_dict[i][j][k] = {}
    return result_dict



def add_electricity_demand(e_app_bd, fuel_type_lu, reg_pop, fuel_type, timesteps, result_dict, timesteps_own_selection):
    """Add data to wrapper timesteps

    """
    import datetime
    from datetime import date

    # Iteratue fuels
    for _ftyp in range(len(fuel_type_lu)):

        if _ftyp is not fuel_type:
            continue

        for region_nr in range(len(reg_pop)):
            year_hour = 0
            for timestep in timesteps: #Iterate over timesteps of full year
                timestep_id = str(timestep)
                _yearday = int(timestep.split("_")[0])   # Yearday
                _h = int(timestep.split("_")[1])         # Hour
                start_period, end_period = timesteps[timestep]['start'], timesteps[timestep]['end']

                # Assign correct data from selection
                # Get season
                _season = get_season(_yearday)

                # Get daytype
                _yeardayReal = _yearday + 1 #Plus one from python
                date_from_yearday = datetime.datetime.strptime('2015 ' + str(_yeardayReal), '%Y %j')
                daytype = get_weekday_type(date_from_yearday)

                # Get position in own timesteps
                hour_own_container = year_hour - _yearday * 24 #Hour of the day
                day_own_container_position = get_own_position(daytype, _season, hour_own_container, timesteps_own_selection) # AS input should

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
