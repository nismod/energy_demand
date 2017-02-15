"""
This file stores all functions of main.py

"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325
print ("Loading main functions")

import csv
import sys
#import pandas as pd
from datetime import date, timedelta as td
import numpy as np


def read_csv(path_to_csv, _dt=()):
    """
    This function reads in CSV files and skip header row.

    Input:
    -path_to_csv              Path to CSV file
    -_dt              Array type: default: float, otherweise

    Output:
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


def create_timesteps_app(date_list, bd_app_elec, reg_lu, fuel_type_lu, app_type_lu):
    '''
    This function creates the simulation time steps for which the energy demand of the
    appliances is calculated.
    Then it selects energy demand from the yearls list for the simulation period

    Input:
    -date_list              List containing selection of dates the simulation should run
    -bd_app_elec            Base demand applications (electricity)
    -reg_lu                 Region look-up table
    -fuel_type_lu           Fuel type look-up table
    -app_type_lu            Appliance look-up table

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
    fuel_type = 0 #elec

    # Create timestep dates
    timestep_dates = []
    for i in date_list:
        start_date, end_date = i[0], i[1]
        list_dates = list(datetime_range(start=start_date, end=end_date))

        #Add to list
        for j in list_dates:

            #Append 24 time steps per day
            for _ in hours:
                timestep_dates.append(j)

    print("timestep_dates: " + str(len(timestep_dates)))
    timesteps = range(len(timestep_dates))

    # Initialise simulation array
    data_timesteps_elec = np.zeros((len(reg_lu), len(fuel_type_lu), len(timesteps), len(app_type_lu), len(hours)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lu)):
        print("Rrgion_NR: " + str(reg_nr))

        for t_step in timesteps:

            # Get appliances demand of region
            for j in list_dates:
                _info = j.timetuple()
                year_day_python = _info[7] - 1  # -1 because in _info yearday 1: 1. Jan

                # Collect absolute data from
                print("ADD: " + str(reg_nr) + str("  ") + str(year_day_python) + str(bd_app_elec[fuel_type][reg_nr][year_day_python].sum()))
                data_timesteps_elec[reg_nr][fuel_type][t_step] = bd_app_elec[fuel_type][reg_nr][year_day_python]

            break #Scrap remove
    
    return data_timesteps_elec

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
            appliance_typ
                hour
    '''
    # Initilaise array to store all values for a year
    year_days = range(365)
    month_nr = range(12)
    hours = range(24)
    year_raw_values = np.zeros((len(year_days), len(app_type_lu), len(hours)), dtype=float)

    # Initialise HES dictionary with every month and day-type
    hes_data = np.zeros((len(daytypee_lu), len(month_nr), len(app_type_lu), len(hours)), dtype=float)

    # Read in energy profiles of base_year
    raw_elec_data = read_csv(path_base_elec_load_profiles)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month = int(row[0])
        daytype = int(row[1])
        appliance_typ = int(row[2])
        k_header = 3    # Check if in excel data starts here

        # iterate over hour
        for hour in hours:
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000)) # [kWH electric] Converts the summed watt into kWH
            hes_data[daytype][month][appliance_typ][hour] = _value
            k_header += 1

    # Create list with all dates of a year
    start_date, end_date = date(base_year, 1, 1), date(base_year, 12, 31)
    list_dates = list(datetime_range(start=start_date, end=end_date))

    #print("Nr of dates: " + str(len(list_dates)))

    if len(list_dates) != 365:
        print ("ERROR: year has 366 day and not 365.... ")
        sys.exit()

    # Assign every date to the place in the array of the year
    for date_in_year in list_dates:
        _info = date_in_year.timetuple()
        month_python = _info[1] - 1       # - 1 because in _info: Month 1 = Jan
        year_day_python = _info[7] - 1    # - 1 because in _info: 1.Jan = 1
        weekday = _info[6]                # 0: Monday

        if weekday == 5 or weekday == 6:
            daytype = 1 # Holiday
        else:
            daytype = 0 # Working day

        _data = hes_data[daytype][month_python] # Get day from HES raw data array

        # Add values to yearly array
        year_raw_values[year_day_python] = _data

    # Calculate yearly total demand over all day years and all appliances
    total_y_demand = year_raw_values.sum()

    print("Sum absolute raw data: " + str(total_y_demand))

    # Calculate Shape of the eletrictiy distribution of the appliances by assigning percent values each
    appliances_shape = np.zeros((len(year_days), len(app_type_lu), len(hours)), dtype=float)
    appliances_shape = (1.0/total_y_demand) * year_raw_values

    print("Sum appliances_shape: " + str(appliances_shape.sum()))

    # Test for errors
    # ---------------
    _control = float(appliances_shape.sum())
    _control = round(_control, 4) # round for 4 digits

    if _control == 1.0:
        print("Shape is 100 % - good")
    else:
        print("Error: The Shape is not 100 %")
        print(_control)
        sys.exit()

    return appliances_shape

