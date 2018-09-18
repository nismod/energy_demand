"""Read residential raw files and store to txt
"""
import os
import csv
from datetime import date
import logging
import numpy as np
from energy_demand.basic import date_prop
from energy_demand.read_write import read_data
from energy_demand.read_write import write_data
from energy_demand.profiles import load_profile as lp

def read_csv(path_to_csv):
    """This function reads in CSV files and skips header row.

    Arguments
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
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        # Iterate rows
        for row in read_lines:
            service_switches.append(row)

    return np.array(service_switches) # Convert list into array

def get_hes_load_shapes(
        appliances_hes_matching,
        year_raw_values,
        hes_y_peak,
        enduse,
        single_enduse=True,
        enduses=False
    ):
    """Read in raw HES data and generate shapes

    Calculate peak day demand

    Arguments
    ----------
    appliances_hes_matching : dict
        HES appliances are matched witch enduses
    year_raw_values : array
        Yearly values from raw
    hes_y_peak : data
        Peak raw values
    enduse : string
        enduse

    Returns
    -------
    shape_peak_yh : float
        Peak demand of each hours of peak day

    Notes
    -----
    The HES appliances are matched with enduses
    """
    if single_enduse:
        # Match enduse with HES appliance ID
        # (see look_up table in original files for more information)
        hes_app_id = appliances_hes_matching[enduse]

        # Values
        enduse_values = year_raw_values[:, :, hes_app_id]

        # Total yearly demand of hes_app_id
        tot_enduse_y = np.sum(year_raw_values[:, :, hes_app_id])

        # Get peak daily load shape, calculate amount of energy demand for peak day of hes_app_id
        peak_h_values = hes_y_peak[:, hes_app_id]

    else:
        for multi_enduse in enduses:

            # Id of enduse
            hes_app_id = appliances_hes_matching[multi_enduse]

            try:
                tot_enduse_y += np.sum(year_raw_values[:, :, hes_app_id])

                # Get peak daily load shape, calculate amount of energy demand for peak day of hes_app_id
                peak_h_values += hes_y_peak[:, hes_app_id]

                # Values
                enduse_values += year_raw_values[:, :, hes_app_id]

            except:
                # Total yearly demand of hes_app_id
                tot_enduse_y = np.sum(year_raw_values[:, :, hes_app_id])
                
                # Get peak daily load shape, calculate amount of energy demand for peak day of hes_app_id
                peak_h_values = hes_y_peak[:, hes_app_id]

                enduse_values = year_raw_values[:, :, hes_app_id]

    # Maximum daily demand
    tot_peak_demand_d = np.sum(peak_h_values)

    # Shape of peak day (hourly values of peak day)
    shape_peak_dh = lp.abs_to_rel(peak_h_values)

    # ---Calculate non-peak shapes
    shape_non_peak_yd = np.zeros((365), dtype="float")
    shape_non_peak_y_dh = np.zeros((365, 24), dtype="float")

    for day, day_values in enumerate(enduse_values):
        #day_values = year_raw_values[day, :, hes_app_id]

        shape_non_peak_yd[day] = (1.0 / tot_enduse_y) * np.sum(day_values)
        shape_non_peak_y_dh[day] = (1.0 / np.sum(day_values)) * day_values

    return shape_peak_dh, shape_non_peak_y_dh, shape_non_peak_yd

def assign_hes_data_to_year(nr_of_appliances, hes_data, base_yr):
    """Fill every base year day with correct data

    Arguments
    ----------
    nr_of_appliances : dict
        Defines how many appliance types are stored (max 10 provided in original hes file)
    hes_data : array
        HES raw data for every month and daytype and appliance
    base_yr : float
        Base year to generate shapes

    Returns
    -------
    year_raw_values : array
        Energy data for every day in the base year for every appliances
    """
    year_raw_values = np.zeros((365, 24, nr_of_appliances), dtype="float") #yeardays, houry, appliances

    # Create list with all dates of a whole year
    list_dates = date_prop.fullyear_dates(
        start=date(base_yr, 1, 1),
        end=date(base_yr, 12, 31))

    # Assign every date to the place in the array of the year
    for yearday_date in list_dates:

        month_python = date_prop.get_month_from_yeraday(
            yearday_date.timetuple().tm_year,
            yearday_date.timetuple().tm_yday)

        yearday_python = date_prop.date_to_yearday(
            yearday_date.timetuple().tm_year,
            yearday_date.timetuple().tm_mon,
            yearday_date.timetuple().tm_mday)

        daytype_str = date_prop.get_weekday_type(yearday_date)

        # Get day from HES raw data array
        year_raw_values[yearday_python] = hes_data[daytype_str][month_python]

    return year_raw_values

def read_hes_data(paths_hes, nr_app_type_lu):
    """Read in HES raw csv files and provide for every
    day in a year (yearday) all fuels

    The fuel is provided for every daytype (weekend or working day)
    for every month and every appliance_typ

    Arguments
    ----------
    paths_hes : string
        Path to HES raw data file
    nr_app_type_lu : dict
        Number of appliances (defines size of container to store data)

    Returns
    -------
    hes_data : dict
        HES non peak raw data per fueltype
    hes_y_coldest : array
        HES for coldest day

    Note
    ----
        -   As only shapes are generated, the absolute
            values are irrelevant, i.e. the unit of energy
    """
    day_type_lu = {
        0: 'holiday',
        1: 'working_day',
        2: 'coldest'}

    hes_data = {}
    for day_type_str in day_type_lu.values():
        hes_data[day_type_str] = np.zeros((12, 24, nr_app_type_lu), dtype="float")

    hes_y_coldest = np.zeros((24, nr_app_type_lu), dtype="float")

    # Read in raw HES data from CSV
    raw_elec_data = read_csv(paths_hes)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month_int, day_type, appliance_typ = int(row[0]), str(row[1]), int(row[2])
        k_header = 3 #Row in Excel where energy data start

        for hour in range(24):
            hourly_value = float(row[k_header])

            # if coldest (see HES file)
            if day_type == 'coldest':
                hes_y_coldest[hour][appliance_typ] = hourly_value
                k_header += 1
            else:
                hes_data[day_type][month_int][hour][appliance_typ] = hourly_value
                k_header += 1

    return hes_data, hes_y_coldest

def run(paths, local_paths, base_yr):
    """Function to run script
    """
    print("... start script %s", os.path.basename(__file__))

    hes_appliances_matching = {
        'rs_cold': 0,
        'rs_cooking': 1,
        'rs_lighting': 2,
        'rs_consumer_electronics': 3,
        'rs_home_computing': 4,
        'rs_wet': 5,
        'rs_water_heating_water_heating': 6,
        'NOT_USED_unkown_1': 7,
        'NOT_USED_unkown_2': 8,
        'NOT_USED_unkown_3': 9,
        'rs_water_heating_showers': 10}

    # HES data -- Generate generic load profiles
    # for all electricity appliances from HES data
    hes_data, hes_y_peak = read_hes_data(
        paths['lp_rs'],
        len(hes_appliances_matching))

    # Assign read in raw data to the base year
    year_raw_hes_values = assign_hes_data_to_year(
        len(hes_appliances_matching),
        hes_data,
        int(base_yr))

    rs_enduses, _, _= read_data.read_fuel_rs(
        paths['rs_fuel_raw'])

    # Load shape for all enduses
    for enduse in rs_enduses:

        if enduse not in hes_appliances_matching:

            # Merge shapes of water heating and shower
            if enduse == 'rs_water_heating':

                # Generate HES load shapes
                shape_peak_dh, shape_non_peak_y_dh, shape_non_peak_yd = get_hes_load_shapes(
                    hes_appliances_matching,
                    year_raw_hes_values,
                    hes_y_peak,
                    enduse,
                    single_enduse=False,
                    enduses=['rs_water_heating_showers', 'rs_water_heating_water_heating'])

                # Write txt files
                write_data.create_txt_shapes(
                    enduse,
                    local_paths['rs_load_profile_txt'],
                    shape_peak_dh,
                    shape_non_peak_y_dh,
                    shape_non_peak_yd)
            else:
                pass
        else:
            # Generate HES load shapes
            shape_peak_dh, shape_non_peak_y_dh, shape_non_peak_yd = get_hes_load_shapes(
                hes_appliances_matching,
                year_raw_hes_values,
                hes_y_peak,
                enduse)

            # Write txt files
            write_data.create_txt_shapes(
                enduse,
                local_paths['rs_load_profile_txt'],
                shape_peak_dh,
                shape_non_peak_y_dh,
                shape_non_peak_yd)

    logging.info("... finished script %s", os.path.basename(__file__))
    return
