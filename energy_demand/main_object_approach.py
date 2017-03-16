""" NEw Model """
#import sys
#import os
#import csv
#import traceback
#import datetime
#from datetime import date
#from datetime import timedelta as td
import numpy as np

#import energy_demand.main_functions as mf
#import energy_demand.building_stock_generator as bg
#import energy_demand.assumptions as assumpt
#from energy_demand import residential_model
import energy_demand.technological_stock as ts
import energy_demand.technological_stock_functions as tf
# pylint: disable=I0011,C0321,C0301,C0103, C0325



# Write function to convert array to list and dump it into txt file / or yaml file (np.asarray(a.tolist()))
#


class Region(object):
    """ Class of region """

    def __init__(self, reg_name, data, data_ext, assumption):
        """ Constructor. Initialising different methods"""
        self.reg_name = reg_name                                       # Name/ID of region
        self.data = data
        self.data_ext = data_ext
        self.assumptions = assumption                                  # Improve: Assumptions per region
        self.current_year = data_ext['glob_var']['current_year']       # Current year
        self.reg_fuel = data['fueldata_disagg'][reg_name]          # Fuel array of region (used to extract all end_uses)

        #self.pop = data_ext['population'][self.current_year][self.reg_name] # Population of current year

        # Create all end use attributes
        self.create_end_use_objects()     # Add end uses and fuel to region

        # Sum final fuels of all end_uses
        self.fuels_new = self.sum_final_fuel_all_enduses()

        # Get peak demand

        # Sum daily

        # Sum hourly
        self.h_sum_data = self.tot_all_enduses_h()

    def create_end_use_objects(self):
        """Initialises all defined end uses. Adds an object for each end use to the Region class"""
        a = {}
        for enduse in self.reg_fuel:
            a[enduse] = EndUseClassResid(self.reg_name, self.current_year, self.data, self.data_ext, enduse, self.assumptions, self.reg_fuel)
        self.end_uses = a
        for _ in self.end_uses:
            vars(self).update(self.end_uses)     # Creat self objects {'key': Value}



    def sum_final_fuel_all_enduses(self):
        '''Summen all fuel types over all end uses'''

        # Initialise empty array to store fuel
        summary_fuel = np.empty((len(self.data['fuel_type_lu']), 1))
        cnt = 0

        for enduse in self.reg_fuel:

            # Fuel of Enduse
            fuel_end_use = self.__getattr__subclass__(enduse, 'fuel_data_reg_after_scenario_driver_yearly') #TODO: Replace reg_fuel_after_switch with Final Energy Demand from end_use_class
            #print(fuel_end_use.shape)

            # Iterate fuels
            #print("A: " + str(summary_fuel.shape))
            #print("B: " + str(fuel_end_use.shape))
            summary_fuel += fuel_end_use

            cnt += 1

        return summary_fuel

    def tot_all_enduses_h(self):
        """Calculate total hourly fuel demand for each fueltype"""

        # Initialise empty array to store fuel
        summary_fuel_h = np.empty((len(self.data['fuel_type_lu']), 365, 24))

        for enduse in self.reg_fuel:
            fuel_end_use_h = self.__getattr__subclass__(enduse, 'reg_fuel_h') #TODO: Replace reg_fuel_after_switch with Final Energy Demand from end_use_class
            summary_fuel_h += fuel_end_use_h

        return summary_fuel_h

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

    def __init__(self, reg_name, current_year, data, data_ext, enduse, assumptions, reg_fuel):

        # --General data
        self.reg_name = reg_name                            # Region
        self.enduse = enduse                      # EndUse Name
        self.current_year = current_year                    # from parent class
        self.data = data                                    # from parent class
        self.data_ext = data_ext                            # from parent class
        self.assumptions = assumptions                      # Assumptions from regions
        self.reg_fuel = reg_fuel[enduse]       # Regional base fuel data
        self.tech_stock = data['tech_stock']                # Technological stock

        # --Load shapes
        self.load_shape_d = data['dict_shapes_end_use_d'][enduse]['shape_d_non_peak']  # shape_d
        self.load_shape_h = data['dict_shapes_end_use_h'][enduse]['shape_h_non_peak']  # shape_h
        self.load_shape_peak_d = data['dict_shapes_end_use_d'][enduse]['peak_d_shape'] # shape_d peak
        self.load_shape_peak_h = data['dict_shapes_end_use_h'][enduse]['peak_h_shape'] # shape_h peak

        # --Yearly fuel data
        #self.efficiency_gains....                                                                   # General efficiency gains of technology over time #TODO
        self.reg_fuel_after_elasticity = self.elasticity_energy_demand()                             # Calculate demand with changing elasticity (elasticity maybe on household level)
        self.reg_fuel_after_switch = self.fuel_switches()                                            # Calculate fuel switches
        self.fuel_data_reg_after_scenario_driver_yearly = self.scenario_driver_for_each_enduse()     # Calculate new fuel demands after scenario drivers

        # --Daily fuel data
        self.reg_fuel_d = self.from_yearly_to_daily()                                           # Disaggregate yearly demand for every day

        # --Hourly fuel data
        self.reg_fuel_h = self.from_daily_to_hourly()                                     # Disaggregate daily demand to hourly demand

        self.peak_d = self.peak_d()                                           # Calculate peak day TODO
        self.peak_h = self.peak_h()                                           #Calculate peak hour TODO




    def elasticity_energy_demand(self):
        """ Adapts yearls fuel use depending on elasticity """
        # Will maybe be on household level
        pass

    def fuel_switches(self):
        """Calculates absolute fuel changes from assumptions about switches in changes of fuel percentages
        It also considers technological efficiency changes of replaced and old technologies."""

        # Share of fuel types for each end use
        fuel_p_by = self.assumptions['fuel_type_p_by'][self.enduse] # Base year
        fuel_p_ey = self.assumptions['fuel_type_p_ey'][self.enduse] # End year

        # Test whether share of fuel types stays identical
        if np.array_equal(fuel_p_by, fuel_p_ey):            # no fuel switches
            return self.reg_fuel                        #print("No Fuel Switches (same perentages)")
        else:                                               #print("Fuel is switched in Enduse: "  + str(self.enduse))

            # Out_dict initialisation
            fuel_switch_array = np.copy((self.reg_fuel))

            # Assumptions about which technology is installed and replaced
            tech_install = self.assumptions['tech_install'][self.enduse]                   #  Technology which is installed
            eff_replacement = getattr(self.tech_stock, tech_install)

            tech_replacement_dict = self.assumptions['tech_replacement_dict'][self.enduse] #  Dict with current echnologes which are to be replaced

            # Calculate percentage differences over full simulation period
            fuel_diff = fuel_p_ey[:, 1] - fuel_p_by[:, 1] # difference in percentage (ID gets wasted because it is substracted)
            #print("fuel_diff: " + str(fuel_diff))

            # Calculate sigmoid diffusion of fuel switches
            fuel_p_cy = fuel_diff * tf.sigmoidefficiency(self.data_ext['glob_var']['base_year'], self.current_year, self.data_ext['glob_var']['end_year'])
            #print("fuel_p_cy:" + str(fuel_p_cy))
            #print(fuel_p_ey[:, 1])
            #print("fuel_p_ey:" + str(fuel_p_ey))
            #print(fuel_p_cy.shape)
            #print("self.reg_fuel: " + str(self.reg_fuel))
            #print(self.reg_fuel.shape)

            # Differences in absolute fuel amounts
            absolute_fuel_diff = self.reg_fuel[0] * fuel_p_cy # Multiply fuel demands by percentage changes
            #print("absolute_fuel_diff: " + str(absolute_fuel_diff))
            #print("Technology which is installed:           " + str(tech_install))
            #print("Efficiency of technology to be installed " + str(eff_replacement))
            #print("Current Year:" + str(self.current_year))

            fuel_type = 0
            for fuel_diff in absolute_fuel_diff:
                tech_replace = tech_replacement_dict[fuel_type]           # Technology which is replaced (read from technology replacement dict)
                eff_tech_remove = getattr(self.tech_stock, tech_replace)  # Get efficiency of technology to be replaced

                # Fuel factor
                fuel_factor = eff_tech_remove / eff_replacement       #TODO ev. auch umgekehrt
                fuel_consid_eff = fuel_diff * fuel_factor
                #print("Technology fuel factor difference: " + str(eff_tech_remove) + "   " + str(eff_replacement) + "  " + str(fuel_factor))
                #print("fuel_diff: " + str(fuel_diff))
                # Add  fuels (if minus, no technology weighting is necessary)
                if fuel_diff > 0:
                    fuel_switch_array[int(fuel_type)] += fuel_consid_eff # Add Fuel
                fuel_type += 1

            #print("Old Fuel: " + str(self.reg_fuel))
            #print("--")
            #print("New Fuel: " + str(fuel_switch_array))
            return fuel_switch_array

    def scenario_driver_for_each_enduse(self):
        """The fuels for every end use are multiplied with scenario driver
        #TODO: Check if in sub-functions alway the latest data is taken (process train)
        """

        fueldata = self.reg_fuel_after_switch   # data
        enduse = self.enduse               # enduse

        by_building_stock = self.data['reg_building_stock_by'][self.reg_name]       # Base year building stock
        cy_building_stock = self.data['reg_building_stock_cur_yr'][self.reg_name]   # Current building stock

        if enduse == 'heating':
            attr_building_stock = 'sd_heating'
        else:
            #TODO: add very end_use
            attr_building_stock = 'sd_heating'

        # Scenariodriver of building base and new stock
        by_driver = getattr(by_building_stock, attr_building_stock)
        cy_driver = getattr(cy_building_stock, attr_building_stock)

        factor_driver = cy_driver / by_driver  #TODO: Or the other way round

        #print("fueldata: " + str(fueldata))

        fueldata_scenario_diver = fueldata * factor_driver

        return fueldata_scenario_diver

    def from_yearly_to_daily(self):

        """Generate array with fuels for every day"""

        fuels_d = np.zeros((len(self.fuel_data_reg_after_scenario_driver_yearly), 365))

        cnt = 0
        # Iterate yearday and 
        for fueltype_year_data in self.fuel_data_reg_after_scenario_driver_yearly:
            fuels_d[cnt] = self.load_shape_d[:, 0] * fueltype_year_data # load_shape_d is  a two dim array with load shapes in first row
            cnt += 1

        return fuels_d


    def from_daily_to_hourly(self):
        """Hourly data for every day in a year

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_h : array
            Hourly fuel data [fueltypes, days, hours]

        Notes
        -----
        """
        fuels_h = np.zeros((self.reg_fuel_d.shape[0], 365, 24)) #fueltypes, days, hours

        cnt = 0
        for fuel_type_data in self.reg_fuel_d:

            # Iterate days and multiply daily fuel data with daily shape
            for day in range(365):
                fuels_h[cnt][day] = fuel_type_data[day] * self.load_shape_h[day]

            cnt += 1

        return fuels_h


    def peak_d(self):
        """ DESCRIPTION"""
        pass

    def peak_h(self):
        """ DESCRIPTION"""
        pass





# ----------------------------------------
'''
def new_energy_demand_model(data, data_ext, assumptions):
    """NEWMODEL"""
    # Now the data needs to look like
    # ----------------------------------------
    #data['fueldata_disagg'] = {0:, data['data_residential_by_fuel_end_uses']} #test_fuel_disaggregated

    #assumptions = {0: assumptions, 1: assumptions, 2: assumptions} # ASsumptions per region
    #print (assumptions)

    # Generate technological stock
    tech_stock = ts.resid_tech_stock(data_ext['glob_var']['current_year'], data, assumptions, data_ext) #TODO ASSUMPTIONS
    data['tech_stock'] = tech_stock


    # Iterate REGION AND GENERATE OBJECTS
    for reg in data['reg_lu']:
        print("Region: " + str(reg))

        # Residential
        a = Region(reg, data, data_ext, assumptions)

        hourly_all_fuels = a.tot_all_enduses_h()

        gas_final = hourly_all_fuels[0]
        elec = hourly_all_fuels[1]
    
'''