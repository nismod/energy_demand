"""Functions related to heating or cooling degree days
"""
import numpy as np

from energy_demand.basic import testing_functions
from energy_demand.geography import weather_station_location as weather_station
from energy_demand.profiles import load_profile

def calc_cdd_min_max(t_min, t_max, t_base):
    """Calculate daily cdd with minimum and maximum
    daily temperatures

    Arguments
    ---------
    t_min : array, shape(365)
        Daily minimum temperatures
    t_max : array, shape(365)
        Daily maximum temperatures
    t_base : float
        Base temperature

    Returns
    -------
    cdd_365 : array
        Daily heating degree days
    """
    cdd_365 = np.zeros((365))
    for day in range(365):

        t_min_day = t_min[day]
        t_max_day = t_max[day]

        case_nr = get_meterological_equation_case_cdd(
            t_min_day,
            t_max_day,
            t_base)

        cdd = calc_met_equation_cdd(
            case_nr,
            t_min_day,
            t_max_day,
            t_base)

        cdd_365[day] = cdd

    assert not testing_functions.test_if_minus_value_in_array(cdd_365)

    return cdd_365

def calc_hdd_min_max(t_min, t_max, t_base):
    """Calculate daily hdd with minimum and maximum
    daily temperatures

    Arguments
    ---------
    t_min : array, shape(365)
        Daily minimum temperatures
    t_max : array, shape(365)
        Daily maximum temperatures
    t_base : float
        Base temperature

    Returns
    -------
    hdd_365 : array
        Daily heating degree days
    """
    hdd_365 = np.zeros((365))
    for day in range(365):

        t_min_day = t_min[day]
        t_max_day = t_max[day]

        case_nr = get_meterological_equation_case_hdd(
            t_min_day,
            t_max_day,
            t_base)

        hdd = calc_met_equation_hdd(
            case_nr,
            t_min_day,
            t_max_day,
            t_base)

        hdd_365[day] = hdd

    assert not testing_functions.test_if_minus_value_in_array(hdd_365)
    return hdd_365

def calc_met_equation_hdd(case, t_min, t_max, t_base):
    """Calculate hdd according to Meteorological
    Office equations as outlined in Day (2006): Degree-days: theory and application
    """
    if case == 1:
        hdd = t_base - 0.5 * (t_max + t_min)
    elif case == 2:
        hdd = 0.5 * (t_base - t_min) - 0.25 * (t_max - t_base)
    elif case == 3:
        hdd = 0.25 * (t_base - t_min)
    else:
        hdd = 0

    return hdd

def calc_met_equation_cdd(case, t_min, t_max, t_base):
    """Calculate cdd according to Meteorological
    Office equations as outlined in Day (2006): Degree-days: theory and application

    Arguments
    ---------
    case : int
        Case number
    t_min : float
        Minimum daily temperature
    t_max : float
        Maximum dail temperature
    t_base : float
        Base temperature

    Return
    -------
    case_nr : int
        Case number

    """
    if case == 1:
        cdd = 0.5 * (t_max + t_min) - t_base
    elif case == 2:
        cdd = 0.5 * (t_max - t_base) - 0.25 * (t_base - t_min)
    elif case == 3:
        cdd = 0.25 * (t_max - t_base)
    else:
        cdd = 0

    return cdd

def get_meterological_equation_case_hdd(t_min, t_max, t_base):
    """Calculate case number to calculate hdd with Meteorological Office
    equations

    Arguments
    ---------
    t_min : float
        Minimum daily temperature
    t_max : float
        Maximum dail temperature
    t_base : float
        Base temperature

    Return
    -------
    case_nr : int
        Case number

    """
    # Adding own constrained
    if (t_max - t_base) == (t_base - t_min):
        t_base += 0.0001


    if t_max <= t_base:
        return 1
    elif t_min >= t_base:
        return 4
    elif (t_min < t_base) and ((t_max - t_base) < (t_base - t_min)):
        return 2
    elif (t_max > t_base) and ((t_max - t_base) > (t_base - t_min)):
        return 3

    else:
        raise Exception(
            "Error in calculating methorological office equation case {}  {} {} ".format(t_max, t_min, t_base))

def get_meterological_equation_case_cdd(t_min, t_max, t_base):
    """Calculatease number to calculate cdd with Meteorological
    Office equations as outlined in Day (2006): Degree-days: theory and application

    Arguments
    ---------
    t_min : float
        Minimum daily temperature
    t_max : float
        Maximum dail temperature
    t_base : float
        Base temperature

    Return
    -------
    case_nr : int
        Case number
    """
    # Added own additional constrained because funciton failes if (t_max - t_base) == (t_base - t_min)
    if (t_max - t_base) == (t_base - t_min):
        t_base += 0.0001

    if t_min >= t_base:
        return 1
    elif t_max <= t_base:
        return 4
    elif (t_max > t_base) and ((t_max - t_base) > (t_base - t_min)):
        return 2
    elif (t_min < t_base) and ((t_max - t_base) < (t_base - t_min)):
        return 3
    else:

        raise Exception("Error in calculating methorological office equation case {} {} {}".format(t_min, t_max, t_base))

