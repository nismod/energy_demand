"""The technological stock for every simulation year"""
import math as m
import technological_stock_functions as tf

class ResidTechStock(object):
    """Class of a technological stock of a year of the residential model"""

    def __init__(self, data, data_ext):
        """Constructor of technologies for residential sector"""

        self.base_year = data_ext['glob_var']['base_year']  # Base year
        self.end_year = data_ext['glob_var']['end_year']    # End year
        self.assumptions = data['assumptions']                      # assumptions
        self.current_year = data_ext['glob_var']['current_year']                    # current year

        # Execute function to add all technological efficiencies as self.
        self.crate_iteration_efficiency()

    def crate_iteration_efficiency(self):
        """Iterate technology list base yeare and add to technology_stock"""
        eff_dict = {}
        eff_by = self.assumptions['eff_by']
        for technology in eff_by:
            eff_dict[technology] = tf.eff_sy_lin(self.base_year, self.current_year, self.end_year, self.assumptions, technology)

        self.technologies = eff_dict
        for _ in self.technologies:
            vars(self).update(self.technologies) # Creat self objects {'key': Value}
