"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103, C0325

import numpy as np

import energy_demand.technological_stock as ts
import energy_demand.technological_stock_functions as tf

# TODO: Write function to convert array to list and dump it into txt file / or yaml file (np.asarray(a.tolist()))

class Region(object):
    """Class of region """

    def __init__(self, reg_id, data, data_ext):
        """ Constructor. Initialising different methods"""
        self.reg_id = reg_id                                        # ID of region
        self.data = data                                            # data
        self.data_ext = data_ext                                    # external data
        self.assumptions = data['assumptions']                      # Improve: Assumptions per region
        self.current_year = data_ext['glob_var']['current_year']    # Current year
        self.reg_fuel = data['fueldata_disagg'][reg_id]             # Fuel array of region (used to extract all end_uses)
        #self.pop = data_ext['population'][self.current_year][self.reg_id] # Population of current year

        # Create all end use attributes
        self.create_end_use_objects()

        # Sum final fuels of all end_uses
        self.fuels_new = self.tot_all_enduses_y()

        # Get peak demand day
        self.reg_peak_h = self.get_reg_peak_d()

        # Get peak demand h
        self.reg_peak_h = self.get_reg_peak_h()

        # Sum daily
        self.fuels_tot_enduses_d = self.tot_all_enduses_d()

        # Sum hourly
        self.fuels_tot_enduses_h = self.tot_all_enduses_h()

    def create_end_use_objects(self):
        """Initialises all defined end uses. Adds an object for each end use to the Region class"""
        a = {}
        for enduse in self.reg_fuel:
            a[enduse] = EndUseClassResid(self.reg_id, self.data, self.data_ext, enduse, self.reg_fuel)
        self.end_uses = a
        for _ in self.end_uses:
            vars(self).update(self.end_uses)     # Creat self objects {'key': Value}

    def tot_all_enduses_y(self):
        '''Summen all fuel types over all end uses'''

        # Initialise array to store fuel
        sum_fuels = np.zeros((len(self.data['fuel_type_lu']), 1))

        for enduse in self.reg_fuel:

            # Fuel of Enduse
            sum_fuels += self.__getattr__subclass__(enduse, 'reg_fuelscen_driver')

        return sum_fuels

    def tot_all_enduses_d(self):
        """Calculate total daily fuel demand for each fueltype"""

        # Initialise array to store fuel
        sum_fuels_d = np.zeros((len(self.data['fuel_type_lu']), 365))

        for enduse in self.reg_fuel:
            sum_fuels_d += self.__getattr__subclass__(enduse, 'reg_fuel_d')

        return sum_fuels_d

    def get_reg_peak_d(self):
        """Summarise peak value of all end_uses"""
        sum_reg_peak_d = np.zeros((len(self.data['fuel_type_lu']), 1))

        for enduse in self.reg_fuel:

            # Fuel of Enduse
            sum_reg_peak_d += self.__getattr__subclass__(enduse, 'reg_peak_d')

        return sum_reg_peak_d

    def get_reg_peak_h(self):
        """Summarise peak value of all end_uses"""
        sum_reg_peak_h = np.zeros((len(self.data['fuel_type_lu']), 1, 24))

        for enduse in self.reg_fuel:

            # Fuel of Enduse
            sum_reg_peak_h += self.__getattr__subclass__(enduse, 'reg_peak_h')

        return sum_reg_peak_h

    def tot_all_enduses_h(self):
        """Calculate total hourly fuel demand for each fueltype"""

        # Initialise array to store fuel
        sum_fuels_h = np.zeros((len(self.data['fuel_type_lu']), 365, 24))

        for enduse in self.reg_fuel:
            sum_fuels_h += self.__getattr__subclass__(enduse, 'reg_fuel_h') #np.around(fuel_end_use_h,10)

        # Read out more error information (e.g. RuntimeWarning)
        #np.seterr(all='raise') # If not round, problem....np.around(fuel_end_use_h,10)
        return sum_fuels_h

    def __getattr__(self, attr):
        """ Get method of own object"""
        return self.attr

    def __getattr__subclass__(self, attr_main_class, attr_sub_class):
        """ Returns the attribute of a subclass"""
        object_class = getattr(self, attr_main_class)
        object_subclass = getattr(object_class, attr_sub_class)
        return object_subclass

