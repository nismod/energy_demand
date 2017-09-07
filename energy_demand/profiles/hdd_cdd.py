"""Functions related to heating or cooling degree days
"""
import numpy as np
from energy_demand.geography import weather_station_location as weather_station
from energy_demand.technologies import diffusion_technologies
from energy_demand.profiles import load_profile
# pylint: disable=I0011,C0321,C0301,C0103,C0325

def calc_hdd(t_base, temp_yh):
    """Heating Degree Days for every day in a year

    Parameters
    ----------
    t_base : int
        Base temperature
    temp_yh : array
        Array containing daily temperatures for each day (shape 365, 24)

    Returns
    -------
    hdd_d : array
        An array containing the Heating Degree Days for every day (shape 365, 1)

    Note
    -----
    This function is optimised for speed. A more intuitive reading is as follows:

        # hdd_d = np.zeros((365))

        # for day, temp_day in enumerate(temp_yh):
        # hdd = 0
        # for temp_h in temp_day:
        #    diff = t_base - temp_h
        #    if diff > 0:
        #        hdd += diff
    """
    temp_diff = (t_base - temp_yh) / 24
    temp_diff[temp_diff < 0] = 0
    hdd_d = np.sum(temp_diff, axis=1)

    return hdd_d

def calc_cdd(rs_t_base_cooling, temperatures):
    """Calculate cooling degree days

    Parameters
    ----------
    rs_t_base_cooling : float
        Base temperature for cooling
    temperatures : array
        Temperatures for every hour in a year

    Return
    ------
    cdd_d : array
        Contains all CDD for every day in a year (365, 1)

    Note
    -----
    - For more info see Formual 2.1: Degree-days: theory and application
      https://www.designingbuildings.co.uk/wiki/Cooling_degree_days

    ```#cdd_d = np.zeros((365))
    # for day_nr, day_temp in enumerate(temperatures):
        #ccd_d = 0
        #for temp_h in day_temp:
        #    diff_t = temp_h - rs_t_base_cooling
        #    if diff_t > 0: # Only if cooling is necessary
        #        ccd_d += diff_t```
    """
    temp_diff = (temperatures - rs_t_base_cooling) / 24
    temp_diff[temp_diff < 0] = 0
    cdd_d = np.sum(temp_diff, axis=1)

    return cdd_d

def get_hdd_country(regions, data, t_base_type):
    """Calculate total number of heating degree days in a region for the base year

    Parameters
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
            data['reg_coord'][region_name]['longitude'],
            data['reg_coord'][region_name]['latitude'],
            data['weather_stations']
            )

        temperatures = data['temperature_data'][closest_station_id][data['sim_param']['base_yr']]

        # Base temperature for base year
        t_base_heating_cy = sigm_temp(data['sim_param'], data['assumptions'], t_base_type)

        hdd_reg = calc_hdd(t_base_heating_cy, temperatures)
        hdd_regions[region_name] = np.sum(hdd_reg)

    return hdd_regions

def get_cdd_country(regions, data, t_base_type):
    """Calculate total number of cooling degree days in a region for the base year

    Parameters
    ----------
    regions : dict
        Dictionary containing regions
    data : dict
        Dictionary with data
    """
    cdd_regions = {}

    for region_name in regions:
        longitude = data['reg_coord'][region_name]['longitude']
        latitude = data['reg_coord'][region_name]['latitude']

        # Get closest weather station and temperatures
        closest_station_id = weather_station.get_closest_station(
            longitude,
            latitude,
            data['weather_stations']
            )

        # Temp data
        temperatures = data['temperature_data'][closest_station_id][data['sim_param']['base_yr']]

        # Base temperature for base year
        t_base_heating_cy = sigm_temp(
            data['sim_param'],
            data['assumptions'],
            t_base_type
            )

        cdd_reg = calc_cdd(t_base_heating_cy, temperatures)
        cdd_regions[region_name] = np.sum(cdd_reg)

    return cdd_regions

def sigm_temp(base_sim_param, assumptions, t_base_type):
    """Calculate base temperature depending on sigmoid diff and location

    Parameters
    ----------
    base_sim_param : dict
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
    t_base_diff = assumptions[t_base_type]['end_yr'] - assumptions[t_base_type]['base_yr']

    # Sigmoid diffusion
    t_base_frac = diffusion_technologies.sigmoid_diffusion(
        base_sim_param['base_yr'],
        base_sim_param['curr_yr'],
        base_sim_param['end_yr'],
        assumptions['smart_meter_diff_params']['sig_midpoint'],
        assumptions['smart_meter_diff_params']['sig_steeppness']
        )

    # Temp diff until current year
    t_diff_cy = t_base_diff * t_base_frac

    # Add temp change to base year temp
    t_base_cy = t_diff_cy + assumptions[t_base_type]['base_yr']

    return t_base_cy

def get_reg_hdd(temperatures, t_base_heating):
    """Calculate HDD for every day and daily yd shape of cooling demand

    Parameters
    ----------
    temperatures : array
        Temperatures
    t_base_heating : float
        Base temperature for heating

    Return
    ------
    hdd_d : array
        Heating degree days for every day in a year (365, 1)

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
    hdd_d = calc_hdd(t_base_heating, temperatures)
    shape_hdd_d = load_profile.abs_to_rel(hdd_d)

    return hdd_d, shape_hdd_d

def get_reg_cdd(temperatures, t_base_cooling):
    """Calculate CDD for every day and daily yd shape of cooling demand

    Parameters
    ----------
    temperatures : array
        Temperatures
    t_base_cooling : array
        Base temperature cooling

    Return
    ------
    shape_yd : array
        Fraction of heat for every day. Array-shape: 365, 1

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

    return cdd_d, shape_cdd_d
