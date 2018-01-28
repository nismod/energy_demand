"""Load factor calculations
===========================
Script containing functions to calculate load factors and
also peak shifting methods which are used to implement
demand management
"""
import numpy as np

def peak_shaving_max_min(loadfactor_yd_cy_improved, average_yd, fuel_yh, mode_constrained):
    """Shift demand with help of load factor. All demand above
    the maximum load is shifted proportionally to all hours
    having below average demand (see Section XY)

    Arguments
    ----------
    loadfactor_yd_cy_improved : array
        Improved shifted daily load fuel
    average_yd : array
        Average load for every day in year
    fuel_yh : array
        Fuel for every hour

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

    # ------------------------------------------
    # Calculate difference to daily mean for every hour
    # for every fueltype (hourly value - daily mean)
    # ------------------------------------------
    if mode_constrained:
        diff_to_mean = fuel_yh - average_yd[:, np.newaxis]
    else:
        diff_to_mean = fuel_yh - average_yd[:, :, np.newaxis]
    

    # ------------------------
    # Calculate areas of lp below average for every day
    # ------------------------
    #all lp higher than average are set to zero
    diff_to_mean[diff_to_mean > 0] = 0
    diff_to_mean = np.abs(diff_to_mean)

    # Sum along all fueltpes the total fuels which are lp below average
    if mode_constrained:
        tot_area_below_mean = np.sum(diff_to_mean, axis=1)
    else:
        tot_area_below_mean = np.sum(diff_to_mean, axis=2)

    # Calculate percentage of total shiftable from above average to
    # below average for all hours which can take on fuel
    if mode_constrained:
         area_below_mean_p = diff_to_mean / tot_area_below_mean[ :, np.newaxis]
    else:
        area_below_mean_p = diff_to_mean / tot_area_below_mean[:, :, np.newaxis]
   
    area_below_mean_p[np.isnan(area_below_mean_p)] = 0

    # ------------------------------------------
    # Calculate diff to newmax for every hour
    # ------------------------------------------
    if mode_constrained:
        diff_to_max_demand_d = fuel_yh - allowed_demand_max_d[:, np.newaxis]
    else:
        diff_to_max_demand_d = fuel_yh - allowed_demand_max_d[:, :, np.newaxis]
    
    diff_to_max_demand_d[diff_to_max_demand_d < 0] = 0

    # -----------------------------------------
    # Start with largest deviation to mean
    # and shift to all hours below average
    # -----------------------------------------
    # Calculate total demand which is to be shifted for every fueltype
    if mode_constrained:
        tot_demand_to_shift = np.sum(diff_to_max_demand_d, axis=1)
    else:
        tot_demand_to_shift = np.sum(diff_to_max_demand_d, axis=2)
    # Add fuel below average:
    # Distribute shiftable demand to all hours which are below average
    # according to percentage contributing to lf which is below average
    #
    if mode_constrained:
        shifted_fuel_yh = fuel_yh + (area_below_mean_p * tot_demand_to_shift[:, np.newaxis])
    else:
        shifted_fuel_yh = fuel_yh + (area_below_mean_p * tot_demand_to_shift[:, :, np.newaxis])
    # Set all fuel hours whih are above max to max (substract diff)
    shifted_fuel_yh = shifted_fuel_yh - diff_to_max_demand_d

    # -----------------------
    # Plotting - compare lp
    # -----------------------
    #from energy_demand.plotting import plotting_results
    #plotting_results.plot_load_profile_dh(fuel_yh[data['lookups']['fueltypes']['electricity']2][0])
    #plotting_results.plot_load_profile_dh(shifted_fuel_yh[data['lookups']['fueltypes']['electricity']][0])
    return shifted_fuel_yh

def calc_lf_y(fuel_yh, average_fuel_yd):
    """Calculate the yearly load factor for every fueltype
    by dividing the yearly average load by the peak hourly
    load in a year.

    Arguments
    ---------
    fuel_yh : array
        Fuel for every day in year per fueltype
    average_fuel_yd : array
        Average load per day

    Returns
    -------
    load_factor_y : array
        Yearly load factors
    Note
    -----
    Load factor = average load / maximum load in given time period
    https://en.wikipedia.org/wiki/Load_factor_(electrical)
    """
    # Calculate average yearly fuel per fueltype
    average_load_y = np.average(average_fuel_yd, axis=1)

    # Calculate maximum hour in every day of a year
    max_load_h_days = np.max(fuel_yh, axis=2)
    max_load_h = np.max(max_load_h_days, axis=1)

    # Caclualte yearly load factor for every fueltype
    with np.errstate(divide='ignore', invalid='ignore'):
        load_factor_y = (average_load_y / max_load_h) * 100 #convert to percentage
    load_factor_y[np.isnan(load_factor_y)] = 0

    return load_factor_y

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

        average_fuel_yd_full_year = np.average(average_fuel_yd[:, ], axis=1)

        # Calculate maximum hour in year
        max_load_h_days_season = np.max(fuel_region_yh[:, yeardays_modelled], axis=2)
        max_load_h_season = np.max(max_load_h_days_season, axis=1)

        # Unable local RuntimeWarning: divide by zero encountered
        with np.errstate(divide='ignore', invalid='ignore'):
            season_lf = (average_fuel_yd_full_year / max_load_h_season) * 100 #convert to percentage

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

    Returns
    -------
    daily_lf : array
        Laod factor calculated for every modelled day [in %]
    average_fuel_yd : array
        Average fuel for every day
    """
    # Get maximum hours in every day
    if mode_constrained:
        #print("se")
        max_load_yd = np.max(fuel_yh, axis=1)
    else:
        max_load_yd = np.max(fuel_yh, axis=2)
    
    # Unable local RuntimeWarning: divide by zero encountered
    with np.errstate(divide='ignore', invalid='ignore'):
        #print("average_fuel_yd: " + str(average_fuel_yd.shape))
        #print("max_load_yd: " + str(max_load_yd.shape))
        #print(fuel_yh.shape)
        daily_lf = (average_fuel_yd / max_load_yd) * 100 #convert to percentage

    # Replace
    daily_lf[np.isinf(daily_lf)] = 0
    daily_lf[np.isnan(daily_lf)] = 0

    return daily_lf

'''def load_factor_d(self, data):
    """Calculate load factor of a day in a year from peak values
    """
    lf_d = np.zeros((data['lookups']['fueltypes_nr']), dtype=float)

    # Get day with maximum demand (in percentage of year)
    peak_d_demand = self.fuels_peak_d

    # Iterate fueltypes to calculate load factors for each fueltype
    for k, fueldata in enumerate(self.rs_fuels_tot_enduses_d):
        average_demand = np.sum(fueldata) / 365 # Averae_demand = yearly demand / nr of days

        if average_demand != 0:
            lf_d[k] = average_demand / peak_d_demand[k] # Calculate load factor

    lf_d = lf_d * 100 # Convert load factor to %
    return lf_d
'''