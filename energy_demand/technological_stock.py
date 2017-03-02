"""The technological stock for every simulation year"""
import math as m

class TechnologicalStock(object):
    """Class of a technological stock of a year"""

    def __init__(self, reg, year, assumptions, e_boiler_A, e_boiler_B):
        """Technological stock

        Parameters
        ----------
        coordinates : float
            coordinates

        """
        self.reg = reg
        self.year = year
        self.assumptions = assumptions

        # Residential
        self.e_boiler_A = e_boiler_A
        self.e_boiler_B = e_boiler_B


        # Fraction of technologies
        self.e_boiler_A = get_share_sim_year(self.year, assumptions['distr_e_boiler_A']) #, baseyear, assumptions) # Input how the fraction will change over time

        # Efficiencies of technologies
        self.eff_e_boiler_A = get_efficiency_sim_year(e_boiler_A, self.year) #(eff_e_boiler_A, assumptions) # Input how much efficiency improvement over years and initial efficiency
        self.eff_e_boiler_B = get_efficiency_sim_year(e_boiler_B, self.year)

    def technological_driver_efficiencies_boilers(self):
        """calc scenario driver based on technological efficiencies and sigmoid uptake"""

        return self.e_boiler_A * self.eff_e_boiler_A +  self.e_boiler_B * self.eff_e_boiler_B

'''def get_share_sim_year(year, technology_distr_assump):

    year_step1 = technology_distr_assump['year_step1']
    year_base = technology_distr_assump['base']

    base_year = 2015
    sim_years = 50 # number of simulated years


    return efficiency

'''

assumptions = { 'distr_e_boiler_A': {'base': 0.8, 'year_step1': 0.9},
                'distr_e_boiler_B': {'base': 0.2, 'year_step1': 0.05},
                'distr_g_boiler_D': {'base': 0.0, 'year_step1': 0.05},
                }


def linearDiffusion(current_year, base_year, fract_by, fract_ey, sim_years):
    """This function assumes a linear technology diffusion.

    All necessary data to run energy demand model is loaded.
    This data is loaded in the wrapper.

    Parameters
    ----------
    current_year : int
        The year of the current simulation.

    base_year : int
        The year of the current simulation.

    fract_by : float
        Fraction of population served with technology in base year

    fract_ey : float
        Fraction of population served with technology in end year

    sim_years : str
        Total number of simulated years.

    Returns
    -------
    fract_sy : float
        The fraction of the technology in the simulation year

    """
    if current_year == base_year:
        fract_sy = fract_by
    else:
        fract_sy = fract_by + ((fract_ey - fract_by) / sim_years) * (current_year - base_year)

    return fract_sy


def sigmoidEfficiencyPos(base_year, year_end, current_year):
    """Calculates a sigmoid diffusion path of a lower to a higher value (saturation is assumed at the endyear)"""

    # TODO: READ IN START AND END AND DECIDE IF NEG OR POSITIVE DIFFUSTION
    # CREATE POSITIVE AND NEGATIVE DIFFUSION
    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    y_trans = -6 + (12 /(year_end - base_year) * (current_year - base_year))

    # Convert x-value into y value on sigmoid curve reaching from -6 to 6
    sigmoidmidpoint = 0  # Can be used to shift curve to the left or right (standard value: 0)
    sigmoidsteepness = 1 # The steepness of the sigmoid curve (standard value: 1)

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    val_yr = 1 / (1 + m.exp(-1 * sigmoidsteepness * (y_trans - sigmoidmidpoint)))

    return val_yr

def sigmoidTechnologyDiffusion(current_year, saturate_year, year_invention, base_year):
    """This function assumes "S"-Curve technology diffusion (logistic function).

    The function reads in the following assumptions about the technology to calculate the
    current distribution of the simulated year:

    Parameters
    ----------
    current_year : int
        The year of the current simulation

    saturate_year : int
        The year a technology saturaes

    year_invention : int
        The year where a technology gets on the market

    base_year : int
        Base year of simulation period

    Returns
    -------
    val_yr : float
        The fraction of the technology in the simulation year
    """
    # Check how many years technology in the market
    if current_year < year_invention:
        val_yr = 0
        return val_yr
    else:
        if current_year >= saturate_year:
            years_availalbe = saturate_year - base_year
        else:
            years_availalbe = current_year - year_invention

    # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
    year_translated = -6 + (12/(saturate_year - year_invention)) * years_availalbe

    # Convert x-value into y value on sigmoid curve reaching from -6 to 6
    sigmoidmidpoint = 0  # Can be used to shift curve to the left or right (standard value: 0)
    sigmoidsteepness = 1 # The steepness of the sigmoid curve (standard value: 1)

    # Get a value between 0 and 1 (sigmoid curve ranging vrom 0 to 1)
    val_yr = 1 / (1 + m.exp(-1 * sigmoidsteepness * (year_translated - sigmoidmidpoint)))

    return val_yr

for i in range(2015, 2050):
    print("year: " + str(i) + "  " + str(sigmoidTechnologyDiffusion(i, 2100, 2020, 2015)))