def datetime_range(start=None, end=None):
    '''
    This function calculates all dates between a star and end date.
    '''

    span = end - start
    for i in range(span.days + 1):
        yield start + td(days=i)

def bd_appliances(shape_app_elec, reg_lu, fuel_type_lu, bd_fuel_data):
    '''
    This function uses the generic shapes of the load profiles to hourly disaggregate energy demand
    for all regions and fuel types

    # So far only eletricity appliances

    out:
    -fuel_type_per_region_hourly        Fueltype per region per appliance per hour
        region
            fueltype
                year_days
                    appliances
                        hours
    '''
    fuelType_elec = 0 # Electrcitiy

    print("bd_fuel_data")
    print(bd_fuel_data)  # Electricity is bd_fuel_data[:,0]

    bd_fuel_data_electricity = bd_fuel_data[:, 1] # Base fuel per region
    print("bd_fuel_data_electricity")
    print(bd_fuel_data_electricity)
    print("---")
    print(len(fuel_type_lu))
    print(reg_lu)

    dim_appliance = shape_app_elec.shape
    print("dim_appliance: " + str(dim_appliance))

    # Initialise array
    fuel_type_per_region = np.zeros((len(fuel_type_lu), len(reg_lu)), dtype=float) # To store absolute demand values
    fuel_type_per_region_hourly = np.zeros((len(fuel_type_lu), len(reg_lu), dim_appliance[0], dim_appliance[1], dim_appliance[2]), dtype=float) # To store absolute demand values of hourly appliances

    # Add electricity base data

    for region_nr in range(len(reg_lu)):
        fuel_type_per_region[fuelType_elec][region_nr] = bd_fuel_data_electricity[region_nr]


    print("fuel_type_per_region")
    print(fuel_type_per_region)
    print("-------------")

    # Appliances per region
    for region_nr in range(len(reg_lu)):
        reg_demand = fuel_type_per_region[fuelType_elec][region_nr]
        print("Local tot demand " + str(reg_demand))
        reg_elec_appliance = shape_app_elec * reg_demand # Shape elec appliance * regional demand in [GWh]

        #print("shape insert: " + str(reg_elec_appliance.shape))
        #print("b ex: " + str(fuel_type_per_region_hourly[fuelType_elec][region_nr].shape))
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance

    return fuel_type_per_region_hourly


def writeToEnergySupply(path_out_csv):
    '''
    REads out results (which still need to be preared) to list of energy supply model.

    Input:
    -path_out_csv   Path to energy supply resulting table
    -in_data        Data input
    '''
    # Prepare data that as follows:

    # YEAR	SEASON	DAY	PERIOD	BusNumber	ElecLoad
    new_data = [[2015, 1, 1, 1, 1, 100], [2015, 1, 1, 1, 1, 21000], [2015, 1, 1, 1, 1, 2030000]]  # YEAR	SEASON	DAY	PERIOD	BusNumber	ElecLoad

    # Read existing CSV
    existing_data = read_csv(path_out_csv)
    print(existing_data)

    for i, j in zip(existing_data, new_data):
        i[5] = j[5]

    print("---")
    print(existing_data)

    with open(path_out_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for row in existing_data:
            writer.writerow(row)

    return