def calc_hdd(
        t_base,
        temp_yh,
        nr_day_to_av,
        crit_temp_min_max
    ):
    """Calculate effective temperatures and
    heating Degree Days for every day in a year

    Arguments
    ----------
    t_base : int
        Base temperature
    temp_yh : array
        Array containing daily temperatures for each day (shape nr_of_days, 24)
    nr_day_to_av : int
        Number of previous days to average current day
    crit_temp_min_max : bool
        Criteria whether hourly or daily temperature input

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
    if not crit_temp_min_max:

        # Calculate effective temperatures
        temp_yh = effective_temps(
            temp_yh,
            nr_day_to_av=nr_day_to_av)

        # Calculate heating degree days
        temp_diff = (t_base - temp_yh) / 24
        temp_diff[temp_diff < 0] = 0
        hdd_d = np.sum(temp_diff, axis=1)

    else:
        # Calculate effective temperatures
        t_min_eff = effective_temps_min_max(
            temp_yh['t_min'],
            nr_day_to_av=nr_day_to_av)

        t_max_eff = effective_temps_min_max(
            temp_yh['t_max'],
            nr_day_to_av=nr_day_to_av)

        # Calculate heating degree days
        hdd_d = calc_hdd_min_max(
            t_min_eff, t_max_eff, t_base)

    return hdd_d

def effective_temps_min_max(temp_365, nr_day_to_av):
    """Calculate effective temperatures for minium and maximum
    temperatures

    Arguments
    ---------
    temp_365 : np.array
        Daily min or max temperatures
    nr_day_to_av : int
        Number of previous days to average current day

    Returns
    -------
    effective_temp_365 : np.array
        Effective daily temperatures
    """
    effective_temp_365 = np.zeros((365), dtype="float")

    # Copy all border days
    for day in range(nr_day_to_av):
        effective_temp_365[day] = temp_365[day]

    # Iterate days in a year
    for day in range(365)[nr_day_to_av:]: #Skip first dates in January

        # Add todays temperature and previous effective temps
        tot_temp = temp_365[day]

        # Add effective temperature of previous day(s)
        for i in range(nr_day_to_av):
            tot_temp = tot_temp + effective_temp_365[day - (i+1)] #not +=

        effective_temp_365[day] = tot_temp / (nr_day_to_av + 1)

    return effective_temp_365

def effective_temps(temp_yh, nr_day_to_av):
    """Calculate effective temperatures

    Todays temperatures (starting from 2. of January) are averaged with
    yesterdays temperatures. This is done to follow the methodology of
    National Grid (2012): Gas demand forecasting methdolology.

    The effective temperature is half of yesterday’s effective temperature added to half of
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
    effective_temp_yh = np.zeros((365, 24), dtype="float")

    # Copy all border days
    for day in range(nr_day_to_av):
        effective_temp_yh[day] = temp_yh[day]

    # Iterate days in a year
    for day in range(365)[nr_day_to_av:]: #Skip first dates in January

        # Add todays temperature and previous effective temps
        tot_temp = temp_yh[day]

        # Add effective temperature of previous day(s)
        for i in range(nr_day_to_av):
            tot_temp = tot_temp + effective_temp_yh[day - (i+1)] #not +=

        effective_temp_yh[day] = tot_temp / (nr_day_to_av + 1)

    return effective_temp_yh

def calc_weekend_corr_f(model_yeardays_daytype, wkend_factor):
    """Based on the factor 'wkend_factor' daily correction
    factors get calculated for every modelled day in a year.abs

    Arguments
    ---------
    model_yeardays_daytype : list
        Daytype for every modelled days in the base year
    wkend_factor : float
        This factors states how much energy deamnd differs
        depending on whether a day is a weekend or working day
        (e.g. 0.8 means that on a weekend, 80% less demand occurs)

    Returns
    --------
    cdd_weekend_f : array
        Factor to multiply cdd calculations for every
        day in a year
    """
    cdd_weekend_f = np.ones((365))

    for day_nr, day in enumerate(model_yeardays_daytype):
        if day == 'holiday':
            cdd_weekend_f[day_nr] = wkend_factor

    return cdd_weekend_f

