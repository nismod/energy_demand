"""The technological stock for every simulation year"""
import math as m
import technological_stock_functions as tf

























class resid_tech_stock(object):
    """Class of a technological stock of a year of the residential model"""

    def __init__(self, year, data, assumptions, data_ext):
        """Technological stock

        Parameters
        ----------
        reg : string
            Region name or ID
        year : int
            Simulation year
        assumptions : dict
            Dictionary with all assumptions
        data_ext : dict
            Dictionary with all external data.
        """
        self.base_year = data_ext['glob_var']['base_year']
        self.end_year = data_ext['glob_var']['end_year']
        self.assumptions = assumptions
        self.year = year

        # Execute function to add all technological efficiencies as self.
        self.crate_iteration_efficiency(assumptions['eff_by'])


    def crate_iteration_efficiency(self, eff_by):
        """Iterate technology list base yeare and add to technology_stock"""
        a = {}
        for technology in eff_by:
            a[technology] = tf.eff_sy_lin(self.base_year, self.year, self.end_year, self.assumptions, technology)

        self.technologies = a
        for _ in self.technologies:
            #print("TECHNO: " + str(_))
            # Creat self objects {'key': Value}
            vars(self).update(self.technologies)



        # Calculate fraction of technologies for each end use demand
        ####self.p_boiler_A = tf.frac_sy_sigm(base_year, self.year, end_year, assumptions, 'boiler_A')
        #self.p_boiler_B = tf.frac_sy_sigm(base_year, self.year, end_year, assumptions, 'boiler_B')

        # New technologies (e.g. % der Pop...)
        ##self.p_new_tech_A = tf.frac_sy_sigm_new_technology(base_year, self.year, end_year, assumptions, 'new_tech_A')
        ##self.NEWDEMAND_tech_A = self.p_new_tech_A * 1000 # kwh

        # Technologie-mix base year of end use demand (to calculate efficiency)
        ##sh_
        
        ## Cal scenario driver of Replacement mix of current year:
        #assump_repl_sh_gas: [kohle: 0%, hydro: 50%, gas: 0%, ] --> calc for every sig diffu path



# yearly_Fuel_Demand_after_switch = change_fuel_demans(technology_stock, FUEL_ARRAY)



# EXAMPLE
#fuel_end_use_to_switch = 'space_heating_gas' # Which fuel end is to be switched
#tot_fuel_from_by = fuel_array[fueltype=gas][reg][end_use]
#tot_fuel_to_by = fuel_array[fueltype=elec][reg][end_use]   # Demand of fuel which is added
#### l(data_ext, curr_year, assumptions, eff_tech_from, eff_tech_tp, fuel_end_use_to_switch, tot_fuel_from_by, tot_fuel_to_by):
#new_demand_from_fuel, new_demand_to_fuel = tf.switch_fuel(data_ext, self.year, assumptions, self.eff_boiler_A, self.eff_boiler_B, fuel_end_use_to_switch, tot_fuel_from_by, tot_fuel_to_by)





 



         # -------------------------------
        # Share of technology for all end uses

        # Summen of irginal data table all values for (Water	Cooking	Lighting	Appliances)

        # -------------------------------$
        # Space heating	(non-HES)
        ##space_heating_cy =
        #space_heating_by = [x,x,x,x] # Percentage of fuel types
        #space_heating_cy = [x,x,x,x] # Wiht assumption on which fuel type is lowered by how much percent with which tehnology

        # ALL HES (all elec)
            # Water	
            # Cooking
            # Lighting	
            # Appliances