class EndUseClassResid(Region):
    """Class of an end use category of the residential sector"""

    def __init__(self, reg_id, data, data_ext, enduse, reg_fuel):

        # --General data
        self.reg_id = reg_id                                        # Region
        self.enduse = enduse                                        # EndUse Name
        self.current_year = data_ext['glob_var']['current_year']    # from parent class
        self.data = data                                            # from parent class
        self.data_ext = data_ext                                    # from parent class
        self.assumptions = data['assumptions']                      # Assumptions from regions
        self.reg_fuel = reg_fuel[enduse]                            # Regional base fuel data
        self.tech_stock = data['tech_stock']                        # Technological stock

        # --Load shapes
        self.enduse_shape_d = data['dict_shapes_end_use_d'][enduse]['shape_d_non_peak']  # shape_d
        self.enduse_shape_h = data['dict_shapes_end_use_h'][enduse]['shape_h_non_peak']  # shape_h
        self.enduse_shape_peak_d = data['dict_shapes_end_use_d'][enduse]['peak_d_shape'] # shape_d peak (Factor to calc one day)
        self.enduse_shape_peak_h = data['dict_shapes_end_use_h'][enduse]['peak_h_shape'] # shape_h peak

        # --Yearly fuel data
        #self.efficiency_gains....                                                       # General efficiency gains of technology over time #TODO
        self.reg_fuel_after_elasticity = self.enduse_elasticity()                        # Calculate demand with changing elasticity (elasticity maybe on household level)
        self.reg_fuel_after_switch = self.enduse_fuel_switches()                         # Calculate fuel switches

        # THIS IS LAST MUTATION IN PROCESS... (all disaggreagtion function refer to this)
        self.reg_fuelscen_driver = self.enduse_scenario_driver()                         # Calculate new fuel demands after scenario drivers

        # --Daily fuel data
        self.reg_fuel_d = self.enduse_y_to_d()                                           # Disaggregate yearly demand for every day

        # --Hourly fuel data
        self.reg_fuel_h = self.enduse_d_to_h()                                           # Disaggregate daily demand to hourly demand
        self.reg_peak_d = self.enduse_peak_d()                                           # Calculate peak day TODO
        self.reg_peak_h = self.enduse_peak_h()                                           #Calculate peak hour TODO

    def enduse_elasticity(self):
        """ Adapts yearls fuel use depending on elasticity """
        # Will maybe be on household level
        pass

    def enduse_fuel_switches(self):
        """Calculates absolute fuel changes from assumptions about switches in changes of fuel percentages
        It also considers technological efficiency changes of replaced and old technologies.

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuel_switch_array : array
            tbd

        Notes
        -----
        """
        # Share of fuel types for each end use
        fuel_p_by = self.assumptions['fuel_type_p_by'][self.enduse] # Base year
        fuel_p_ey = self.assumptions['fuel_type_p_ey'][self.enduse] # End year

        # Test whether share of fuel types stays identical
        if np.array_equal(fuel_p_by, fuel_p_ey):            # no fuel switches
            return self.reg_fuel                            # No Fuel Switches (same perentages)
        else:
            fuel_switch_array = np.copy((self.reg_fuel))    # Out_dict initialisation

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

            for fuel_type, fuel_diff in enumerate(absolute_fuel_diff):
                tech_replace = tech_replacement_dict[fuel_type]           # Technology which is replaced (read from technology replacement dict)
                eff_tech_remove = getattr(self.tech_stock, tech_replace)  # Get efficiency of technology to be replaced

                # Fuel factor   #TODO ev. auch umgekehrt
                fuel_factor = eff_tech_remove / eff_replacement
                fuel_consid_eff = fuel_diff * fuel_factor
                #print("Technology fuel factor difference: " + str(eff_tech_remove) + "   " + str(eff_replacement) + "  " + str(fuel_factor))
                #print("fuel_diff: " + str(fuel_diff))
                # Add  fuels (if minus, no technology weighting is necessary)
                if fuel_diff > 0:
                    fuel_switch_array[int(fuel_type)] += fuel_consid_eff # Add Fuel

            #print("Old Fuel: " + str(self.reg_fuel))
            #print("--")
            #print("New Fuel: " + str(fuel_switch_array))
            return fuel_switch_array

    def enduse_scenario_driver(self):
        """The fuel data for every end use are multiplied with respective scenario driver

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
        This is the energy end use used for disaggregating to daily and hourly
        """
        if self.enduse == 'heating':
            attr_building_stock = 'sd_heating'
        else:
            #TODO: add very end_use
            attr_building_stock = 'sd_heating'

        # Scenariodriver of building stock base year and new stock
        by_driver = getattr(self.data['reg_building_stock_by'][self.reg_id], attr_building_stock)     # Base year building stock
        cy_driver = getattr(self.data['reg_building_stock_cur_yr'][self.reg_id], attr_building_stock) # Current building stock

        factor_driver = cy_driver / by_driver  #TODO: Or the other way round

        fueldata_scenario_diver = self.reg_fuel_after_switch * factor_driver
        return fueldata_scenario_diver

    def enduse_y_to_d(self):
        """Generate array with fuels for every day"""

        fuels_d = np.zeros((len(self.reg_fuel), 365))

        # Iterate yearday and
        for k, fueltype_year_data in enumerate(self.reg_fuelscen_driver):
            fuels_d[k] = self.enduse_shape_d[:, 0] * fueltype_year_data[0] # enduse_shape_d is  a two dim array with load shapes in first row

        return fuels_d

    def enduse_d_to_h(self):
        """Disaggregate yearly fuel data to every day in the year

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

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for k, fuel_type_data in enumerate(self.reg_fuel_d):
            for day in range(365):
                fuels_h[k][day] = self.enduse_shape_h[day] * fuel_type_data[day]

        return fuels_h

    def enduse_peak_d(self):
        """Disaggregate yearly fuel data to the peak day.

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_d_peak : array
            Hourly fuel data [fueltypes, peak_day, hours]

        Notes
        -----
        """
        fuels_d_peak = np.zeros((len(self.reg_fuel), 1))

        # Iterate yearday and
        for k, fueltype_year_data in enumerate(self.reg_fuelscen_driver):
            fuels_d_peak[k] = self.enduse_shape_peak_d * fueltype_year_data[0] # enduse_shape_d is  a two dim array with load shapes in first row

        return fuels_d_peak

    def enduse_peak_h(self):
        """Disaggregate daily peak day fuel data to the peak hours.

        Parameters
        ----------
        self : self
            Data from constructor

        Returns
        -------
        fuels_h_peak : array
            Hourly fuel data [fueltypes, peakday, peak_hours]

        Notes
        -----
        """
        fuels_h_peak = np.zeros((self.reg_fuel_d.shape[0], 1, 24)) #fueltypes  days, hours

        # Iterate fueltypes and day and multiply daily fuel data with daily shape
        for k, fuel_data in enumerate(self.reg_peak_d):
            for day in range(1):
                fuels_h_peak[k][day] = self.enduse_shape_peak_h[day] * fuel_data[day]

        return fuels_h_peak
