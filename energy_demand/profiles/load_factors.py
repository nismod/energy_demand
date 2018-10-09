"""Script containing functions to calculate load factors and
also peak shifting methods which are used to implement
demand management"""
import numpy as np

def peak_shaving_max_min(
        loadfactor_yd_cy_improved,
        average_yd,
        fuel_yh,
        mode_constrained
    ):
    """Shift demand with help of load factor. All demand above
    the maximum load is shifted proportionally to all hours
    having below average demand (see Section XY).

    Arguments
    ----------
    loadfactor_yd_cy_improved : array
        Improved shifted daily load fuel
    average_yd : array
        Average load for every day in year
    fuel_yh : array
        Fuel for every hour
    mode_constrained : bool
        Running mode information

    Returns
    -------
    shifted_fuel_yh : array
        Shifted fuel

    Info
    ----
        Steps:
            - Calculate new maximum demand for every hour and fueltype
            - Calculate difference in demand to mean for every day and fueltype
            - Calculate percentage of demand for every hour with lower demand than average
            - Calculate total demand above average and shift to yh
            - Set all hours with more demand than maximum peak to maximum peak demand
    """
    # ------------------------------------------
    # Calculate new maximum demand for every day
    # and fueltype with help of newly adaped load factor
    # ------------------------------------------
    allowed_demand_max_d = average_yd / loadfactor_yd_cy_improved
    allowed_demand_max_d[np.isnan(allowed_demand_max_d)] = 0

    if mode_constrained:
        average_yd = average_yd[:, np.newaxis]
        allowed_demand_max_d = allowed_demand_max_d[:, np.newaxis]
    else:
        average_yd = average_yd[:, :, np.newaxis]
        allowed_demand_max_d = allowed_demand_max_d[:, :, np.newaxis]

    # ------------------------------------------
    # Calculate difference to daily mean for every hour
    # for every fueltype (hourly value - daily mean)
    # ------------------------------------------
    diff_to_mean = fuel_yh - average_yd

    # ------------------------
    # Calculate areas of lp below average for every day
    # all lp higher than average are set to zero
    # ------------------------
    diff_to_mean[diff_to_mean > 0] = 0
    diff_to_mean = np.abs(diff_to_mean)

    # Sum along all fueltypes the total fuels which are lp below average
    # Calculate percentage of total shiftable from above average to
    # below average for all hours which can take on fuel
    if mode_constrained:
        tot_area_below_mean = np.sum(diff_to_mean, axis=1) #one fueltype
        tot_area_below_mean = tot_area_below_mean[:, np.newaxis]
    else:
        tot_area_below_mean = np.sum(diff_to_mean, axis=2) #multiple fueltypes
        tot_area_below_mean = tot_area_below_mean[:, :, np.newaxis]

    area_below_mean_p = diff_to_mean / tot_area_below_mean
    area_below_mean_p[np.isnan(area_below_mean_p)] = 0

    # Calculate diff to newmax for every hour
    diff_to_max_demand_d = fuel_yh - allowed_demand_max_d
    diff_to_max_demand_d[diff_to_max_demand_d < 0] = 0

    # -----------------------------------------
    # Start with largest deviation to mean
    # and shift to all hours below average
    # -----------------------------------------
    # Calculate total demand which is to be shifted
    if mode_constrained:
        tot_demand_to_shift = np.sum(diff_to_max_demand_d, axis=1) # one fueltype
        tot_demand_to_shift = tot_demand_to_shift[:, np.newaxis]
    else:
        tot_demand_to_shift = np.sum(diff_to_max_demand_d, axis=2) # multiple fueltypes
        tot_demand_to_shift = tot_demand_to_shift[:, :, np.newaxis]

    # Add fuel below average:
    # Distribute shiftable demand to all hours which are below average
    # according to percentage contributing to lf which is below average
    shifted_fuel_yh = fuel_yh + (area_below_mean_p * tot_demand_to_shift)

    # Set all fuel hours whih are above max to max (substract diff)
    shifted_fuel_yh = shifted_fuel_yh - diff_to_max_demand_d

    return shifted_fuel_yh

def calc_lf_y(fuel_yh):
    """Calculate the yearly load factor for every fueltype
    by dividing the yearly average load by the peak hourly
    load in a year.

    Arguments
    ---------
    fuel_yh : array (fueltypes, 365, 24) or (fueltypes, 8760)
        Yh fuel

    Returns
    -------
    load_factor_y : array
        Yearly load factors as percentage (100% = 100)

    Note
    -----
    Load factor = average load / peak load
    https://en.wikipedia.org/wiki/Load_factor_(electrical)
    https://circuitglobe.com/load-factor.html
    """
    if fuel_yh.shape[1] == 365:
        fuel_yh_8760 = fuel_yh.reshape(fuel_yh.shape[0], 8760)
    else:
        fuel_yh_8760 = fuel_yh

    # Get total sum per fueltype
    tot_load_y = np.sum(fuel_yh_8760, axis=1)

    # Calculate maximum hour in every day of a year
    max_load_h = np.max(fuel_yh_8760, axis=1)

    # Caclualte yearly load factor for every fueltype
    with np.errstate(divide='ignore', invalid='ignore'):
        load_factor_y = (tot_load_y / 8760) / max_load_h

    load_factor_y[np.isnan(load_factor_y)] = 0

    return load_factor_y * 100

