""" Functions for fuel_enduse_switch stock"""
import math as m

'''def eff_sy_lin(base_year, current_yr, year_end, assumptions, technology):
    """ Calculates lineare diffusion
    Parameters
    ----------
    base_year : float
        Base year

    Returns
    -------
    diffusion : float
        Share of fuel switch in simluation year
    """
    eff_by = assumptions['eff_by'][technology]
    eff_ey = assumptions['eff_ey'][technology]
    sim_years = year_end - base_year


    # How far the diffusion is
    diffusion = round(lineardiffusion(base_year, current_yr, eff_by, eff_ey, sim_years), 2)

    return diffusion
'''

def frac_sy_sigm(base_year, current_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate sigmoid diffusion of a fuel type share of a current year
    Parameters
    ----------
    base_year : float
        Base year
    current_yr : float
        Base year
    year_end : float
        Base year
    assumptions : float
        Base year
    fuel_enduse_switch : float
        Base year
    Returns
    -------
    fract_cy : float
        Share of fuel switch in simluation year
    """
    # Fuel share of total ED in base year
    fract_by = assumptions['fuel_type_p_by'][fuel_enduse_switch]

    # Fuel share af total ED in end year
    fract_ey = assumptions['fuel_type_p_ey'][fuel_enduse_switch]

    # Difference
    if fract_by > fract_ey:
        diff_frac = -1 * (fract_by - fract_ey) # minus
    else:
        diff_frac = fract_ey -fract_by

    # How far the diffusion has progressed
    p_of_diffusion = round(sigmoidefficiency(base_year, current_yr, year_end), 2)

    # Fraction of current year
    fract_cy = fract_by + (diff_frac * p_of_diffusion)

    return fract_cy

def lineardiffusion(base_year, current_yr, eff_by, eff_ey, sim_years):
    """This function assumes a linear fuel_enduse_switch diffusion.
    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.
    Parameters
    ----------
    current_yr : int
        The year of the current simulation.
    base_year : int
        The year of the current simulation.
    eff_by : float
        Fraction of population served with fuel_enduse_switch in base year
    eff_ey : float
        Fraction of population served with fuel_enduse_switch in end year
    sim_years : str
        Total number of simulated years.
    Returns
    -------
    fract_sy : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    if current_yr == base_year:
        fract_sy = eff_by
    else:
        fract_sy = eff_by + ((eff_ey - eff_by) / sim_years) * (current_yr - base_year)

    return fract_sy

def sigmoidefficiency(base_year, current_yr, year_end):
    """Calculates a sigmoid diffusion path of a lower to a higher value
    (saturation is assumed at the endyear)
    """
    # TODO: READ IN START AND END AND DECIDE IF NEG OR POSITIVE DIFFUSTION
    # CREATE POSITIVE AND NEGATIVE DIFFUSION
    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    y_trans = -6.0 + (12.0 / (year_end - base_year)) * (current_yr - base_year)

    sigmoidmidpoint = 0  # Can be used to shift curve to the left or right (standard value: 0)
    sigmoidsteepness = 1 # The steepness of the sigmoid curve (standard value: 1) TODO: Make as global ssumption

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    val_yr = 1 / (1 + m.exp(-1 * sigmoidsteepness * (y_trans - sigmoidmidpoint)))

    return val_yr

'''def sigmoidfuel_enduse_switchdiffusion(base_year, current_yr, saturate_year, year_invention):
    """This function assumes "S"-Curve fuel_enduse_switch diffusion (logistic function).
    The function reads in the following assumptions about the fuel_enduse_switch to calculate the
    current distribution of the simulated year:
    Parameters
    ----------
    current_yr : int
        The year of the current simulation
    saturate_year : int
        The year a fuel_enduse_switch saturaes
    year_invention : int
        The year where a fuel_enduse_switch gets on the market
    base_year : int
        Base year of simulation period
    Returns
    -------
    val_yr : float
        The fraction of the fuel_enduse_switch in the simulation year
    """
    # Check how many years fuel_enduse_switch in the market
    if current_yr < year_invention:
        val_yr = 0
        return val_yr
    else:
        if current_yr >= saturate_year:
            years_availalbe = saturate_year - base_year
        else:
            years_availalbe = current_yr - year_invention

    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    print("years_availalbe: " + str(years_availalbe))
    year_translated = -6 + ((12 / (saturate_year - year_invention)) * years_availalbe)

    # Convert x-value into y value on sigmoid curve reaching from -6 to 6
    sigmoidmidpoint = 0  # Can be used to shift curve to the left or right (standard value: 0)
    sigmoidsteepness = 1 # The steepness of the sigmoid curve (standard value: 1)

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    val_yr = 1 / (1 + m.exp(-1 * sigmoidsteepness * (year_translated - sigmoidmidpoint)))

    return val_yr
'''

'''def frac_sy_sigm_new_fuel_enduse_switch(base_year, current_yr, year_end, assumptions, fuel_enduse_switch):
    """ Calculate share of a fuel_enduse_switch in a year based on assumptions
        Parameters
        ----------
        base_year : float
            Base year
        current_yr : float
            Base year
        year_end : float
            Base year
        assumptions : float
            Base year
        fuel_enduse_switch : float
            The end use energy demand of a fueltype (e.g. space_heating_gas)
        Out:
    """
    fract_by = assumptions['p_tech_by'][fuel_enduse_switch]
    fract_ey = assumptions['p_tech_ey'][fuel_enduse_switch]
    market_year = assumptions['tech_market_year'][fuel_enduse_switch]
    saturation_year = assumptions['tech_saturation_year'][fuel_enduse_switch]
    # EV: MAX_SHARE POSSIBLE
    #max_possible
    # How far the fuel_enduse_switch has diffused
    p_of_diffusion = round(sigmoidfuel_enduse_switchdiffusion(base_year, current_yr, saturation_year, market_year), 2)
    print("p_of_diffusion: " + str(p_of_diffusion))
    #fract_cy = p_of_diffusion * max_possible
    return p_of_diffusion
'''
