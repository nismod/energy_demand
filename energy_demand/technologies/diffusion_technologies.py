"""Funtions related to the diffusion of technologies
"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import math
import numpy as np
from scipy.optimize import curve_fit
from energy_demand.plotting import plotting_program as plotting

def linear_diff(base_yr, curr_yr, value_start, value_end, sim_years):
    """This function assumes a linear diffusion

    Parameters
    ----------
    base_yr : int
        The year of the current simulation.
    curr_yr : int
        The year of the current simulation.
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    sim_years : str
        Total number of simulated years.

    Returns
    -------
    fract_sy : float
        The fraction in the simulation year

    Note
    ----
    - returns ``value_start`` if no change or ``curr_yr`` == ``base_yr``
    """
    # If current year is base year, return zero
    if curr_yr == base_yr or sim_years == 0: #SHARK or value_end == value_start:
        fract_sy = 0 #value_start #0 SHARK
    else:
        #-1 because in base year no change
        fract_sy = ((value_end - value_start) / (sim_years - 1)) * (curr_yr - base_yr)

    return fract_sy

def sigmoid_function(x_value, l_value, midpoint, steepness):
    """Sigmoid function

    Paramters
    ---------
    x_value : float
        X-Value
    l_value : float
        The curv'es maximum value
    midpoint : float
        The midpoint x-value of the sigmoid's midpoint
    k : dict
        The steepness of the curve

    Return
    ------
    y : float
        Y-Value

    Notes
    -----
    This function is used for fitting and plotting

    """
    y_value = l_value / (1 + np.exp(-steepness * ((x_value - 2000) - midpoint)))

    return y_value

def sigmoid_diffusion(base_yr, curr_yr, end_yr, sig_midpoint, sig_steeppness):
    """Calculates a sigmoid diffusion path of a lower to a higher value with
    assumed saturation at the end year

    Parameters
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
    sig_steeppness : float
        Steepness of sigmoid diffusion function The steepness of the
        sigmoid curve (standard value: 1)

    Returns
    -------
    cy_p : float
        The fraction of the diffusion in the current year

    Note
    ----
    It is always assuemed that for the simulation year the share is
    replaced with technologies having the efficencies of the current year. For technologies
    which get replaced fast (e.g. lightbulb) this is corret assumption, for longer lasting
    technologies, this is more problematic (in this case, over every year would need to be iterated
    and calculate share replaced with efficiency of technology in each year).

    TODO: Always return positive value. Needs to be considered for changes in negative
    """
    if curr_yr == base_yr:
        return 0
    elif curr_yr == end_yr:
        return 1
    else:
        # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
        if end_yr == base_yr:
            y_trans = 5.0
        else:
            y_trans = -5.0 + (10.0 / (end_yr - base_yr)) * (curr_yr - base_yr)

        # Get a value between 0 and 1 (sigmoid curve ranging from 0 to 1)
        cy_p = 1.0 / (1 + math.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

        return cy_p
