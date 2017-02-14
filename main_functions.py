# This file stores all functions of main.py
print ("Loading main functions")

import csv
import sys
#import pandas as pd
import datetime
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


def generate_sim_period_appliances(date_list, time_steps, bd_appliances_elec, reg_lookup, fuel_type_lookup, appliance_type_lu):
    '''
    This function creates the simulation time steps for which the energy demand is calculated.
    Then it selects energy demand from the yearls list for the simulation period


    '''
    # Region, Fuel
    hours = range(24)
    fuel_type = 0 #elec

    # Create timestep dates
    time_step_dates = []
    for i in date_list:
        print("i: " + str(i))
        start_date, end_date = i[0], i[1]
        list_dates = list(datetime_range(start=start_date, end=end_date))

        #Add to list
        for j in list_dates:
            
            #Append 24 time steps per day
            for k in hours:
                time_step_dates.append(j)
    
    print("time_step_dates: " + str(len(time_step_dates)))



    # Initialise simulation array
    data_time_steps = np.zeros((len(reg_lookup), len(fuel_type_lookup), len(time_steps), len(appliance_type_lu), len(hours)), dtype=float)

    # Iterate regions
    for reg_nr in range(len(reg_lookup)):
        print("REgion_NR: " + str(reg_nr))

        for ts in time_steps:


            # Get appliances demand of region
            for j in list_dates:
                _info = j.timetuple()
                month = _info[1]            # Month 1: Jan
                month_python = month - 1
                year_day = _info[7]         # Day nr of the year 1.Jan = 1
                year_day_python = year_day - 1
                weekday = _info[6]          # 0: Monday

                # Collect absolute data from
                _data_yearday = bd_appliances_elec[fuel_type][reg_nr][year_day_python]

                data_time_steps[reg_nr][fuel_type][ts] = _data_yearday


    return data_time_steps

def shape_base_resid_appliances(path_base_elec_load_profiles, daytypee_lu, appliance_type_lu, base_year):
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
    -appliance_type_lu              Looup dictionary containing all appliances
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
    year_raw_values = np.zeros((len(year_days), len(appliance_type_lu), len(hours)), dtype=float)

    # Initialise HES dictionary with every month and day-type
    hes_data = np.zeros((len(daytypee_lu), len(month_nr), len(appliance_type_lu), len(hours)), dtype=float)

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
    appliances_shape = np.zeros((len(year_days), len(appliance_type_lu), len(hours)), dtype=float)
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



def calc_base_demand_appliances(shape_appliances_elec, reg_lookup, fuel_type_lookup, base_fuel_data):
    '''
    This function uses the generic shapes of the load profiles to hourly disaggregate energy demand
    for all regions and fuel types

    # So far only eletricity appliances

    out:
    -fuel_type_per_region_hourly        Fueltype per region per appliance per hour
        Fuel_type
            region
                year_days
                    appliances
                        hours
    '''
    fuel_elec = 0

    print("base_fuel_data")
    print(base_fuel_data)  # Electricity is base_fuel_data[:,0]

    base_fuel_data_electricity = base_fuel_data[:, 1] # Base fuel per region
    print("base_fuel_data_electricity")
    print(base_fuel_data_electricity)
    print("---")
    print(len(fuel_type_lookup))
    print(reg_lookup)

    dim_appliance = shape_appliances_elec.shape
    print("dim_appliance: " + str(dim_appliance))

    # Initialise array
    fuel_type_per_region = np.zeros((len(fuel_type_lookup), len(reg_lookup)), dtype=float) # To store absolute demand values
    fuel_type_per_region_hourly = np.zeros((len(fuel_type_lookup), len(reg_lookup), dim_appliance[0], dim_appliance[1], dim_appliance[2]), dtype=float) # To store absolute demand values of hourly appliances

    # Add electricity base data
    fuelType_elec = 0 # Electrcitiy
    for region_nr in range(len(reg_lookup)):
        fuel_type_per_region[fuelType_elec][region_nr] = base_fuel_data_electricity[region_nr]


    print("fuel_type_per_region")
    print(fuel_type_per_region)
    print("-------------")

    # Appliances per region
    for region_nr in range(len(reg_lookup)):
        reg_demand = fuel_type_per_region[fuelType_elec][region_nr]
        print("Local tot demand " + str(reg_demand))
        reg_elec_appliance = shape_appliances_elec * reg_demand # Shape elec appliance * regional demand in [GWh]

        #print("shape insert: " + str(reg_elec_appliance.shape))
        #print("b ex: " + str(fuel_type_per_region_hourly[fuelType_elec][region_nr].shape))
        fuel_type_per_region_hourly[fuelType_elec][region_nr] = reg_elec_appliance

    return fuel_type_per_region_hourly


def writeToEnergySupply(path_out_csv, in_data):
    '''
    REads out results (which still need to be preared) to list of energy supply model.

    Input:
    -path_out_csv   Path to energy supply resulting table
    -in_data        Data input
    '''
    # Prepare data that as follows:

    # YEAR	SEASON	DAY	PERIOD	BusNumber	ElecLoad
    new_data = [[2015,1,1,1,1,100], [2015,1,1,1,1,21000], [2015,1,1,1,1,2030000]]  # YEAR	SEASON	DAY	PERIOD	BusNumber	ElecLoad

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