def calc_cdd(t_base_cooling, temp_yh, nr_day_to_av, crit_temp_min_max=False):
    """Calculate cooling degree days

    Arguments
    ----------
    t_base_cooling : float
        Base temperature for cooling
    temp_yh : array
        Temperatures for every hour in a year
    nr_day_to_av : array
        Number of days to average temperature

    Return
    ------
    cdd_d : array
        Contains all CDD for every day in a year (nr_of_days, 1)

    Note
    -----
    - For more info see Formual 2.1: Degree-days: theory and application
      https://www.designingbuildings.co.uk/wiki/Cooling_degree_days
    """
    if not crit_temp_min_max:
        # ---------------------------------------------
        # Average temperature with previous day(s) information
        # ---------------------------------------------
        temp_yh = effective_temps(
            temp_yh,
            nr_day_to_av)

        temp_diff = (temp_yh - t_base_cooling) / 24
        temp_diff[temp_diff < 0] = 0
        cdd_d = np.sum(temp_diff, axis=1)

    else:

        # Calculate effective temperatures
        t_min_eff = effective_temps_min_max(
            temp_yh['t_min'],
            nr_day_to_av=nr_day_to_av)

        t_max_eff = effective_temps_min_max(
            temp_yh['t_max'],
            nr_day_to_av=nr_day_to_av)

        # Calculate heating degree days
        cdd_d = calc_cdd_min_max(t_min_eff, t_max_eff, t_base_cooling)

    return cdd_d

def get_hdd_country(
        t_base_heating,
        regions,
        temp_data,
        reg_coord,
        weather_stations,
        crit_temp_min_max=False
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
            reg_coord[region]['latitude'],
            reg_coord[region]['longitude'],
            weather_stations)

        temperatures = temp_data[closest_station_id]

        hdd_reg = calc_hdd(
            t_base_heating,
            temperatures,
            nr_day_to_av=1,
            crit_temp_min_max=crit_temp_min_max)

        hdd_regions[region] = np.sum(hdd_reg)

    return hdd_regions

def get_cdd_country(
        t_base_cooling,
        regions,
        temp_data,
        reg_coord,
        weather_stations,
        crit_temp_min_max=False
    ):
    """Calculate total number of cooling degree days in a
    region for the base year

    Arguments
    ----------
    t_base_cooling : float
        Base temperature assumption
    regions : dict
        Dictionary containing regions
    temp_data : array
        Temperature data
    reg_coord : dict
        Coordinates
    weather_stations : dict
        Weather stations
    """
    cdd_regions = {}

    for region in regions:

        # Get closest weather station and temperatures
        closest_station_id = weather_station.get_closest_station(
            reg_coord[region]['latitude'],
            reg_coord[region]['longitude'],
            weather_stations)

        # Temp data
        temperatures = temp_data[closest_station_id]

        cdd_reg = calc_cdd(
            t_base_cooling,
            temperatures,
            nr_day_to_av=1,
            crit_temp_min_max=crit_temp_min_max)

        cdd_regions[region] = np.sum(cdd_reg)

    return cdd_regions

def calc_reg_hdd(
        temperatures,
        t_base_heating,
        model_yeardays,
        crit_temp_min_max=False
    ):
    """Calculate hdd for every day and daily
    yd shape of heating demand

    Arguments
    ----------
    temperatures : array
        Temperatures
    t_base_heating : float
        Base temperature for heating
    model_yeardays : dict
        Modelled yeardays

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
    hdd_d = calc_hdd(
        t_base_heating,
        temperatures,
        nr_day_to_av=1,
        crit_temp_min_max=crit_temp_min_max)

    shape_hdd_d = load_profile.abs_to_rel(hdd_d)

    # Select only modelled yeardays
    shape_hdd_d_selection = shape_hdd_d[model_yeardays]

    return hdd_d, shape_hdd_d_selection

def calc_reg_cdd(
        temperatures,
        t_base_cooling,
        model_yeardays,
        crit_temp_min_max=False
    ):
    """Calculate CDD for every day and daily yd shape of cooling demand

    Arguments
    ----------
    temperatures : array
        Temperatures
    t_base_cooling : array
        Base temperature cooling
    model_yeardays : list
        Modelled yeardays

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
    if not crit_temp_min_max:
        cdd_d = calc_cdd(
            t_base_cooling,
            temperatures,
            nr_day_to_av=1,
            crit_temp_min_max=crit_temp_min_max)

        shape_cdd_d = load_profile.abs_to_rel(cdd_d)

        # Select only modelled yeardays
        shape_cdd_d_selection = shape_cdd_d[model_yeardays]
        cdd_d_selection = cdd_d[model_yeardays]

        # If no calc_provide flat curve
        if np.sum(cdd_d_selection) == 0:
            shape_cdd_d_selection = np.full(
                (len(model_yeardays)),
                1 / len(model_yeardays))
    else:
        cdd_d = calc_cdd(
            t_base_cooling,
            temperatures,
            nr_day_to_av=1,
            crit_temp_min_max=crit_temp_min_max)

        shape_cdd_d = load_profile.abs_to_rel(cdd_d)

        # Select only modelled yeardays
        shape_cdd_d_selection = shape_cdd_d[model_yeardays]
        cdd_d_selection = cdd_d[model_yeardays]

        # If no calc_provide flat curve
        if np.sum(cdd_d_selection) == 0:
            shape_cdd_d_selection = np.full(
                (len(model_yeardays)),
                1 / len(model_yeardays))

    return cdd_d_selection, shape_cdd_d_selection
