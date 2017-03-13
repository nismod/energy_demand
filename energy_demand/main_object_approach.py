import sys
import os
import csv
import traceback
import datetime
from datetime import date
from datetime import timedelta as td
import numpy as np

import energy_demand.main_functions as mf
import energy_demand.building_stock_generator as bg
import energy_demand.assumptions as assumpt
from energy_demand import residential_model
import energy_demand.technological_stock as ts
import energy_demand.technological_stock_functions as tf
# pylint: disable=I0011,C0321,C0301,C0103, C0325

# Dict for every end_use with
#    - Scenario Drivers
#    - All shapes
#    - All Demand switches



class Region(object):
    """ Class of region """

    # Constructor (initialise class)
    def __init__(self, reg_name, data, data_ext, ass):
        self.reg_name = reg_name                                            # Name/ID of region
        self.data = data
        self.data_ext = data_ext
        self.ass = ass
        #self.floor_area = floor_area

        self.assumptions = ass                                              # Improve: Assumptions per region
        self.current_year = data_ext['glob_var']['current_year']            # Current year
        self.fueldata_reg = data['fueldata_disagg'][reg_name]               # Fuel array of region
        self.pop = data_ext['population'][self.current_year][self.reg_name] # Population of current year



        # Functions in constructor
        self.create_end_use_objects()     # Add end uses and fuel to region


        
        #self.SHAPES_ASSUMPTIONS
        # ...
        self.fuels_new = self.sum_all_fuels_over_appliances()


    # Functions within class
    def create_end_use_objects(self):
        """Initialises all defined end uses. Adds an object for each end use to the Region class"""
        a = {}
        for enduse_name in self.fueldata_reg:
            a[enduse_name] = EndUse_Class(self.current_year, self.data, self.data_ext, enduse_name, self.assumptions, self.fueldata_reg)
        self.end_uses = a
        for i in self.end_uses:
            # Creat self objects {'key': Value}
            vars(self).update(self.end_uses)

    # Sum yearly
    def sum_all_fuels_over_appliances(self):
        '''Summen all appliances'''
        pass

    # Sum hourly







class EndUse_Class(Region):
    """Energy end use"""

    def __init__(self, year, data, data_ext, enduse_name, ass, fueldata_reg):

        self.enduse_name = enduse_name                              # EndUse Name

        # from parent class
        self.year = year
        self.data = data
        self.data_ext = data_ext
        self.assumptions = ass                                      #ASsumptions from regions
        self.fueldata_reg = fueldata_reg[self.enduse_name]              # FUEL DATA OF ONE USE

        # Calculate fuel switches
        self.fuel_data_reg_after_switch = self.fuel_switches()


        self.fuel_data_reg_after_scenario_driver_yearly = self.scenario_driver_for_each_enduse()
        self.fuel_data_daily = self.from_yearly_to_daily()
        self.self_fuel_data_hourly = self.from_daily_to_hourly()
        self.peak_daily = self.peak_daily()
        self.peak_hourly = self.peak_hourly()

    # Fuel Switches. Get new Fuels after switch
    def fuel_switches(self):
        """Calculates absolute fuel changes from switches in changes of fuel percentages

        considers also technological changes
        """

        # Build in Criteria if switch is executed TO
        fuel_p_by = self.assumptions['fuel_type_p_by'][self.enduse_name] # Base year fuel percentages
        fuel_p_ey = self.assumptions['fuel_type_p_ey'][self.enduse_name] # End year fuel percentages
        #print("fuel_p_by: " + str(fuel_p_by))
        #print("fuel_p_ey: " + str(fuel_p_ey))

        if np.array_equal(fuel_p_by, fuel_p_ey): # If no fuel switches:
            print("No Fuel Switches (same perentages)")
            return self.fueldata_reg
        else:
            print("Fuel is switched in Enduse: "  + str(self.enduse_name))
            tech_install = self.assumptions['tech_install'][self.enduse_name]                       #  Technology which is installed
            replacement_dict_simple = self.assumptions['replacement_dict_simple'][self.enduse_name] #  Efficiens of current echnologes to be rplaced

            end_year = self.data_ext['glob_var']['end_year']
            base_year = self.data_ext['glob_var']['base_year']

            # Out_dict initialisation
            out_fuel_array = np.copy((self.fueldata_reg))

            # Calculate percentage differences over full simulation period EndUse_Class
            fuel_diff = fuel_p_ey[:, 1:] - fuel_p_by[:, 1:] # difference in percentage (ID gets wasted because it is substracted)

            # Calculate sigmoid diffusion of fuel switches
            fuel_p_cy = fuel_diff * tf.sigmoidefficiency(base_year, self.year, end_year)
            print("fuel_p_cy:" + str(fuel_p_cy))
            print("fuel_p_ey:" + str(fuel_p_ey))

            # Differences in absolute fuel without technologies
            absolute_fuel_diff = self.fueldata_reg * fuel_p_cy # Multiply fuel by percentage changes

            # Technology stock
            technologies_year = ts.resid_tech_stock(self.year, self.data, self.assumptions, self.data_ext) # Generate technology stock
            eff_replacement = getattr(technologies_year, tech_install)

            print("Technology which is installed:           " + str(tech_install))
            print("Efficiency of technology to be installed " + str(eff_replacement))
            print("Current Year:" + str(self.year))

            fuel_type = 0
            for fuel_change in absolute_fuel_diff:

                # Get efficiency of technology to be replaced
                tech_replace = replacement_dict_simple[fuel_type]

                eff_tech_remove = getattr(technologies_year, tech_replace)                                # Get efficiency

                # Fuel factor
                new_fuel_factor = (eff_tech_remove / eff_replacement)   #TODO ev. auch umgekehrt 
                print("Technology fuel factor difference: " + str(eff_tech_remove) + "   " + str(eff_replacement) + "  " + str(new_fuel_factor))
                new_fuel_considering_efficiency = fuel_change * new_fuel_factor

                # Add  fuels (if minus, no technology weighting is necessary)
                if fuel_change > 0:
                    out_fuel_array[int(fuel_type)] += new_fuel_considering_efficiency
                fuel_type += 1

            #print("Old Fuel: " + str(self.fueldata_reg))
            #print("--")
            #print("New Fuel: " + str(out_fuel_array))
            return out_fuel_array

    def scenario_driver_for_each_enduse(self):
        pass

    def from_yearly_to_daily(self):
        #Get from dict for every end_use:
        pass

    def from_daily_to_hourly(self):
        #Get from dict for every end_use:
        pass

    def peak_daily(self):
        pass

    def peak_hourly(self):
        pass





# ----------------------------------------

def test_run_new_model(data, data_ext, assumptions):

    # Now the data needs to look like
    # ----------------------------------------
    #data['fueldata_disagg'] = {0:, data['data_residential_by_fuel_end_uses']} #test_fuel_disaggregated

    #assumptions = {0: assumptions, 1: assumptions, 2: assumptions} # ASsumptions per region
    #print (assumptions)


    tech_stock = ts.resid_tech_stock(2015, data, assumptions, data_ext) #TODO ASSUMPTIONS

    data['tech_stock'] = tech_stock

    # Iterate regions
    for reg in data['reg_lu']:
            print("Region: " + str(reg))

            # Residential
            a = Region(reg, data, data_ext, assumptions)

            print(a.cooking)

            print(len(a.end_uses))
            #prnt("..")
            #return

