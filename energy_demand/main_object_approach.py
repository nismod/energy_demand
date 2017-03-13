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

        self.assumptions = ass[self.reg_name]                       # Improve: Assumptions per region
        self.current_year = data_ext['glob_var']['current_year']            # Current year
        self.fueldata_reg = data['fueldata_disagg'][reg_name]               # Fuel array of region
        self.pop = data_ext['population'][self.current_year][self.reg_name] # Population of current year

        # Functions in constructor
        self.create_end_use_objects()     # Add end uses and fuel to region


        #self.floor_area = floor_area
        #self.SHAPES_ASSUMPTIONS
        # ...
        self.fuels_new = self.sum_all_fuels_over_appliances()

    # Summen new yearly data overall appliances



    def create_end_use_objects(self):
        """Initialises all defined end uses. Adds an object for each end use to the Region class"""
        a = {}
        for i in self.fueldata_reg:
            a[i] = EndUse_Class(i, self.assumptions, self.fueldata_reg)
        self.end_uses = a
        for i in self.end_uses: # Creat self objects {'key': Value}
            vars(self).update(self.end_uses)

    # Sum yearly
    def sum_all_fuels_over_appliances(self):
        '''Summen all appliances'''
        pass

    # Sum hourly

    # Sum peak

    # sum...






class EndUse_Class(Region):
    """End Use class"""

    def __init__(self, enduse_name, ass, fueldata_reg):
        # Call from self of Region class

        self.enduse_name = enduse_name                              # EndUse Name

        # from parent class
        self.assumptions = ass #ASsumptions from regions
        self.fueldata_reg = fueldata_reg

        self.fuel_data_reg_after_switch = self.fuel_switches(self.enduse_name)
        self.fuel_data_reg_after_scenario_driver_yearly = self.scenario_driver_for_each_enduse()
        self.fuel_data_daily = self.from_yearly_to_daily()
        self.self_fuel_data_hourly = self.from_daily_to_hourly()
        self.peak_daily = self.peak_daily()
        self.peak_hourly = self.peak_hourly()

    # Fuel Switches. Get new Fuels after switch
    def fuel_switches(self, enduse_name):

        fuel_p_by = self.assumptions['fuel_type_p_by'][self.enduse_name] # Base year fuel percentages #self.enduse_name #TODO: RMOEVE 'hetaing'
        fuel_p_ey = self.assumptions['fuel_type_p_ey'][self.enduse_name] # End year fuel percentages

        print(fuel_p_by)
        print(fuel_p_ey)
        # Calculate percentage differences for EndUse_Class
        fuel_diff = fuel_p_ey - fuel_p_by # difference in percentage
        print(fuel_diff)
        print("--")
        print(self.fueldata_reg)
        absolute_fuel_diff = self.fueldata_reg[self.enduse_name] * fuel_diff #TODO
        # Load all fuels to switch
        

        #tf.switch_fuel(data_ext, self.current_year, assumptions, eff_tech_from, eff_tech_tp, fuel_end_use_to_switch, tot_fuel_from_by, tot_fuel_to_by)
        #pass
        return absolute_fuel_diff
    

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
    print(data['fuel_type_lu'])
    print(data['reg_lu'])
    print(data['fuel_bd_data'])
    #print(data['data_residential_by_fuel_end_uses'])
    #pint("----")
    print(data['fueldata_disagg'])

    # Now the data needs to look like
    # ----------------------------------------



    test_fuel_disaggregated = {0:
                                    {'heating': np.array((len(data['fuel_type_lu']), 1)),
                                    'cooking':  np.array((len(data['fuel_type_lu']), 1))
                                    }
                               }
    #data['fueldata_disagg'] = {0:, data['data_residential_by_fuel_end_uses']} #test_fuel_disaggregated
    
    assumptions = {0: assumptions, 1: assumptions, 2: assumptions} # ASsumptions per region

    # Iterate regions
    for reg in data['reg_lu']:
            print("Region: " + str(reg))

            # Residential
            a = Region(reg, data, data_ext, assumptions)

            print(a.cooking)

            print(len(a.end_uses))
            #prnt("..")
            #return

