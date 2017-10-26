"""Load factor calculations
===========================
Script containing functions to calculate load factors and
also peak shifting methods which are used to implement
demand management
"""
import numpy as np

def peak_shaving_max_min(loadfactor_yd_cy_improved, average_yd, fuel_yh):
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
    max_daily_demand_allowed = average_yd / loadfactor_yd_cy_improved
    max_daily_demand_allowed[np.isnan(max_daily_demand_allowed)] = 0

    # ------------------------------------------
    # Calculate difference to daily mean for every hour
    # for every fueltype (hourly value - daily mean)
    # ------------------------------------------
    diff_to_mean = fuel_yh - average_yd[:, :, np.newaxis]

    # ------------------------
    # Calculate areas of lp below average for every day
    # ------------------------
    #all lp higher than average are set to zero
    diff_to_mean[diff_to_mean > 0] = 0
    diff_to_mean = np.abs(diff_to_mean)

    # Sum along all fueltpes the total fuels which are lp below average
    tot_area_below_mean = np.sum(diff_to_mean, axis=2)

    # Calculate percentage of total shiftable from above average to
    # below average for all hours which can take on fuel
    area_below_mean_p = diff_to_mean / tot_area_below_mean[:, :, np.newaxis]
    area_below_mean_p[np.isnan(area_below_mean_p)] = 0

    # ------------------------------------------
    # Calculate diff to newmax for every hour
    # ------------------------------------------
    diff_to_new_daily_max = fuel_yh - max_daily_demand_allowed[:, :, np.newaxis]
    diff_to_new_daily_max[diff_to_new_daily_max < 0] = 0

    # -----------------------------------------
    # Start with largest deviation to mean
    # and shift to all hours below average
    # -----------------------------------------
    # Calculate total demand which is to be shifted for every fueltype
    tot_demand_to_shift = np.sum(diff_to_new_daily_max, axis=2)

    # Add fuel below average:
    # Distribute shiftable demand to all hours which are below average
    # according to percentage contributing to lf which is below average
    shifted_fuel_yh = fuel_yh + (area_below_mean_p * tot_demand_to_shift[:, :, np.newaxis])

    # Set all fuel hours whih are above max to max (substract diff)
    shifted_fuel_yh = shifted_fuel_yh - diff_to_new_daily_max

    # -----------------------
    # Plotting - compare lp
    # -----------------------
    #from energy_demand.plotting import plotting_results
    #plotting_results.plot_load_profile_dh(fuel_yh[2][0])
    #plotting_results.plot_load_profile_dh(shifted_fuel_yh[2][0])
    return shifted_fuel_yh

def calc_lf_y(fuel_yh):
    """Calculate the yearly load factor by dividing
    the yearly average load by the peak hourly load
    in a year

    Arguments
    ---------
    fuel_yh : array
        Fuel for every day in year per fueltype

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
    average_load_y_days = np.average(fuel_yh, axis=1)
    average_load_y = np.average(average_load_y_days, axis=1)

    # Calculate maximum hour in year
    max_load_h_days = np.max(fuel_yh, axis=2)
    max_load_h = np.max(max_load_h_days, axis=1)

    # Caclualte yearly load factor for every fueltype
    load_factor_y = average_load_y / max_load_h
    load_factor_y[np.isnan(load_factor_y)] = 0

    return load_factor_y

def calc_lf_d(fuel_yh):
    """Calculate the daily load factor for every day in a year
    by dividing for each day the daily average by the daily peak
    hour load.

    # SHARK: Convert load factor to %

    Arguments
    ---------
    fuel_yh : array
        Fuel for every hour in a year

    Returns
    -------
    daily_lf : array
        Laod factor calculated for every modelled day
    average_fuel_yd : array
        Average fuel for every day
    """
    # Calculate average load for every day
    average_fuel_yd = np.mean(fuel_yh, axis=2)

    # Get maximum hours in every day
    max_load_yd = np.max(fuel_yh, axis=2)

    daily_lf = average_fuel_yd / max_load_yd

    # Replace
    daily_lf[np.isinf(daily_lf)] = 0
    daily_lf[np.isnan(daily_lf)] = 0
    
    return daily_lf, average_fuel_yd

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