def calc_lf_y_8760(fuel_yh_8760):
    """Calculate the yearly load factor for every fueltype
    by dividing the yearly average load by the peak hourly
    load in a year.

    Arguments
    ---------
    fuel_yh_8760 : array
        Fueltypes, regions, 8760hours

    Returns
    -------
    load_factor_y : array
        Yearly load factors as percentage (100% = 100)

    Note
    -----
    Load factor = average load / peak load
    https://en.wikipedia.org/wiki/Load_factor_(electrical)
    https://circuitglobe.com/load-factor.html
    """
    # Get total sum per fueltype
    tot_load_y = np.sum(fuel_yh_8760) #, axis=2)

    # Calculate maximum hour in every day of a year
    max_load_h = np.max(fuel_yh_8760)

    # Caclualte yearly load factor for every fueltype
    with np.errstate(divide='ignore', invalid='ignore'):
        load_factor_y = (tot_load_y / 8760) / max_load_h

    if np.isnan(load_factor_y):
        load_factor_y = 0
    #load_factor_y[np.isnan(load_factor_y)] = 0

    return load_factor_y * 100

def calc_lf_season(seasons, fuel_region_yh, average_fuel_yd):
    """Calculate load factors per fueltype per region.
    The load factor is calculated based on average
    yearly load and maximum saisonal peak factor.

    Arguments
    ---------
    seasons : dict
        Seasons containing yeardays for four seasons
    fuel_region_yh : array
        Fuels
    average_fuel_yd : array
        Average fuels

    Returns
    -------
    seasons_lfs : dict
        Load factors per fueltype and season

    Note
    ----
    If not the yearly average is used for calculation,
    only the load factors within the regions are calculated.
    """
    seasons_lfs = {}
    for season, yeardays_modelled in seasons.items():

        average_fuel_yd_full_year = np.average(
            average_fuel_yd[:, ],
            axis=1)

        # Calculate maximum hour in year
        max_load_h_days_season = np.max(
            fuel_region_yh[:, yeardays_modelled],
            axis=2)

        max_load_h_season = np.max(max_load_h_days_season, axis=1)

        # Unable local RuntimeWarning: divide by zero encountered
        with np.errstate(divide='ignore', invalid='ignore'):

            #convert to percentage
            season_lf = (average_fuel_yd_full_year / max_load_h_season) * 100

        # Replace
        season_lf[np.isinf(season_lf)] = 0
        season_lf[np.isnan(season_lf)] = 0

        seasons_lfs[season] = season_lf

    return seasons_lfs

def calc_lf_d(fuel_yh, average_fuel_yd, mode_constrained):
    """Calculate the daily load factor for every day in a year
    by dividing for each day the daily average by the daily peak
    hour load. The load factor is given in %

    Arguments
    ---------
    fuel_yh : array
        Fuel for every hour in a year
    average_fuel_yd : array
        Average load per day
    mode_constrained : bool
        Mode information

    Returns
    -------
    daily_lf : array
        Laod factor calculated for every modelled day [in %]
    average_fuel_yd : array
        Average fuel for every day
    """
    # Get maximum hours in every day
    if mode_constrained:
        max_load_yd = np.max(fuel_yh, axis=1) #single fueltype
    else:
        max_load_yd = np.max(fuel_yh, axis=2) #multiple fueltypes

    # Unable local RuntimeWarning: divide by zero encountered
    with np.errstate(divide='ignore', invalid='ignore'):

        #convert to percentage
        daily_lf = (average_fuel_yd / max_load_yd) * 100

    # Replace by zero
    daily_lf[np.isinf(daily_lf)] = 0
    daily_lf[np.isnan(daily_lf)] = 0

    return daily_lf

def calc_lf_d_8760(fuel_yh):
    """Calculate the daily load factor for every day in a year
    by dividing for each day the daily average by the daily peak
    hour load. The load factor is given in %

    Arguments
    ---------
    fuel_yh : array
        Fuel for every hour in a year
    average_fuel_yd : array
        Average load per day
    mode_constrained : bool
        Mode information

    Returns
    -------
    daily_lf : array
        Laod factor calculated for every modelled day [in %]
    average_fuel_yd : array
        Average fuel for every day
    """
    # Get maximum hours in every day
    fuel_yh = fuel_yh.reshape(365, 24)
    
    max_load_yd = np.max(fuel_yh, axis=1)
    average_fuel_yd = np.average(fuel_yh, axis=1)

    # Unable local RuntimeWarning: divide by zero encountered
    with np.errstate(divide='ignore', invalid='ignore'):

        #convert to percentage
        daily_lf = (average_fuel_yd / max_load_yd) * 100

    # Replace by zero
    daily_lf[np.isinf(daily_lf)] = 0
    daily_lf[np.isnan(daily_lf)] = 0

    return daily_lf

def calc_lf_season_8760(seasons, fuel_region_yh):
    """Calculate load factors per fueltype per region.
    The load factor is calculated based on average
    yearly load and maximum saisonal peak factor.

    Arguments
    ---------
    seasons : dict
        Seasons containing yeardays for four seasons
    fuel_region_yh : array
        Fuels

    Returns
    -------
    seasons_lfs : dict
        Load factors per fueltype and season

    Note
    ----
    If not the yearly average is used for calculation,
    only the load factors within the regions are calculated.
    """
    fuel_region_yh_365_24 = fuel_region_yh.reshape(365, 24)
    seasons_lfs = {}

    for season, yeardays_modelled in seasons.items():

        average_fuel_yd = np.average(fuel_region_yh_365_24, axis=1)

        # Calculate maximum hour in year
        max_load_h_days_season = np.max(
            fuel_region_yh_365_24[yeardays_modelled], axis=1)

        max_load_h_season = np.max(max_load_h_days_season)

        # Unable local RuntimeWarning: divide by zero encountered
        with np.errstate(divide='ignore', invalid='ignore'):
            season_lf = (average_fuel_yd / max_load_h_season) * 100 #convert to percentage

        # Replace
        season_lf[np.isinf(season_lf)] = 0
        season_lf[np.isnan(season_lf)] = 0

        seasons_lfs[season] = season_lf

    return seasons_lfs
