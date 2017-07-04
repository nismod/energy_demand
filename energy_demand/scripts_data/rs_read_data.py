"""Read raw data for residential sector (mainly HES data)
"""
from datetime import date
import numpy as np
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_data import read_data

def get_hes_load_shapes(appliances_hes_matching, year_raw_values, hes_y_peak, enduse):
    """Read in raw HES data and generate shapes

    Calculate peak day demand

    Parameters
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
        print("...The enduse has not HES ID and thus shape")

    # Total yearly demand of hes_app_id
    tot_enduse_y = np.sum(year_raw_values[:, :, hes_app_id])

    # ---Peak calculation Get peak daily load shape

    # Calculate amount of energy demand for peak day of hes_app_id
    peak_h_values = hes_y_peak[:, hes_app_id]

    # Shape of peak day (hourly values of peak day) #1.0/tot_peak_demand_d * peak_h_values
    shape_peak_dh = shape_handling.absolute_to_relative(peak_h_values)

    # Maximum daily demand
    tot_peak_demand_d = np.sum(peak_h_values)

    # Factor to calculate daily peak demand from yearly demand
    shape_peak_yd_factor = (1.0 / tot_enduse_y) * tot_peak_demand_d

    # ---Calculate non-peak shapes
    shape_non_peak_yd = np.zeros((365))
    shape_non_peak_dh = np.zeros((365, 24))

    for day in range(365):
        day_values = year_raw_values[day, :, hes_app_id]

        shape_non_peak_yd[day] = (1.0 / tot_enduse_y) * np.sum(day_values)
        shape_non_peak_dh[day] = (1.0 / np.sum(day_values)) * day_values # daily shape

    return shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd

def assign_hes_data_to_year(nr_of_appliances, hes_data, base_yr):
    '''Fill every base year day with correct data

    Parameters
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
    '''
    year_raw_values = np.zeros((365, 24, nr_of_appliances), dtype=float)

    # Create list with all dates of a whole year
    list_dates = date_handling.fullyear_dates(start=date(base_yr, 1, 1), end=date(base_yr, 12, 31))

    # Assign every date to the place in the array of the year
    for yearday in list_dates:
        month_python = yearday.timetuple().tm_mon - 1 # - 1 because in _info: Month 1 = Jan
        yearday_python = yearday.timetuple().tm_yday - 1 # - 1 because in _info: 1.Jan = 1
        daytype = date_handling.get_weekday_type(yearday)

        # Get day from HES raw data array
        year_raw_values[yearday_python] = hes_data[daytype][month_python] 

    return year_raw_values

def read_hes_data(paths_hes, nr_app_type_lu, day_type_lu):
    '''Read in HES raw csv files and provide for every day in a year (yearday) all fuels

    The fuel is provided for every daytype (weekend or working day) for every month
    and every appliance_typ

    Parameters
    ----------
    paths_hes : string
        Path to HES raw data file
    nr_app_type_lu : dict
        Number of appliances (defines size of container to store data)
    day_type_lu : dict
        Look-up table for daytypes

    Returns
    -------
    hes_data : array
        HES non peak raw data
    hes_y_coldest : array
        HES for coldest day
    hes_y_warmest : array
        HES for warmest day

    Info
    ----
    '''
    hes_data = np.zeros((len(day_type_lu), 12, 24, nr_app_type_lu), dtype=float)

    hes_y_coldest = np.zeros((24, nr_app_type_lu))
    hes_y_warmest = np.zeros((24, nr_app_type_lu))

    # Read in raw HES data from CSV
    raw_elec_data = read_data.read_csv(paths_hes)

    # Iterate raw data of hourly eletrictiy demand
    for row in raw_elec_data:
        month, daytype, appliance_typ = int(row[0]), int(row[1]), int(row[2])
        k_header = 3 #Row in Excel where energy data start

        for hour in range(24): # iterate over hour  = row in csv file
            # [kWH electric] Converts the summed watt into kWH
            # Note: This would actually not necessary as we are only calculating in relative terms
            _value = float(row[k_header]) * (float(1)/float(6)) * (float(1)/float(1000))

            # if coldest (see HES file)
            if daytype == 2:
                hes_y_coldest[hour][appliance_typ] = _value
                k_header += 1
            elif daytype == 3:
                hes_y_warmest[hour][appliance_typ] = _value
                k_header += 1
            else:
                hes_data[daytype][month][hour][appliance_typ] = _value
                k_header += 1

    return hes_data, hes_y_coldest, hes_y_warmest
