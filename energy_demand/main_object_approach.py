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

# pylint: disable=I0011,C0321,C0301,C0103, C0325

# Dict for every end_use with
#    - Scenario Drivers
#    - All shapes
#    - All Demand switches



class Region(object):
    """ Class of region """

    # Constructor (initialise class)
    def __init__(self, reg_name, data, data_ext):
        self.reg_name = reg_name                                            # Name/ID of region
        self.current_year = data_ext['glob_var']['current_year']
        self.fueldata_reg = data['fueldata_disagg'][reg_name]               # Fuel array of region

        self.pop = data_ext['population'][self.current_year][self.reg_name] # Population of current year

        #self.floor_area = floor_area
        #self.SHAPES_ASSUMPTIONS
        # ...
        self.fuels_new = self.sum_all_fuels_over_appliances()


        # Functions in constructor
        self.create_end_use_objects()     # Add end uses and fuel to region


    # Summen new yearly data overall appliances

    # Get hourly data


    def create_end_use_objects(self):
        """Initialises all defined end uses. Adds an object for each end use to the Region class"""
        a = {}
        for i in self.fueldata_reg:
            a[i] = EndUse_Class(i, self.fueldata_reg[i])
        self.end_uses = a

        # Creat self objects {'key': Value}
        for i in self.end_uses:
            vars(self).update(self.end_uses)

    def sum_all_fuels_over_appliances(self):
        '''Summen all appliances'''
        pass





class EndUse_Class(Region):
    """End Use class"""

    def __init__(self, enduse_name, fuel_data_reg):
        self.enduse_name = enduse_name
        self.fuel_data_reg_after_switch = self.fuel_switches()
        self.fuel_data_reg_after_scenario_driver_yearly = self.scenario_driver_for_each_enduse()
        self.fuel_data_daily = self.from_yearly_to_daily()
        self.self_fuel_data_hourly = self.from_daily_to_hourly()
        self.peak_daily = self.peak_daily()
        self.peak_hourly = self.peak_hourly()

    # Fuel Switches. Get new Fuels after switch
    def fuel_switches(self):
        self.fueldata_reg

        pass

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
