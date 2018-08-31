"""Funtions related to the diffusion of technologies
"""
import math
import numpy as np

def linear_diff(base_yr, curr_yr, value_start, value_end, yr_until_changed):
    """Calculate a linear diffusion for a current year. If
    the current year is identical to the base year, the
    start value is returned

    Arguments
    ----------
    base_yr : int
        The year of the current simulation
    curr_yr : int
        The year of the current simulation
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    yr_until_changed : str
        Year until changed is fully implemented

    Returns
    -------
    fract_cy : float
        The fraction in the simulation year
    """
    # Total number of simulated years
    sim_years = yr_until_changed - base_yr  + 1

    if curr_yr == base_yr or sim_years == 0 or value_end == value_start:
        fract_cy = value_start
    else:
        #-1 because in base year no change
        fract_cy = ((value_end - value_start) / (sim_years - 1)) * (curr_yr - base_yr) + value_start

    return fract_cy

def sigmoid_function(x_value, l_value, midpoint, steepness):
    """Sigmoid function used for fitting and plotting.

    Arguments
    ---------
    x_value : float
        X-Value
    l_value : float
        The curv'es maximum value
    midpoint : float
        The midpoint x-value of the sigmoid's midpoint
    steepness : dict
        The steepness of the curve

    Return
    ------
    y-value : float
        Y-Value

    Warning
    -------
    Because 2000 is substracted, the start year can not be before 2001.
    """
    return l_value / (1 + np.exp(-steepness * ((x_value - 2000.0) - midpoint)))

def sigmoid_diffusion(
        base_yr,
        curr_yr,
        end_yr,
        sig_midpoint,
        sig_steepness
    ):
    """Calculates a sigmoid diffusion path of a lower to a higher value with
    assumed saturation at the end year

    Arguments
    ----------
    base_yr : int
        Base year of simulation period
    curr_yr : int
        The year of the current simulation
    end_yr : int
        The year a fuel_enduse_switch saturaes
    sig_midpoint : float
        Mid point of sigmoid diffusion function can be used to shift
        curve to the left or right (standard value: 0)
    sig_steepness : float
        Steepness of sigmoid diffusion function The steepness of the
        sigmoid curve (standard value: 1)

    Returns
    -------
    cy_p : float
        The fraction of the diffusion in the current year

    Note
    ----
    It is always assuemed that for the simulation year the share is
    replaced with technologies having the efficencies of the current year.
    For technologies which get replaced fast (e.g. lightbulb) this
    is corret assumption, for longer lasting technologies, this is
    more problematic (in this case, over every year would need to be iterated
    and calculate share replaced with efficiency of technology in each year).

    Always returns positive value. Needs to be considered for changes in negative
    """
    if curr_yr == base_yr:
        return float(0)
    elif curr_yr == end_yr:
        return float(1)
    else:
        # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
        if end_yr == base_yr:
            y_trans = 5.0
        else:
            y_trans = -5.0 + (10.0 / (end_yr - base_yr)) * (curr_yr - base_yr)

        # Get a value between 0 and 1 (sigmoid curve ranging from 0 to 1)
        cy_p = 1.0 / (1 + math.exp(-1 * sig_steepness * (y_trans - sig_midpoint)))

        return float(cy_p)
