"""Load factor calculations

#TODO: DOCUMENTATION

"""
import numpy as np
from energy_demand.plotting import plotting_results

def peak_shaving_max_min(loadfactor_yd_cy_improved, average_yd, fuel_yh):
    """Shift demand with help of load factor. All demand above
    the maximum load is shifted proportionally to all hours
    having below average demand (see Section XY)

    Arguments
    ----------
    loadfactor_yd_cy_improved : array
        Improved shifted daily load fuel
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

    ##tot_area_above_mean = np.sum(diff_to_mean[diff_to_mean > 0])
    ##tot_area_below_mean = np.sum(diff_to_mean[diff_to_mean < 0])
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
    # Distribute shiftable demand to all hours which are below
    # average according to percentage contributing to lf which
    # is below average
    shifted_fuel_yh = fuel_yh + (area_below_mean_p * tot_demand_to_shift[:, :, np.newaxis])

    # Set all fuel hours whih are above max to max (substract diff)
    shifted_fuel_yh = shifted_fuel_yh - diff_to_new_daily_max

    # Plotting - compare lp
    #plotting_results.plot_load_profile_dh(fuel_yh[2][0])
    #plotting_results.plot_load_profile_dh(shifted_fuel_yh[2][0])

    return shifted_fuel_yh

def calc_lf_y(fuel_yh_input):
    """Calculate the yearly load factor
    for a full year
    Calculate load factor of a h in a year
    from peak data (peak hour compared to all hours in a year)

    Note
    -----
    Load factor = average load / maximum load in given time period
    https://en.wikipedia.org/wiki/Load_factor_(electrical)

    Combined Heating, Cooling & Power Handbook: Technologies & 
    https://books.google.co.uk/books?id=hA129h8dc1AC&pg=PA421&lpg=PA421&dq=load+factor+handbook+electricity&source=bl&ots=yQt-VBL9PP&sig=NaW4Y1jW4R4AH8yCS6hhuont9hQ&hl=en&sa=X&ved=0ahUKEwj2nMTKiozXAhVHExoKHaxXCeMQ6AEIKDAA#v=onepage&q=load%20factor%20handbook%20electricity&f=false


    """
    # Calculate average yearly fuel per fueltype
    average_load_y_days = np.average(fuel_yh_input, axis=1)
    average_load_y = np.average(average_load_y_days, axis=1)

    # total_fuel_y

    # Calculate maximum hour in year
    max_load_h_days = np.max(fuel_yh_input, axis=2)
    max_load_h = np.max(max_load_h_days, axis=1)

    # Caclualte yearly load factor for every fueltype
    yearly_lf = average_load_y / max_load_h
    yearly_lf[np.isnan(yearly_lf)] = 0

    return yearly_lf

def calc_lf_d(fuel_yh_input):
    """Calculate the daily load factor for
    every day in a year

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
    average_fuel_yd = np.mean(fuel_yh_input, axis=2)

    # Get maximum hours in every day
    max_load_yd = np.max(fuel_yh_input, axis=2)

    daily_lf = average_fuel_yd / max_load_yd

    # Replace
    daily_lf[np.isinf(daily_lf)] = 0
    daily_lf[np.isnan(daily_lf)] = 0

    # MAYBE: # Convert load factor to %

    return daily_lf, average_fuel_yd

'''def load_factor_d_non_peak(self, data):
    """Calculate load factor of a day in a year from non-peak data
    self.fuels_peak_d     :   Fuels for peak day (fueltype, data)
    self.rs_fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

    Return
    ------
    lf_d : array
            Array with load factor for every fuel type in %

    Note
    -----
    Load factor = average load / maximum load in given time period

    https://en.wikipedia.org/wiki/Load_factor_(electrical)
    """
    lf_d = np.zeros((data['lookups']['fueltypes_nr']))

    # Iterate fueltypes to calculate load factors for each fueltype
    for k, fueldata in enumerate(self.rs_fuels_tot_enduses_d):

        average_demand = sum(fueldata) / 365 # Averae_demand = yearly demand / nr of days
        max_demand_d = max(fueldata)

        if  max_demand_d != 0:
            lf_d[k] = average_demand / max_demand_d # Calculate load factor

    lf_d = lf_d * 100 # Convert load factor to %

    return lf_d
'''

def load_factor_h_non_peak(data, fueltypes_nr, fuels_tot_enduses_h, rs_fuels_peak_h): #data['lookups']['fueltypes_nr'
    """Calculate load factor of a h in a year from non-peak data

    self.rs_fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

    Return
    ------
    load_factor_h : array
        Array with load factor for every fuel type [in %]

    Note
    -----
    Load factor = average load / maximum load in given time period

    https://en.wikipedia.org/wiki/Load_factor_(electrical)
    """
    load_factor_h = np.zeros((fueltypes_nr), dtype=float) # Initialise array to store fuel

    # Iterate fueltypes to calculate load factors for each fueltype
    for fueltype, fueldata in enumerate(fuels_tot_enduses_h):

        '''all_hours = []
        for day_hours in self.fuels_tot_enduses_h[fueltype]:
                for h in day_hours:
                    all_hours.append(h)
        maximum_h_of_day_in_year = max(all_hours)
        '''
        maximum_h_of_day_in_year = rs_fuels_peak_h[fueltype]

        average_demand_h = np.sum(fueldata) / 8760 # Averae load = yearly demand / nr of days

        # If there is a maximum day hour
        if maximum_h_of_day_in_year != 0:
            load_factor_h[fueltype] = average_demand_h / maximum_h_of_day_in_year # Calculate load factor

    # Convert load factor to %
    load_factor_h *= 100

    return load_factor_h

def load_factor_d(self, data):
    """Calculate load factor of a day in a year from peak values

    Arguments
    -----------
    data

    Retrn
    ------
    lf_d : array
            Array with load factor for every fuel type in %

    Note
    -----
    - Load factor = average load / maximum load in given time period

    - https://en.wikipedia.org/wiki/Load_factor_(electrical)
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
