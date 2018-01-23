"""Read residential raw files and store to txt
"""
import os
import csv
from datetime import date
import numpy as np
import logging
from energy_demand.basic import date_prop
from energy_demand.scripts import s_shared_functions
from energy_demand.read_write import read_data
from energy_demand.read_write import data_loader
from energy_demand.assumptions import non_param_assumptions
from energy_demand.assumptions import param_assumptions
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

def get_hes_load_shapes(appliances_hes_matching, year_raw_values, hes_y_peak, enduse):
    """Read in raw HES data and generate shapes

    Calculate peak day demand

    Arguments
    ----------
    appliances_hes_matching : dict
        HES appliances are matched witch enduses
    year_raw_values : data
        Yearly values from raw
    hes_y_peak : data
        Peak raw values
    enduse : string
        enduse

    Returns
    -------
    shape_peak_yd_factor : float
        Peak day demand (Calculate factor which can be used to
        multiply yearly demand to generate peak demand)
    shape_peak_yh : float
        Peak demand of each hours of peak day

    Notes
    -----
    The HES appliances are matched with enduses
    """
    # Match enduse with HES appliance ID (see look_up table in original files for more information)
    if enduse in appliances_hes_matching:
        hes_app_id = appliances_hes_matching[enduse]
    else:
        logging.debug("...The enduse has not HES ID and thus shape")

    # Total yearly demand of hes_app_id
    tot_enduse_y = np.sum(year_raw_values[:, :, hes_app_id])

    # ---Peak calculation Get peak daily load shape

    # Calculate amount of energy demand for peak day of hes_app_id
    peak_h_values = hes_y_peak[:, hes_app_id]

    # Shape of peak day (hourly values of peak day) #1.0/tot_peak_demand_d * peak_h_values
    shape_peak_dh = lp.abs_to_rel(peak_h_values)

    # Maximum daily demand
    tot_peak_demand_d = np.sum(peak_h_values)

    # Factor to calculate daily peak demand from yearly demand
    shape_peak_yd_factor = (1.0 / tot_enduse_y) * tot_peak_demand_d

    # ---Calculate non-peak shapes
    shape_non_peak_yd = np.zeros((365), dtype=float)
    shape_non_peak_y_dh = np.zeros((365, 24), dtype=float)

    for day in range(365):
        day_values = year_raw_values[day, :, hes_app_id]

        shape_non_peak_yd[day] = (1.0 / tot_enduse_y) * np.sum(day_values)
        shape_non_peak_y_dh[day] = (1.0 / np.sum(day_values)) * day_values # daily shape

    return shape_peak_dh, shape_non_peak_y_dh, shape_peak_yd_factor, shape_non_peak_yd

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
    year_raw_values = np.zeros((365, 24, nr_of_appliances), dtype=float)

    # Create list with all dates of a whole year
    list_dates = date_prop.fullyear_dates(
        start=date(base_yr, 1, 1),
        end=date(base_yr, 12, 31))

    # Assign every date to the place in the array of the year
    for yearday in list_dates:
        month_python = yearday.timetuple().tm_mon - 1 # - 1 because in _info: Month 1 = Jan
        yearday_python = yearday.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
        daytype_str = date_prop.get_weekday_type(yearday)

        # Get day from HES raw data array
        year_raw_values[yearday_python] = hes_data[daytype_str][month_python]

    return year_raw_values

def read_hes_data(paths_hes, nr_app_type_lu):
    """Read in HES raw csv files and provide for every day in a year (yearday) all fuels

    The fuel is provided for every daytype (weekend or working day) for every month
    and every appliance_typ

    Arguments
    ----------
    paths_hes : string
        Path to HES raw data file
    nr_app_type_lu : dict
        Number of appliances (defines size of container to store data)
    day_type_lu : dict
        Look-up table for daytypes

    Returns
    -------
    hes_data : dict
        HES non peak raw data TODO CORRECT
    hes_y_coldest : array
        HES for coldest day
    hes_y_warmest : array
        HES for warmest day

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
    for day_type_int, day_type_str in day_type_lu.items():
        hes_data[day_type_str] = np.zeros((12, 24, nr_app_type_lu), dtype=float)

    hes_y_coldest = np.zeros((24, nr_app_type_lu), dtype=float)

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
        'rs_water_heating': 6,
        'NOT_USED_unkown_1': 7,
        'NOT_USED_unkown_2': 8,
        'NOT_USED_unkown_3': 9,
        'NOT_USED_showers': 10}

    # HES data -- Generate generic load profiles
    # for all electricity appliances from HES data
    hes_data, hes_y_peak = read_hes_data(
        local_paths['path_bd_e_load_profiles'],
        len(hes_appliances_matching))

    # Assign read in raw data to the base year
    year_raw_hes_values = assign_hes_data_to_year(
        len(hes_appliances_matching),
        hes_data,
        int(base_yr))

    _, rs_enduses = read_data.read_base_data_resid(
        paths['rs_fuel_raw_data_enduses'])

    # Load shape for all enduses
    for enduse in rs_enduses:
        if enduse not in hes_appliances_matching:
            logging.debug("Warning: The enduse %s is not defined in hes_appliances_matching", enduse)
        else:
            # Generate HES load shapes
            shape_peak_dh, shape_non_peak_y_dh, shape_peak_yd_factor, shape_non_peak_yd = get_hes_load_shapes(
                hes_appliances_matching,
                year_raw_hes_values,
                hes_y_peak,
                enduse)

            # Write txt files
            s_shared_functions.create_txt_shapes(
                enduse,
                local_paths['rs_load_profiles'],
                shape_peak_dh,
                shape_non_peak_y_dh,
                shape_peak_yd_factor,
                shape_non_peak_yd)

    print("... finished script %s", os.path.basename(__file__))
    return
