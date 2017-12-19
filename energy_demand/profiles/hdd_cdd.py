"""Functions related to heating or cooling degree days
"""
import numpy as np
from energy_demand.geography import weather_station_location as weather_station
from energy_demand.technologies import diffusion_technologies
from energy_demand.profiles import load_profile

def calc_hdd(t_base, temp_yh, nr_day_to_av):
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
        An array containing the Heating Degree Days
        for every day (shape nr_of_days, 1)

    Note
    -----
    This function is optimised for speed. A more intuitive reading is as follows:
    """
    # ---------------------------------------------
    # Average temperature with previous day(s) information
    # ---------------------------------------------
    temp_yh = averaged_temp(temp_yh, nr_day_to_av=nr_day_to_av)

    temp_diff = (t_base - temp_yh) / 24
    temp_diff[temp_diff < 0] = 0
    hdd_d = np.sum(temp_diff, axis=1)

    # -----------------------------------------
    # Average hdd with previous day(s) information
    # -----------------------------------------
    #hdd_d = averaged_hdd(hdd_d, nr_day_to_av=2)

    return hdd_d

def averaged_temp(temp_yh, nr_day_to_av):
    """Average temperatures with previous day. Todays temperatures (starting
    from 2. of January) are averaged with yesterdays temperatures. This is done
    to follow the methodology of National Grid (2012): Gas demand forecasting
    methdolology.

    The effective temperature is half of yesterday’s temperature added to half of
    today’s actual temperature. Effective temperature takes into account the previous
    day’s temperature due to consumer behaviour and perception of the weather.

    Arguments
    ---------
    temp_yh : array
        Temperatures for every hour for all modelled days
    nr_day_to_av : int
        Number of previous days to average current day

    Returns
    -------
    effective_temp_yh : array
        Averaged temperatures with temperatures of previous day(s)

    Notes
    ------
    Correlation results (r_value) for base year with different nr_day_to_av.
        nr_day_to_av = 0: 0.807
        nr_day_to_av = 1: 0.840 ()
        nr_day_to_av = 2: 0.865 ()
        nr_day_to_av = 3: 0.878
    """
    modelled_days = range(365)
    effective_temp_yh = np.zeros((365, 24))

    for day in range(nr_day_to_av):
        effective_temp_yh[day] = temp_yh[day]

    for day in modelled_days[nr_day_to_av:]: #Skip first dates in January

        # Add todays temperature and previous effective temps
        tot_temp = 0
        tot_temp += temp_yh[day]
        for i in range(nr_day_to_av):
            #tot_temp += temp_yh[day - (i+1)]
            tot_temp += effective_temp_yh[day - (i+1)]

        effective_temp_yh[day] = tot_temp / (nr_day_to_av + 1)

    return effective_temp_yh

def averaged_hdd(hdd_d, nr_day_to_av):
    """Average calculated HDD per day with previous HDD per day

    Arguments
    ---------
    hdd_d : array
        heating degree days for every day
    nr_day_to_av : int
        Number of previous days to average

    Returns
    -------
    effective_hdd_d : array
        Averaged hdd with hdd of previous day(s)

    Notes
    ------
    Correlation results (r_value) for base year with different nr_day_to_av.

        nr_day_to_av = 0: 0.807
        nr_day_to_av = 1: 0.836  (not affective 0.819)
        nr_day_to_av = 2: 0.860 (not affective 0.830)
        nr_day_to_av = 3: (not affective 0.839)
        nr_day_to_av = 4: (not affective 0.845)
        nr_day_to_av = 5: (not affective 0.849)
        nr_day_to_av = 6: (not affective 0.854)

        10: 0.859
        20: 0.86 --> splitting of lines?
    """
    if nr_day_to_av == 0:
        effective_hdd_d = hdd_d
        return effective_hdd_d
    else:
        to_iterate = range(nr_day_to_av)

        effective_hdd_d = np.zeros((hdd_d.shape[0]))

        # Copy initial days
        for day in to_iterate:
            effective_hdd_d[day] = hdd_d[day]

        for day, hdd_today in enumerate(hdd_d[nr_day_to_av:], nr_day_to_av): #Skip first dates in year for average

            # Todays HDD plus effective HDD from past
            tot_hdd = 0
            tot_hdd += hdd_today

            for i in to_iterate:
                tot_hdd += effective_hdd_d[day - (i + 1)]
            effective_hdd_d[day] = tot_hdd / (nr_day_to_av + 1)

        return effective_hdd_d

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
        base_yr,
        curr_yr,
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

    for region in regions:

        # Get closest weather station and temperatures
        closest_station_id = weather_station.get_closest_station(
            reg_coord[region]['longitude'],
            reg_coord[region]['latitude'],
            weather_stations)

        temperatures = temp_data[closest_station_id]

        # Base temperature for base year
        t_base_heating_cy = sigm_temp(
            t_base_fy,
            t_base_cy,
            base_yr,
            curr_yr,
            diff_params['sig_midpoint'],
            diff_params['sig_steeppness'],
            diff_params['yr_until_changed'])

        hdd_reg = calc_hdd(t_base_heating_cy, temperatures, nr_day_to_av=2)

        hdd_regions[region] = np.sum(hdd_reg)

    return hdd_regions

def get_cdd_country(
        base_yr,
        curr_yr,
        regions,
        temp_data,
        diff_params,
        t_base_fy,
        t_base_cy,
        reg_coord,
        weather_stations):
    """Calculate total number of cooling degree days in a
    region for the base year

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

    for region in regions:
        longitude = reg_coord[region]['longitude']
        latitude = reg_coord[region]['latitude']

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
            base_yr,
            curr_yr,
            diff_params['sig_midpoint'],
            diff_params['sig_steeppness'],
            diff_params['yr_until_changed'])

        cdd_reg = calc_cdd(t_base_heating_cy, temperatures)
        cdd_regions[region] = np.sum(cdd_reg)

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
    hdd_d = calc_hdd(t_base_heating, temperatures, nr_day_to_av=2)

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
