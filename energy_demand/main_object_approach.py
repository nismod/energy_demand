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

    def __init__(self, reg_name, data, data_ext, assumption):
        """ Constructor. Initialising different methods"""
        self.reg_name = reg_name                                            # Name/ID of region
        self.data = data
        self.data_ext = data_ext
        self.assumptions = assumption                                       # Improve: Assumptions per region

        self.current_year = data_ext['glob_var']['current_year']            # Current year
        self.fueldata_reg = data['fueldata_disagg'][reg_name]               # Fuel array of region
        #self.pop = data_ext['population'][self.current_year][self.reg_name] # Population of current year

        # Create all end use attributes
        self.create_end_use_objects()     # Add end uses and fuel to region


        # Sum final fuels of all end_uses
        self.fuels_new = self.sum_final_fuels_over_all_end_uses()

    # Functions within class
    # ----------------------
    def create_end_use_objects(self):
        """Initialises all defined end uses. Adds an object for each end use to the Region class"""
        a = {}
        for enduse_name in self.fueldata_reg:
            a[enduse_name] = EndUseClassResid(self.current_year, self.data, self.data_ext, enduse_name, self.assumptions, self.fueldata_reg)
        self.end_uses = a
        for _ in self.end_uses:
            vars(self).update(self.end_uses)     # Creat self objects {'key': Value}


    # Sum hourly


    def sum_final_fuels_over_all_end_uses(self):
        '''Summen all fuel types over all end uses'''

        # Initialise empty array to store fuel
        summary_fuel = np.empty((len(self.data['fuel_type_lu']), 1))

        for enduse_name in self.fueldata_reg:
            fuel_end_use = self.__getattr__subclass__(enduse_name, 'reg_fuel_after_switch') #TODO: Replace reg_fuel_after_switch with Final Energy Demand from end_use_class
            summary_fuel += fuel_end_use
        return summary_fuel

    def __getattr__(self, attr):
        """ Get method of own object"""
        return self.attr

    def __getattr__subclass__(self, attr_main_class, attr_sub_class):
        """ Returns the attribute of a subclass"""
        object_class = getattr(self, attr_main_class)
        object_subclass = getattr(object_class, attr_sub_class)
        return object_subclass


    







class EndUseClassResid(Region):
    """Class of an energy use category (e.g. lignting) of residential sector"""

    def __init__(self, current_year, data, data_ext, enduse_name, assumptions, fueldata_reg):
        self.enduse_name = enduse_name                      # EndUse Name
        self.current_year = current_year                    # from parent class
        self.data = data                                    # from parent class
        self.data_ext = data_ext                            # from parent class
        self.assumptions = assumptions                      # Assumptions from regions
        self.fueldata_reg = fueldata_reg[self.enduse_name]  # Regional fuel data

        self.tech_stock = ts.resid_tech_stock(self.current_year, self.data, self.assumptions, self.data_ext) # Generate technology stock of year

        # General efficiency gains of technology #TODO

        # Calculate fuel switches
        self.reg_fuel_after_switch = self.fuel_switches()   # Fuel after switching

        # Calculate new fuel demands after scenario drivers
        self.fuel_data_reg_after_scenario_driver_yearly = self.scenario_driver_for_each_enduse()
        self.fuel_data_daily = self.from_yearly_to_daily()
        self.self_fuel_data_hourly = self.from_daily_to_hourly()
        self.peak_daily = self.peak_daily()
        self.peak_hourly = self.peak_hourly()

    # Fuel Switches. Get new Fuels after switch
    def fuel_switches(self):
        """Calculates absolute fuel changes from assumptions about switches in changes of fuel percentages
        It also considers technological efficiency changes of replaced and old technologies."""

        # Share of fuel types for each end use
        fuel_p_by = self.assumptions['fuel_type_p_by'][self.enduse_name] # Base year fuel percentages
        fuel_p_ey = self.assumptions['fuel_type_p_ey'][self.enduse_name] # End year fuel percentages

        # Test whether share of fuel types stays identical
        if np.array_equal(fuel_p_by, fuel_p_ey):            # no fuel switches
            #print("No Fuel Switches (same perentages)")
            return self.fueldata_reg
        else:
            #print("Fuel is switched in Enduse: "  + str(self.enduse_name))

            # Out_dict initialisation
            fuel_switch_array = np.copy((self.fueldata_reg))

            # Assumptions about which technology is installed and replaced
            tech_install = self.assumptions['tech_install'][self.enduse_name]                   #  Technology which is installed
            tech_replacement_dict = self.assumptions['tech_replacement_dict'][self.enduse_name] #  Dict with current echnologes which are to be replaced

            # Calculate percentage differences over full simulation period EndUseClassResid
            fuel_diff = fuel_p_ey[:, 1:] - fuel_p_by[:, 1:] # difference in percentage (ID gets wasted because it is substracted)

            # Calculate sigmoid diffusion of fuel switches
            fuel_p_cy = fuel_diff * tf.sigmoidefficiency(self.data_ext['glob_var']['base_year'], self.current_year, self.data_ext['glob_var']['end_year'])
            print("fuel_p_cy:" + str(fuel_p_cy))
            print("fuel_p_ey:" + str(fuel_p_ey))

            # Differences in absolute fuel amounts
            absolute_fuel_diff = self.fueldata_reg * fuel_p_cy # Multiply fuel demands by percentage changes

            # Technology stock
            eff_replacement = getattr(self.tech_stock, tech_install)

            print("Technology which is installed:           " + str(tech_install))
            print("Efficiency of technology to be installed " + str(eff_replacement))
            print("Current Year:" + str(self.current_year))

            fuel_type = 0
            for fuel_diff in absolute_fuel_diff:
                tech_replace = tech_replacement_dict[fuel_type]           # Technology which is replaced (read from technology replacement dict)
                eff_tech_remove = getattr(self.tech_stock, tech_replace)  # Get efficiency of technology to be replaced

                # Fuel factor
                fuel_factor = (eff_tech_remove / eff_replacement)       #TODO ev. auch umgekehrt 
                fuel_consid_eff = fuel_diff * fuel_factor

                print("Technology fuel factor difference: " + str(eff_tech_remove) + "   " + str(eff_replacement) + "  " + str(fuel_factor))

                # Add  fuels (if minus, no technology weighting is necessary)
                if fuel_diff > 0:
                    fuel_switch_array[int(fuel_type)] += fuel_consid_eff # Add Fuel
                fuel_type += 1

            #print("Old Fuel: " + str(self.fueldata_reg))
            #print("--")
            #print("New Fuel: " + str(fuel_switch_array))
            return fuel_switch_array

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

