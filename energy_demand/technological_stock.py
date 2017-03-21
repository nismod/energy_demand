"""The technological stock for every simulation year"""
import math as m
import technological_stock_functions as tf

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model

    The main class of the residential model. For every region, a Region Object needs to be generated.

    Parameters
    ----------
    data : dict
        tbd
    data_ext : dict
        tbd
    """
    def __init__(self, assumptions, data_ext):
        """Constructor of technologies for residential sector"""

        self.base_year = data_ext['glob_var']['base_year']
        self.end_year = data_ext['glob_var']['end_year']
        self.assumptions = assumptions
        self.current_year = data_ext['glob_var']['current_year']

        # Execute function to add all technological efficiencies as self argument
        self.crate_iteration_efficiency()

    def crate_iteration_efficiency(self):
        """Iterate technology list base yeare and add to technology_stock

        The efficiency of each technology is added as `self` Attribute
        Based on assumptions of theoretical maximum efficiency gaing of
        each technology and the actual achieved efficiency, the efficiency
        of the current year is calculated based on a linear diffusion

        Example
        -------
        Technology X is projected to have maximum potential efficiency increase
        from 0.5 to a 1.00 efficiency. If however, the acutal efficiency gain
        is only 50%, then after the simulation, an efficiency of 0.75 is reached
        """
        eff_dict = {}
        technology_list = self.assumptions['eff_by']

        for technology in technology_list:

            eff_by = self.assumptions['eff_by'][technology]
            eff_ey = self.assumptions['eff_ey'][technology]
            sim_years = self.end_year - self.base_year

            # Theoretical maximum efficiency potential if theoretical maximum is linearly calculated
            theor_max_eff = round(tf.lineardiffusion(self.base_year, self.current_year, eff_by, eff_ey, sim_years), 2)

            # Get assmuption how much of efficiency potential is reaped
            achieved_eff = self.assumptions['eff_achieved'][technology]

            # Actual efficiency potential
            eff_dict[technology] = achieved_eff * theor_max_eff # Efficiency gain assumption achieved * theoretically maximum achieveable efficiency gain

        self.technologies = eff_dict
        for _ in self.technologies:
            vars(self).update(self.technologies) # Creat self objects {'key': Value}
