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

        #Appliances 
        ## Lighting
        

        ## Heating
        self.e_boiler_A = e_boiler_A
        self.e_boiler_B = e_boiler_B

        # Calculate fraction of technologies
        self.e_boiler_A = get_share_sim_year(self.year, assumptions['distr_e_boiler_A']) #, baseyear, assumptions) # Input how the fraction will change over time

        # Efficiencies of technologies
        self.eff_e_boiler_A = get_efficiency_sim_year(e_boiler_A, self.year) #(eff_e_boiler_A, assumptions) # Input how much efficiency improvement over years and initial efficiency
        self.eff_e_boiler_B = get_efficiency_sim_year(e_boiler_B, self.year)

    def technological_driver_efficiencies_boilers(self):
        """calc scenario driver based on technological efficiencies and sigmoid uptake"""

        return self.e_boiler_A * self.eff_e_boiler_A + self.e_boiler_B * self.eff_e_boiler_B

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