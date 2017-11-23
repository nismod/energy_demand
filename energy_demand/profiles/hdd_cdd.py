"""Functions related to heating or cooling degree days
"""
import numpy as np
from energy_demand.geography import weather_station_location as weather_station
from energy_demand.technologies import diffusion_technologies
from energy_demand.profiles import load_profile

def calc_hdd(t_base, temp_yh):
    """Heating Degree Days for every day in a year

    Arguments
    ----------
    t_base : int
        Base temperature
    temp_yh : array
        Array containing daily temperatures for each day (shape nr_of_days, 24)

    Returns
    -------
    hdd_d : array
        An array containing the Heating Degree Days for every day (shape nr_of_days, 1)

    Note
    -----
    This function is optimised for speed. A more intuitive reading is as follows:
    """
    temp_diff = (t_base - temp_yh) / 24
    temp_diff[temp_diff < 0] = 0
    hdd_d = np.sum(temp_diff, axis=1)

    return hdd_d

def calc_cdd(rs_t_base_cooling, temperatures):
    """Calculate cooling degree days

    Arguments
    ----------
    rs_t_base_cooling : float
        Base temperature for cooling
    temperatures : array
        Temperatures for every hour in a year

    Return
    ------
    cdd_d : array
        Contains all CDD for every day in a year (nr_of_days, 1)

    Note
    -----
    - For more info see Formual 2.1: Degree-days: theory and application
      https://www.designingbuildings.co.uk/wiki/Cooling_degree_days
    """
    temp_diff = (temperatures - rs_t_base_cooling) / 24
    temp_diff[temp_diff < 0] = 0
    cdd_d = np.sum(temp_diff, axis=1)

    return cdd_d

def get_hdd_country(
        sim_param,
        regions,
        temp_data,
        diff_params,
        t_base_fy,
        t_base_cy,
        reg_coord,
        weather_stations
    ):
    """Calculate total number of heating degree days in a region for the base year

    Arguments
    ----------
    regions : dict
        Dictionary containing regions
    data : dict
        Dictionary with data
    """
    hdd_regions = {}

    for region_name in regions:

        # Get closest weather station and temperatures
        closest_station_id = weather_station.get_closest_station(
            reg_coord[region_name]['longitude'],
            reg_coord[region_name]['latitude'],
            weather_stations)

        temperatures = temp_data[closest_station_id]

        # Base temperature for base year
        t_base_heating_cy = sigm_temp(
            t_base_fy,
            t_base_cy,
            sim_param['base_yr'],
            sim_param['curr_yr'],
            diff_params['sig_midpoint'],
            diff_params['sig_steeppness'],
            diff_params['yr_until_changed'])

        hdd_reg = calc_hdd(t_base_heating_cy, temperatures)

        hdd_regions[region_name] = np.sum(hdd_reg)

    return hdd_regions

def get_cdd_country(
        sim_param,
        regions,
        temp_data,
        diff_params,
        t_base_fy,
        t_base_cy,
        reg_coord,
        weather_stations):
    """Calculate total number of cooling degree days in a region for the base year

    Arguments
    ----------
    sim_param : dict
        Simulation parameters
    regions : dict
        Dictionary containing regions
    temp_data : array
        Temperature data
    assumptions : dict
        Assumptions
    reg_coord : dict
        Coordinates
    weather_stations : dict
        Weather stations
    t_base_type : str
        Type of base temperature
    """
    cdd_regions = {}

    for region_name in regions:
        longitude = reg_coord[region_name]['longitude']
        latitude = reg_coord[region_name]['latitude']

        # Get closest weather station and temperatures
        closest_station_id = weather_station.get_closest_station(
            longitude,
            latitude,
            weather_stations)

        # Temp data
        temperatures = temp_data[closest_station_id]

        # Base temperature for base year
        t_base_heating_cy = sigm_temp(
            t_base_fy,
            t_base_cy,
            sim_param['base_yr'],
            sim_param['curr_yr'],
            diff_params['sig_midpoint'],
            diff_params['sig_steeppness'],
            diff_params['yr_until_changed'])

        cdd_reg = calc_cdd(t_base_heating_cy, temperatures)
        cdd_regions[region_name] = np.sum(cdd_reg)

    return cdd_regions

def sigm_temp(
        t_future_yr,
        t_base_yr,
        base_yr,
        curr_yr,
        sig_midpoint,
        sig_steeppness,
        yr_until_changed
    ):
    """Calculate base temperature depending on sigmoid
    diff and location

    Arguments
    ----------
    sim_param : dict
        Base simulation assumptions
    assumptions : dict
        Dictionary with assumptions

    Return
    ------
    t_base_cy : float
        Base temperature of current year

    Note
    ----
    Depending on the base temperature in the base and end year
    a sigmoid diffusion from the base temperature from the base year
    to the end year is calculated

    This allows to model changes e.g. in thermal confort
    """
    # Base temperature of end year minus base temp of base year
    t_base_diff = t_future_yr - t_base_yr

    # Sigmoid diffusion
    t_base_frac = diffusion_technologies.sigmoid_diffusion(
        base_yr,
        curr_yr,
        yr_until_changed,
        sig_midpoint,
        sig_steeppness)

    # Temp diff until current year
    t_diff_cy = t_base_diff * t_base_frac

    # Add temp change to base year temp
    t_base_cy = t_diff_cy + t_base_yr

    return t_base_cy

def calc_reg_hdd(temperatures, t_base_heating, model_yeardays):
    """Calculate hdd for every day and daily
    yd shape of heating demand

    Arguments
    ----------
    temperatures : array
        Temperatures
    t_base_heating : float
        Base temperature for heating

    Return
    ------
    hdd_d : array
        Heating degree days for every day in a year (nr_of_days, 1)
    shape_hdd_d : array
        Shape for heating days (only selected modelling days)

    Note
    -----
    - Based on temperatures of a year, the HDD are calculated for every
      day in a year. Based on the sum of all HDD of all days, the relative
      share of heat used for any day is calculated.

    - The Heating Degree Days are calculated based on assumptions of
      the base temperature of the current year.

    - The shape_yd can be calcuated as follows: 1/ np.sum(hdd_d) * hdd_d

    - The diffusion is assumed to be sigmoid
    """
    # Temperatures of full year
    hdd_d = calc_hdd(t_base_heating, temperatures)

    shape_hdd_d = load_profile.abs_to_rel(hdd_d)

    # Select only modelled yeardays
    shape_hdd_d_selection = shape_hdd_d[[model_yeardays]]

    return hdd_d, shape_hdd_d_selection

def calc_reg_cdd(temperatures, t_base_cooling, model_yeardays):
    """Calculate CDD for every day and daily yd shape of cooling demand

    Arguments
    ----------
    temperatures : array
        Temperatures
    t_base_cooling : array
        Base temperature cooling

    Return
    ------
    shape_yd : array
        Fraction of heat for every day. Array-shape: nr_of_days, 1

    Note
    ----
    - Based on temperatures of a year, the CDD are calculated for every
      day in a year. Based on the sum of all CDD of all days, the relative
      share of heat used for any day is calculated.

    - The Cooling Degree Days are calculated based on assumptions of
      the base temperature of the current year.
    """
    cdd_d = calc_cdd(t_base_cooling, temperatures)
    shape_cdd_d = load_profile.abs_to_rel(cdd_d)

    # Select only modelled yeardays
    shape_cdd_d_selection = shape_cdd_d[[model_yeardays]]
    cdd_d_selection = cdd_d[[model_yeardays]]

    return cdd_d_selection, shape_cdd_d_selection
