"""The technological stock for every simulation year"""
import math as m
import technological_stock_functions as tf

class TechStockResid(object):
    """Class of a technological stock of a year of the residential model"""

    def __init__(self, reg, year, assumptions, data_ext):
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
        base_year = data_ext['glob_var']['base_year']
        end_year = data_ext['glob_var']['end_year']

        self.reg = reg      # Name of the region
        self.year = year    # Year


        # Efficiencies of all technologies usd in residential model

        #Appliances
        ## Lighting

        ## Heating
        # Efficiencies of technologies for simulation year ( # linear extrapolation: e.g. from 0.8 to 0.9) (was in NISMOD 1 sigmoid)
        self.eff_boiler_A = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'boiler_A')
        self.eff_boiler_B = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'boiler_B')
        self.eff_new_tech_A = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'new_tech_A')

        self.eff_tech_A = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'tech_A')
        self.eff_tech_B = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'tech_B')
        self.eff_tech_C = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'tech_C')
        self.eff_tech_A = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'tech_D')
        self.eff_tech_B = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'tech_E')
        self.eff_tech_C = tf.eff_sy_lin(base_year, self.year, end_year, assumptions, 'tech_F')

        '''boiler_gas
        boiler_oil
        boiler_condensing
        boiler_biomass
        ASHP
        HP_ground_source
        HP_air_source
        HP_gas
        micro_CHP_elec
        micro_CHP_thermal
        '''

        '''# Calculate fraction of technologies
        self.p_boiler_A = tf.frac_sy_sigm(base_year, self.year, end_year, assumptions, 'boiler_A')
        self.p_boiler_B = tf.frac_sy_sigm(base_year, self.year, end_year, assumptions, 'boiler_B')

        # New technologies (e.g. % der Pop...)
        self.p_new_tech_A = tf.frac_sy_sigm_new_technology(base_year, self.year, end_year, assumptions, 'new_tech_A')
        self.NEWDEMAND_tech_A = self.p_new_tech_A * 1000 # kwh
        '''



# yearly_Fuel_Demand_after_switch = change_fuel_demans(technology_stock, FUEL_ARRAY)

# Functions to calculate share of fuel type

# # Switch Spae Heating (oil): Tech_from   to   eff_tech_tp

'''
# EXAMPLE
fuel_end_use_to_switch = 'space_heating_gas' # Which fuel end is to be switched
tot_fuel_from_by = fuel_array[fueltype=gas][reg][end_use]
tot_fuel_to_by = fuel_array[fueltype=elec][reg][end_use]   # Demand of fuel which is added
# l(data_ext, curr_year, assumptions, eff_tech_from, eff_tech_tp, fuel_end_use_to_switch, tot_fuel_from_by, tot_fuel_to_by):
new_demand_from_fuel, new_demand_to_fuel = tf.switch_fuel(data_ext, self.year, assumptions, self.eff_boiler_A, self.eff_boiler_B, fuel_end_use_to_switch, tot_fuel_from_by, tot_fuel_to_by)

'''




 



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


        # --> Sigmoid replacement of fuel shares (e.g. replace 10% of heating (oil) with gas): Heating: Gas, 80%, oil: 10%, 10% rest)
        #heating_oil_by = 20%
        #heating_oil_cy = sigmoid(heating_oil_by, assumption_tech_heating_oil_switch)
        #heating_gas_boiler_A = (base_year_percentage, )
        #heating_hydrogen_boiler_A = 

        # With help of technology replacement assumptions, calculate how the end use is made up of technologies (calc technological stock for every year)
        # E.g. Base Year: Heitzen: 80% Gasheizung Gas Heizungen Technologie A & 20 % Heat Source pum,p, End Year: 50% Gas, 50% Heat Source pum,
        # --> Sigmoid replacement of individ technology (e.g. End use demand (e.g. heating demand) to hydrogen base demand (hydrogen boiler) for each fuel type [3/3/3/3] #[gas, elec, oil, hydrogen] 
