"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
from datetime import date
import unittest
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import energy_demand.main_functions as mf
import energy_demand.technological_stock as ts
import energy_demand.enduseClass as enduseClass
import energy_demand.serviceSector as ssClass
#import energy_demand.residential_model
ASSERTIONS = unittest.TestCase('__init__')

class RegionClass(object):
    """Region Class for the residential model

    The main class of the residential model. For every region, a Region object needs to be generated.

    A. In Region the shape of individ technologies get assigned to technology stock

    Parameters
    ----------
    reg_name : str
        Unique identifyer of region
    data : dict
        Dictionary containing data
    """
    def __init__(self, reg_name, data):
        """Constructor of RegionClass
        """
        print("--------------------------------")
        print(" ")
        print("REGION NAME: " + str(reg_name))
        print(" ")
        print("--------------------------------")
        self.reg_name = reg_name

        # Fuels
        self.rs_enduses_fuel = data['rs_fueldata_disagg'][reg_name]
        self.ss_enduses_sectors_fuels = data['ss_fueldata_disagg'][reg_name]

        # Get closest weather station and temperatures
        longitude = data['region_coordinates'][reg_name]['longitude']
        latitude = data['region_coordinates'][reg_name]['latitude']
        closest_weatherstation_id = mf.get_closest_weather_station(longitude, latitude, data['weather_stations'])
        temp_by = data['temperature_data'][closest_weatherstation_id][data['base_yr']]
        temp_cy = data['temperature_data'][closest_weatherstation_id][data['curr_yr']]

        # Calculate HDD and CDD for calculating heating and cooling service demand
        hdd_by = self.get_reg_hdd(data, temp_by, data['base_yr'])
        hdd_cy = self.get_reg_hdd(data, temp_cy, data['curr_yr'])
        cdd_by = self.get_reg_cdd(data, temp_by, data['base_yr'])
        cdd_cy = self.get_reg_cdd(data, temp_cy, data['curr_yr'])

        # yd peak factors for heating and cooling (factor to calculate max daily demand from yearly demand)
        self.reg_peak_yd_heating_factor = self.get_shape_peak_yd_factor(hdd_cy)
        self.reg_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(cdd_cy)

        # Climate change correction factors (Assumption: Demand for heat correlates directly with fuel)
        self.heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(hdd_by))) * np.sum(hdd_cy) #Yearly factor
        self.cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(cdd_by))) * np.sum(cdd_cy) #Yearly factor

        # yd shapes cy - Heating and cooling 
        fuel_shape_heating_yd = mf.absolute_to_relative(hdd_cy)
        fuel_shape_cooling_yd = mf.absolute_to_relative(cdd_cy)

        # Create region specific technological stock
        self.tech_stock = ts.ResidTechStock(
            data,
            data['assumptions']['tech_lu'],
            temp_by,
            temp_cy
            )

        # -------------------
        # Load and calculate fuel shapes for different technologies and assign to technological stock for every region
        # -------------------
        
        # Heating technologies
        fuel_shape_boilers_yh, fuel_shape_boilers_y_dh = self.get_shape_heating_boilers_yh(data, fuel_shape_heating_yd, 'rs_shapes_heating_boilers_dh') # Residential heating, boiler, non-peak
        fuel_shape_hp_yh, fuel_shape_hp_y_dh = self.get_fuel_shape_heating_hp_yh(data, self.tech_stock, hdd_cy, 'rs_shapes_heating_heat_pump_dh') # Residential heating, heat pumps, non-peak
        fuel_get_shape_cooling_yh = self.get_shape_cooling_yh(data, fuel_shape_cooling_yd, 'rs_shapes_cooling_dh') # Residential cooling, linear tech (such as boilers)
        fuel_shape_hybrid_gas_elec_yh = self.get_shape_heating_hybrid_yh(fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, 'hybrid_gas_elec', 'boiler_gas', 'av_heat_pump_electricity') # Hybrid

        # OTHER TECHNOLOGIES?
        #fuel_shape_lighting = data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'] * data['rs_shapes_dh']['rs_lighting']['shape_non_peak_dh']

        # Assign shapes to technologies in technological stock
        #self.tech_stock = self.assign_fuel_shapes_tech_stock(
        self.assign_fuel_shapes_tech_stock(
            data['assumptions']['tech_lu'],
            data['assumptions'],
            fuel_shape_heating_yd,
            fuel_shape_boilers_yh,
            fuel_get_shape_cooling_yh,
            fuel_shape_hp_yh,
            fuel_shape_hybrid_gas_elec_yh
            )

        # ------------
        # Residential
        # ------------
        '''# Set attributs of all enduses to the Region Class
        self.rs_create_enduse(
            data['rs_all_enduses'],
            data)
        '''
        # ------------
        # Service
        # ------------
        self.ss_create_enduses_sector(
            data['all_service_sectors'],
            data,
            data['ss_all_enduses']
        )

        # ------------
        # Industry
        # ------------

        # ------------
        # Transport
        # ------------


        # --------------------
        # -- summing functions
        # --------------------
        # Sum final 'yearly' fuels (summarised over all enduses)
        #self.rs_fuels_new = self.tot_all_enduses_y(data['rs_all_enduses'], 'enduse_fuel_yh') #TODO: IF NO defined, skip
        self.ss_fuels_new = self.tot_all_enduses_y(data['ss_all_enduses'], 'enduse_fuel_yh')

        # Get sum of fuels for each fueltype across fueltypes
        self.rs_tot_fuels_all_enduses_yh = self.tot_all_enduses_yh(data, data['rs_all_enduses'], 'enduse_fuel_yh') #NEW
        self.ss_tot_fuels_all_enduses_yh = self.tot_all_enduses_yh(data, data['ss_all_enduses'], 'enduse_fuel_yh') #NEW

        #self.rs_fuels_new_enduse_specific_y = self.enduse_specific_y(data, data['rs_all_enduses'], 'enduse_fuel_new_fuel')
        self.rs_fuels_new_enduse_specific_h = self.enduse_specific_h(data, data['rs_all_enduses'])
        self.ss_fuels_new_enduse_specific_h = self.enduse_specific_h(data, data['ss_all_enduses'])

        print("FUEL sr AMOUNT IN REGION: " + str(np.sum(self.rs_tot_fuels_all_enduses_yh)))
        print("FUEL ss AMOUNT IN REGION: " + str(np.sum(self.ss_tot_fuels_all_enduses_yh)))

        # Get peak energy demand for all enduses for every fueltype
        self.rs_max_fuel_peak = self.max_fuel_fueltype_allenduses(data, data['rs_all_enduses'], 'enduse_fuel_peak_h')
        self.ss_max_fuel_peak = self.max_fuel_fueltype_allenduses(data, data['ss_all_enduses'], 'enduse_fuel_peak_h')

        print("MAX PEAK: " + str(np.sum(self.rs_max_fuel_peak)))
        # ----
        # PEAK summaries
        # ----
        # Get 'peak demand day' (summarised over all enduses)
        ##self.fuels_peak_d = self.get_calc_enduse_fuel_peak_yd_factor(data, data['rs_all_enduses'])

        # Get 'peak demand h of peak calculations' (summarised over all enduse for each enduse)
        self.rs_fuels_peak_h = self.get_calc_enduse_fuel_peak_h(data, data['rs_all_enduses'], 'enduse_fuel_peak_h')
        self.ss_fuels_peak_h = self.get_calc_enduse_fuel_peak_h(data, data['ss_all_enduses'], 'enduse_fuel_peak_h')

        # Sum 'daily' demand in region (summarised over all enduses)
        self.rs_fuels_tot_enduses_d = self.tot_all_enduses_d(data, data['rs_all_enduses'], 'enduse_fuel_yd')
        self.ss_fuels_tot_enduses_d = self.tot_all_enduses_d(data, data['ss_all_enduses'], 'enduse_fuel_yd')

        # Sum 'hourly' demand in region for all enduses but fueltype specific (summarised over all enduses)
        self.rs_fuels_tot_enduses_h = self.tot_all_enduses_h(data, data['rs_all_enduses'], 'enduse_fuel_yh')
        self.ss_fuels_tot_enduses_h = self.tot_all_enduses_h(data, data['ss_all_enduses'], 'enduse_fuel_yh')

        # Calculate load factors from peak values
        self.rs_reg_load_factor_h = self.calc_load_factor_h(data, self.rs_fuels_tot_enduses_h, self.rs_fuels_peak_h) #Across all enduses
        self.ss_reg_load_factor_h = self.calc_load_factor_h(data, self.ss_fuels_tot_enduses_h, self.ss_fuels_peak_h) #Across all enduses

    def get_shape_heating_hybrid_yh(self, fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, hybrid_tech, tech_low_temp, tech_high_temp):
        """Use yd shapes and dh shapes of hybrid technologies to generate yh shape

        Parameters
        ----------
        fuel_shape_boilers_y_dh : array
            Fuel shape of boilers (dh) for evey day in a year
        fuel_shape_hp_y_dh : array
            Fuel shape of heat pumps (dh) for every day in a year
        fuel_shape_heating_yd : array
            Fuel shape for assign demand to day in a year (yd)
        tech_low_temp : string
            Low temperature technology
        tech_high_temp : string
            High temperature technology

        Return
        -------
        fuel_shape_yh : array
            Share of yearly fuel for hybrid technology

        Note: This is for hybrid_gas_elec technology
        """
        fuel_shape_yh = np.zeros((365, 24))

        # Create dh shapes for every day from relative dh shape of hybrid technologies
        fuel_shape_hybrid_y_dh = mf.calc_hybrid_fuel_shapes_y_dh(
            fuel_shape_boilers_y_dh=fuel_shape_boilers_y_dh,
            fuel_shape_hp_y_dh=fuel_shape_hp_y_dh,
            tech_low_high_p=self.tech_stock.get_tech_attribute(hybrid_tech, 'service_distr_hybrid_h_p_cy'),
            eff_low_tech=self.tech_stock.get_tech_attribute(tech_low_temp, 'eff_cy'),
            eff_high_tech=self.tech_stock.get_tech_attribute(tech_high_temp, 'eff_cy')
            )

        # Calculate yh fuel shape
        for day, fuel_day in enumerate(fuel_shape_heating_yd):
            fuel_shape_yh[day] = fuel_shape_hybrid_y_dh[day] * fuel_day

        # Testing
        np.testing.assert_almost_equal(np.sum(fuel_shape_yh), 1, decimal=3, err_msg="ERROR XY: The hybridy yh shape does not sum up to 1.0")

        return fuel_shape_yh

    def get_shape_peak_yd_factor(self, demand_yd):
        """From yd shape calculate maximum relative yearly service demand which is provided in a day

        Parameters
        ----------
        demand_yd : shape
            Demand for energy service for every day in year

        Return
        ------
        max_factor_yd : float
            yd maximum factor

        Info
        -----
        If the shape is taken from heat and cooling demand the assumption is made that
        HDD and CDD are directly proportional to fuel usage
        """
        tot_demand_y = np.sum(demand_yd) # Total yearly demand
        max_demand_d = np.max(demand_yd) # Maximum daily demand
        max_factor_yd = np.divide(1.0, tot_demand_y) * max_demand_d

        return max_factor_yd

    def assign_fuel_shapes_tech_stock(self, technologies, assumptions, fuel_shape_heating_yd, fuel_shape_boilers_yh, fuel_get_shape_cooling_yh, fuel_shape_hp_yh, fuel_shape_hybrid_gas_elec_yh):
        """Assign fuel shapes to indidivdual technologies in technologicalStock

        The technologies are iterated and checked wheter they are part of
        a specified enduse. Depending on defined asspumptions different shape
        curves for yd or yh are taken.

        Parameters
        ----------
        technologies : list
            List with technologies
        assumptions : dict
            Assumptions
        fuel_shape_heating_yd : array
            Assume that fuel of day is proportional to HDD (for all technologies)
        Return
        ------
        tech_stock : attribute
            Updated attribute of `Region` class
        """
        # Iterate all technologies and check if specific technology has a own shape
        for technology in technologies:

            # Heating boiler technologies
            if technology in assumptions['list_tech_heating_const']:
                self.tech_stock.set_tech_attribute(technology, 'shape_yd', fuel_shape_heating_yd) # Non peak
                self.tech_stock.set_tech_attribute(technology, 'shape_yh', fuel_shape_boilers_yh) # Non peak

            elif technology in assumptions['list_tech_cooling_const']:
                self.tech_stock.set_tech_attribute(technology, 'shape_yh', fuel_get_shape_cooling_yh) # Non peak

            elif technology in assumptions['list_tech_heating_temp_dep']:
                self.tech_stock.set_tech_attribute(technology, 'shape_yd', fuel_shape_heating_yd)
                self.tech_stock.set_tech_attribute(technology, 'shape_yh', fuel_shape_hp_yh)

            elif technology in assumptions['list_tech_heating_hybrid']:

                # Hybrid
                if technology == 'hybrid_gas_elec':
                    self.tech_stock.set_tech_attribute(technology, 'shape_yd', fuel_shape_heating_yd)
                    self.tech_stock.set_tech_attribute(technology, 'shape_yh', fuel_shape_hybrid_gas_elec_yh)

            #elif technology in assumptions['list_tech_rs_lighting']:
                #self.tech_stock.set_tech_attribute(technology, 'shape_yd', self.fuel_shape_heating_yd)
                #self.tech_stock.set_tech_attribute(technology, 'shape_yh', self.fuel_shape_hp_yh)

            #else:
            #    sys.exit("Error: The technology '{}' was not defined in a TECHLISTE".format(technology))

            '''
            elif technology in assumptions['list_enduse_tech_cooking']:
                enduse_shape_from_HES_yd = data['rs_shapes_yd']['rs_cooking']['shape_non_peak_yd']
                enduse_shape_from_HES_dh = data['rs_shapes_dh']['rs_cooking']['shape_non_peak_dh']
                enduse_shape_from_HES_yh = enduse_shape_from_HES_yd * enduse_shape_from_HES_dh
                self.tech_stock.set_tech_attribute(technology, 'shape_yh', enduse_shape_from_HES_yh)
                self.tech_stock.set_tech_attribute(technology, 'shape_yd', enduse_shape_from_HES_yd)
            '''
        
        #return self.tech_stock

    def ss_create_enduses_sector(self, service_sectors, data, all_enduses):
        """Create instance of service sector

        Parameters
        ----------
        reg_name : list
            All regions
        service_sectors : list
            All service sectors
        data : dict
            Data
        """
        # Iterate over sectors and create 'ServiceSectorClass' instance
        list_with_sectors = []
        for sector in service_sectors:

            # Service sector object
            sector_object = ssClass.ServiceSectorClass(
                reg_name=self.reg_name,
                sector_name=sector,
                data=data,
                tech_stock=self.tech_stock,
                heating_factor_y=self.heating_factor_y,
                cooling_factor_y=self.cooling_factor_y,
                reg_peak_yd_heating_factor=self.reg_peak_yd_heating_factor,
                reg_peak_yd_cooling_factor=self.reg_peak_yd_cooling_factor,
                fuels_all_enduses=self.ss_enduses_sectors_fuels
                )
            list_with_sectors.append(sector_object)


        # Iterate overall sectors and add summarised enduse to RegionClass
        for enduse in all_enduses:

             # Assign summarised enduse to RegionClass with relevant attributes
            enduse_fuel_yd = np.zeros((len(data['lu_fueltype']), 365))
            enduse_fuel_yh = np.zeros((len(data['lu_fueltype']), 365, 24))
            enduse_fuel_peak_dh = np.zeros((len(data['lu_fueltype']), 24))
            enduse_fuel_peak_h = np.zeros((len(data['lu_fueltype'])))

            # Attributes to sum over all sectory
            for sector_object in list_with_sectors:
                enduse_fuel_yd += self.getattr_summary_sector(sector_object, enduse, 'enduse_fuel_yd')
                enduse_fuel_yh += self.getattr_summary_sector(sector_object, enduse, 'enduse_fuel_yh')
                enduse_fuel_peak_dh += self.getattr_summary_sector(sector_object, enduse, 'enduse_fuel_peak_dh')
                enduse_fuel_peak_h += self.getattr_summary_sector(sector_object, enduse, 'enduse_fuel_peak_h')

            # Set as attribute
            RegionClass.__setattr__(
                self,
                enduse,

                # Summed individual attribute
                enduseClass.EnduseClassSummarySector(
                    enduse_fuel_yd=enduse_fuel_yd,
                    enduse_fuel_yh=enduse_fuel_yh,
                    enduse_fuel_peak_dh=enduse_fuel_peak_dh,
                    enduse_fuel_peak_h=enduse_fuel_peak_h
                )
            )

        return

    def getattr_summary_sector(self, summary_object, enduse, attr_sub_class):
        """Get the attribute of a subclass"""
        object_class = getattr(summary_object, enduse)
        object_subclass = getattr(object_class, attr_sub_class)
        return object_subclass

    def rs_create_enduse(self, enduses, data):
        """All enduses are initialised and inserted as an attribute of the `Region` Class

        It is checked wheter the enduse is a defined enduse where the enduse_peak_yd_factor
        depends on regional characteristics (temp).

        Parameters
        ----------
        enduses : list
            Enduses
        data : dict
            Data
        """
        # Iterate all residential enduses
        for enduse in enduses:

            # Enduse specific parameters
            if enduse == 'rs_space_heating' or enduse == 'ss_space_heating': #in data['assumptions']['enduse_rs_space_heating']:
                enduse_peak_yd_factor = self.reg_peak_yd_heating_factor # Regional yd factor for heating
            elif enduse == 'rs_space_cooling' or enduse == 'ss_space_cooling': #in data['assumptions']['enduse_space_cooling']:
                enduse_peak_yd_factor = self.reg_peak_yd_cooling_factor # Regional yd factor for cooling
            else:
                enduse_peak_yd_factor = data['rs_shapes_yd'][enduse]['shape_peak_yd_factor'] # Get parameters from loaded shapes for enduse

            # --------------------
            # Add enduse to region
            # --------------------
            RegionClass.__setattr__(
                self,
                enduse,
                enduseClass.EnduseClass(
                    reg_name=self.reg_name,
                    data=data,
                    enduse=enduse,
                    enduse_fuel=self.rs_enduses_fuel[enduse],
                    tech_stock=self.tech_stock,
                    heating_factor_y=self.heating_factor_y,
                    cooling_factor_y=self.cooling_factor_y,
                    enduse_peak_yd_factor=enduse_peak_yd_factor,
                    fuel_switches=data['assumptions']['rs_fuel_switches'],
                    service_switches=data['assumptions']['rs_service_switches'],
                    fuel_enduse_tech_p_by=data['assumptions']['rs_fuel_enduse_tech_p_by'],
                    service_tech_by_p=data['assumptions']['rs_service_tech_by_p'],
                    tech_increased_service=data['assumptions']['rs_tech_increased_service'],
                    tech_decreased_share=data['assumptions']['rs_tech_decreased_share'],
                    tech_constant_share=data['assumptions']['rs_tech_constant_share'],
                    installed_tech=data['assumptions']['rs_installed_tech'],
                    sigm_parameters_tech=data['assumptions']['rs_sigm_parameters_tech'],
                    data_shapes_yd=data['rs_shapes_yd'],
                    data_shapes_dh=data['rs_shapes_dh'],
                    enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['residential_sector'],
                    dw_stock=data['rs_dw_stock']
                    )
                )

    def tot_all_enduses_y(self, enduses, attribute_to_get):
        """Sum all fuel types over all end uses
        """
        sum_fuels = 0
        for enduse in enduses:
            sum_fuels += np.sum(self.__getattr__subclass__(enduse, attribute_to_get))

        return sum_fuels

    def tot_all_enduses_yh(self, data, enduses, attribute_to_get):
        """Sum all fuel types over all end uses
        """
        tot_fuels_all_enduse = np.zeros((data['nr_of_fueltypes'], 365, 24))

        for enduse in enduses:
            if hasattr(self, enduse): # If attribute is in class
                tot_fuels_all_enduse += self.__getattr__subclass__(enduse, attribute_to_get)
                print("ENDUSE {} SUMME {}".format(enduse, np.sum(self.__getattr__subclass__(enduse, attribute_to_get))))
            else:
                print("Enduse '{}' is not in object".format(enduse))

        return tot_fuels_all_enduse

    def max_fuel_fueltype_allenduses(self, data, enduses, attribute_to_get):
        """Sum all fuel types over all end uses
        """
        sum_fuels = np.zeros((data['nr_of_fueltypes']))

        for enduse in enduses:
            for fueltype in data['fuel_type_lu']:
                if hasattr(self, enduse):
                    sum_fuels[fueltype] += self.__getattr__subclass__(enduse, attribute_to_get)[fueltype]

        return sum_fuels

    def get_fuels_enduse_requested(self, enduse):
        """ TEST: READ ENDSE SPECIFID FROM"""
        fuels = self.__getattr__subclass__(enduse, 'enduse_fuel_new_fuel')
        return fuels

    def enduse_specific_y(self, data, enduses, attribute_to_get):
        """Sum fuels for every fuel type for each enduse
        """
        sum_fuels_all_enduses = {}
        for enduse in enduses:
            sum_fuels_all_enduses[enduse] = np.zeros((data['nr_of_fueltypes']))

        # Sum data
        for enduse in enduses:
            if hasattr(self, enduse):
                sum_fuels_all_enduses[enduse] += self.__getattr__subclass__(enduse, attribute_to_get) # Fuel of Enduse
        return sum_fuels_all_enduses

    def enduse_specific_h(self, data, enduses):
        """Sum fuels for every fuel type for each enduse
        """
        sum_fuels_all_enduses = {}
        for enduse in enduses:
            sum_fuels_all_enduses[enduse] = np.zeros((data['nr_of_fueltypes'], 365, 24))

        # Sum data
        for enduse in enduses:
            if hasattr(self, enduse):
                sum_fuels_all_enduses[enduse] += self.__getattr__subclass__(enduse, 'enduse_fuel_yh') # Fuel of Enduse h

        return sum_fuels_all_enduses

    def tot_all_enduses_d(self, data, enduses, attribute_to_get):
        """Calculate total daily fuel demand for each fueltype
        """
        sum_fuels_d = np.zeros((data['nr_of_fueltypes'], 365))

        for fueltype in data['fuel_type_lu']:
            for enduse in enduses:
                if hasattr(self, enduse):
                    sum_fuels_d[fueltype] += self.__getattr__subclass__(enduse, attribute_to_get)[fueltype]

        return sum_fuels_d

    def get_calc_enduse_fuel_peak_yd_factor(self, data, enduses):
        """Summarise absolute fuel of peak days over all end_uses
        """
        sum_calc_enduse_fuel_peak_yd_factor = np.zeros((data['nr_of_fueltypes']))  # Initialise

        for enduse in enduses:
            sum_calc_enduse_fuel_peak_yd_factor += self.__getattr__subclass__(enduse, 'enduse_peak_yd_factor') # Fuel of Enduse

        return sum_calc_enduse_fuel_peak_yd_factor

    def get_calc_enduse_fuel_peak_h(self, data, enduses, attribute_to_get):
        """Summarise peak values of all enduses for every fueltype
        """
        sum_calc_enduse_fuel_peak_yh = np.zeros((data['nr_of_fueltypes'], 1))

        for fueltype in data['fuel_type_lu']:
            for enduse in enduses:
                if hasattr(self, enduse):
                    sum_calc_enduse_fuel_peak_yh[fueltype] += self.__getattr__subclass__(enduse, attribute_to_get)[fueltype] # Fuel of Endus enduse_fuel_peak_dh

        return sum_calc_enduse_fuel_peak_yh

    def tot_all_enduses_h(self, data, enduses, attribute_to_get):
        """Calculate total hourly fuel demand for each fueltype
        """
        sum_fuels_h = np.zeros((data['nr_of_fueltypes'], 365, 24))

        for fueltype in data['fuel_type_lu']:
            for enduse in enduses:
                if hasattr(self, enduse):
                    sum_fuels_h[fueltype] += self.__getattr__subclass__(enduse, attribute_to_get)[fueltype]

        # Read out more error information (e.g. RuntimeWarning)
        #np.seterr(all='raise') # If not round, problem....np.around(fuel_end_use_h,10)
        return sum_fuels_h

    def load_factor_d(self, data):
        """Calculate load factor of a day in a year from peak values

        self.fuels_peak_d     :   Fuels for peak day (fueltype, data)
        self.rs_fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data) for full year

        Return
        ------
        lf_d : array
            Array with load factor for every fuel type in %

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        lf_d = np.zeros((data['nr_of_fueltypes']))

        # Get day with maximum demand (in percentage of year)
        peak_d_demand = self.fuels_peak_d

        # Iterate fueltypes to calculate load factors for each fueltype
        for k, fueldata in enumerate(self.rs_fuels_tot_enduses_d):
            average_demand = np.sum(fueldata) / 365 # Averae_demand = yearly demand / nr of days

            if average_demand != 0:
                lf_d[k] = average_demand / peak_d_demand[k] # Calculate load factor

        lf_d = lf_d * 100 # Convert load factor to %

        return lf_d

    def calc_load_factor_h(self, data, rs_fuels_tot_enduses_h, rs_fuels_peak_h):
        """Calculate load factor of a h in a year from peak data (peak hour compared to all hours in a year)

        self.rs_fuels_peak_h     :   Fuels for peak day (fueltype, data)
        self.rs_fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

        Return
        ------
        load_factor_h : array
            Array with load factor for every fuel type [in %]

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        load_factor_h = np.zeros((data['nr_of_fueltypes']))

        # Iterate fueltypes to calculate load factors for each fueltype
        for fueltype, fuels in enumerate(rs_fuels_tot_enduses_h):

            # Maximum fuel of an hour of the peak day
            maximum_h_of_day = rs_fuels_peak_h[fueltype][0]

            #Calculate average in full year
            average_demand_h = np.mean(fuels) # np.average(fuels)

            # If there is a maximum day hour
            if maximum_h_of_day != 0:
                load_factor_h[fueltype] = average_demand_h / maximum_h_of_day # Calculate load factor

        # Convert load factor to %
        load_factor_h *= 100

        return load_factor_h

    def load_factor_d_non_peak(self, data):
        """Calculate load factor of a day in a year from non-peak data

        self.fuels_peak_d     :   Fuels for peak day (fueltype, data)
        self.rs_fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

        Return
        ------
        lf_d : array
            Array with load factor for every fuel type in %

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        lf_d = np.zeros((data['nr_of_fueltypes']))

        # Iterate fueltypes to calculate load factors for each fueltype
        for k, fueldata in enumerate(self.rs_fuels_tot_enduses_d):

            average_demand = sum(fueldata) / 365 # Averae_demand = yearly demand / nr of days
            max_demand_d = max(fueldata)

            if  max_demand_d != 0:
                lf_d[k] = average_demand / max_demand_d # Calculate load factor

        lf_d = lf_d * 100 # Convert load factor to %

        return lf_d

    def load_factor_h_non_peak(self, data):
        """Calculate load factor of a h in a year from non-peak data

        self.rs_fuels_tot_enduses_d    :   Hourly fuel for different fueltypes (fueltype, 24 hours data)

        Return
        ------
        load_factor_h : array
            Array with load factor for every fuel type [in %]

        Info
        -----
        Load factor = average load / maximum load in given time period

        Info: https://en.wikipedia.org/wiki/Load_factor_(electrical)
        """
        load_factor_h = np.zeros((data['nr_of_fueltypes'], 1)) # Initialise array to store fuel

        # Iterate fueltypes to calculate load factors for each fueltype
        for fueltype, fueldata in enumerate(self.rs_fuels_tot_enduses_h):

            '''all_hours = []
            for day_hours in self.rs_fuels_tot_enduses_h[fueltype]:
                for h in day_hours:
                    all_hours.append(h)
            maximum_h_of_day_in_year = max(all_hours)
            '''
            maximum_h_of_day_in_year = self.rs_fuels_peak_h[fueltype]

            average_demand_h = np.sum(fueldata) / (365 * 24) # Averae load = yearly demand / nr of days

            # If there is a maximum day hour
            if maximum_h_of_day_in_year != 0:
                load_factor_h[fueltype] = average_demand_h / maximum_h_of_day_in_year # Calculate load factor

        # Convert load factor to %
        load_factor_h *= 100

        return load_factor_h

    def get_reg_hdd(self, data, temperatures, year):
        """Calculate daily shape of heating demand based on calculating HDD for every day

        Based on temperatures of a year, the HDD are calculated for every
        day in a year. Based on the sum of all HDD of all days, the relative
        share of heat used for any day is calculated.

        The Heating Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        data : dict
            Base data dict

        Return
        ------
        hdd_d : array
            Heating degree days for every day in a year (365, 1)

        Info
        -----
        The shape_yd can be calcuated as follows: 1/ np.sum(hdd_d) * hdd_d

        The diffusion is assumed to be sigmoid
        """
        # Calculate base temperature for heating of current year
        rs_t_base_heating_cy = mf.t_base_sigm(year, data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_heating')

        # Calculate hdd for every day (365, 1)
        hdd_d = mf.calc_hdd(rs_t_base_heating_cy, temperatures)

        # Error testing
        if np.sum(hdd_d) == 0:
            sys.exit("Error: No heating degree days means no fuel for heating is necessary")

        return hdd_d

    def get_reg_cdd(self, data, temperatures, year):
        """Calculate daily shape of cooling demand based on calculating CDD for every day

        Based on temperatures of a year, the CDD are calculated for every
        day in a year. Based on the sum of all CDD of all days, the relative
        share of heat used for any day is calculated.

        The Cooling Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        data : dict
            Base data dict
        data_ext : dict
            External data

        Return
        ------
        shape_yd : array
            Fraction of heat for every day. Array-shape: 365, 1
        """
        t_base_cooling_resid = mf.t_base_sigm(year, data['assumptions'], data['base_yr'], data['end_yr'], 't_base_cooling_resid')

        # Calculate cdd for every day (365, 1)
        cdd_d = mf.calc_cdd(t_base_cooling_resid, temperatures)

        return cdd_d

    def get_fuel_shape_heating_hp_yh(self, data, tech_stock, hdd_cy, tech_to_get_shape):
        """Convert daily shapes to houly based on robert sansom daily load for heatpump

        This is for non-peak.

        Parameters
        ---------
        data : dict
            data
        tech_stock : object
            Technology stock
        hdd_cy : array
            Heating Degree Days (365, 1)

        Returns
        -------
        hp_shape : array
            Daily shape how yearly fuel can be distributed to hourly
        shape_y_dh : array
            Shape of fuel shape for every day in a year (total sum = 365)
        Info
        ----
        The service is calculated based on the efficiency of gas heat pumps (av_heat_pump_gas)

        The daily heat demand is converted to daily fuel depending on efficiency of heatpumps (assume if 100% heat pumps).
        In a final step the hourly fuel is converted to percentage of yearly fuel demand.

        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily fuel demand curve for heat pumps taken from:
        Sansom, R. (2014). Decarbonising low grade heat for low carbon future. Dissertation, Imperial College London.
        """
        shape_yh_hp = np.zeros((365, 24))
        shape_y_dh = np.zeros((365, 24))

        list_dates = mf.fullyear_dates(start=date(data['base_yr'], 1, 1), end=date(data['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):

            # See wether day is weekday or weekend
            weekday = date_gasday.timetuple().tm_wday

            # Take respectve daily fuel curve depending on weekday or weekend from Robert Sansom for heat pumps
            if weekday == 5 or weekday == 6:
                daily_fuel_profile = np.divide(data[tech_to_get_shape][2], np.sum(data[tech_to_get_shape][2])) # WkendHourly gas shape. Robert Sansom hp curve
            else:
                daily_fuel_profile = np.divide(data[tech_to_get_shape][1], np.sum(data[tech_to_get_shape][1])) # Wkday Hourly gas shape. Robert Sansom hp curve

            # Calculate weighted average daily efficiency of heat pump
            average_eff_d = 0
            for hour, heat_share_h in enumerate(daily_fuel_profile):
                tech_object = getattr(tech_stock, 'av_heat_pump_gas') # Select gas heat pumps to calculate service shape
                average_eff_d += heat_share_h * getattr(tech_object, 'eff_cy')[day][hour] # Hourly heat demand * heat pump efficiency

            # Convert daily service demand to fuel (Heat demand / efficiency = fuel)
            hp_daily_fuel = np.divide(hdd_cy[day], average_eff_d)

            # Fuel distribution within day
            fuel_shape_d = hp_daily_fuel * daily_fuel_profile

            # Distribute fuel of day according to fuel load curve
            shape_yh_hp[day] = fuel_shape_d

            #print("*************DDDDDDD")
            #print(np.sum(fuel_shape_d))

            # Add normalised daily fuel curve
            #shape_y_dh[day] = np.divide(1, np.sum(fuel_shape_d)) * fuel_shape_d
            shape_y_dh[day] = mf.absolute_to_relative(fuel_shape_d)

        # Convert absolute hourly fuel demand to relative fuel demand within a year
        shape_yh = np.divide(1, np.sum(shape_yh_hp)) * shape_yh_hp

        return shape_yh, shape_y_dh

    def get_shape_cooling_yh(self, data, cooling_shape, tech_to_get_shape):
        """Convert daily shape to hourly based on robert sansom daily load for boilers

        This is for non-peak.

        Every the day same

        Taken from Denholm, P., Ong, S., & Booten, C. (2012). Using Utility Load Data to
        Estimate Demand for Space Cooling and Potential for Shiftable Loads,
        (May), 23. Retrieved from http://www.nrel.gov/docs/fy12osti/54509.pdf

        Parameters
        ---------
        data : dict
            data

        Returns
        -------
        shape_yd_cooling_tech : array
            Shape of cooling devices

        Info
        ----
        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily heat demand (calculated with hdd) is distributed within the day
        fuel demand curve for boilers from:

        """
        shape_yd_cooling_tech = np.zeros((365, 24))

        for day in range(365):
            shape_yd_cooling_tech[day] = data[tech_to_get_shape] * cooling_shape[day] # Shape of cooling (same for all days) * daily cooling demand
        return shape_yd_cooling_tech

    def get_shape_heating_boilers_yh(self, data, heating_shape, tech_to_get_shape):
        """Convert daily fuel shape to hourly based on robert sansom daily load for boilers

        This is for non-peak.

        Parameters
        ---------
        data : dict
            data
        heating_shape : array
            Daily (yd) service demand shape for heat (percentage of yearly heat demand for every day)

        Returns
        -------
        shape_yh_boilers : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_y_dh_boilers : array
            Shape of distribution of fuel within every day of a year (total sum == 365)

        Info
        ----
        The assumption is made that boilers have constant efficiency for every hour in a year.
        Therefore the fuel demand correlates directly with the heat service demand.

        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily heat demand (calculated with hdd) is distributed within the day
        fuel demand curve for boilers from:

        Sansom, R. (2014). Decarbonising low grade heat for low carbon future. Dissertation, Imperial College London.
        """
        shape_yh_boilers = np.zeros((365, 24))
        shape_y_dh_boilers = np.zeros((365, 24))

        list_dates = mf.fullyear_dates(start=date(data['base_yr'], 1, 1), end=date(data['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):

            # See wether day is weekday or weekend
            weekday = date_gasday.timetuple().tm_wday

            # Take respectve daily fuel curve depending on weekday or weekend
            if weekday == 5 or weekday == 6:

                # -----
                # The percentage of totaly yearly heat demand (heating_shape[day]) is distributed with daily fuel shape of boilers
                # Because boiler eff is constant, the shape_yh_boilers reflects the needed heat per hour
                # ------
                # Wkend Hourly gas shape. Robert Sansom boiler curve
                shape_yh_boilers[day] = heating_shape[day] * (data[tech_to_get_shape][2] / np.sum(data[tech_to_get_shape][2]))

                shape_y_dh_boilers[day] = np.divide(data[tech_to_get_shape][2], np.sum(data[tech_to_get_shape][2]))
            else:
                # Wkday Hourly gas shape. Robert Sansom boiler curve
                shape_yh_boilers[day] = heating_shape[day] * (data[tech_to_get_shape][1] / np.sum(data[tech_to_get_shape][1])) #yd shape

                shape_y_dh_boilers[day] = np.divide(data[tech_to_get_shape][1], np.sum(data[tech_to_get_shape][1])) #dh shape

        # Testing
        np.testing.assert_almost_equal(np.sum(shape_yh_boilers), 1, err_msg="Error in shape_yh_boilers: The sum of hourly shape is not 1: {}".format(np.sum(shape_yh_boilers)))

        return shape_yh_boilers, shape_y_dh_boilers

    def __getattr__subclass__(self, attr_main_class, attr_sub_class):
        """Get the attribute of a subclass"""
        object_class = getattr(self, attr_main_class)
        object_subclass = getattr(object_class, attr_sub_class)
        return object_subclass

    def plot_stacked_regional_end_use(self, nr_of_day_to_plot, fueltype, yearday, reg_name):
        """Plots stacked end_use for a region

        #TODO: Make that end_uses can be sorted, improve legend...

        0: 0-1
        1: 1-2
        2:

        #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
        """
        fig, ax = plt.subplots() #fig is needed
        nr_hours_to_plot = nr_of_day_to_plot * 24 #WHY 2?

        day_start_plot = yearday
        day_end_plot = (yearday + nr_of_day_to_plot)

        x = range(nr_hours_to_plot)

        legend_entries = []

        # Initialise (number of enduses, number of hours to plot)
        Y_init = np.zeros((len(self.rs_enduses_fuel), nr_hours_to_plot))

        # Iterate enduse
        for k, enduse in enumerate(self.rs_enduses_fuel):
            legend_entries.append(enduse)
            sum_fuels_h = self.__getattr__subclass__(enduse, 'enduses_fuel_h') #np.around(fuel_end_use_h,10)

            list_all_h = []

            #Get data of a fueltype
            for _, fuel_data in enumerate(sum_fuels_h[fueltype][day_start_plot:day_end_plot]):
                for h in fuel_data:
                    list_all_h.append(h)

            Y_init[k] = list_all_h

        #color_list = ["green", "red", "#6E5160"]

        sp = ax.stackplot(x, Y_init)
        proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]

        ax.legend(proxy, legend_entries)

        #ticks x axis
        ticks_x = range(24)
        plt.xticks(ticks_x)

        #plt.xticks(range(3), ['A', 'Big', 'Cat'], color='red')
        plt.axis('tight')

        plt.xlabel("Hours")
        plt.ylabel("Energy demand in GWh")
        plt.title("Stacked energy demand for region{}".format(reg_name))

        #from matplotlib.patches import Rectangle
        #legend_boxes = []
        #for i in color_list:
        #    box = Rectangle((0, 0), 1, 1, fc=i)
        #    legend_boxes.append(box)
        #ax.legend(legend_boxes, legend_entries)

        #ax.stackplot(x, Y_init)
        plt.show()


def plot_stacked_regional_end_use(self, nr_of_day_to_plot, fueltype, yearday, reg_name):
    """Plots stacked end_use for a region

    #TODO: Make that end_uses can be sorted, improve legend...

    0: 0-1
    1: 1-2
    2:

    #TODO: For nice plot make that 24 --> shift averaged 30 into middle of bins.
    """
    fig, ax = plt.subplots() #fig is needed
    nr_hours_to_plot = nr_of_day_to_plot * 24 #WHY 2?

    day_start_plot = yearday
    day_end_plot = (yearday + nr_of_day_to_plot)

    x = range(nr_hours_to_plot)

    legend_entries = []

    # Initialise (number of enduses, number of hours to plot)
    Y_init = np.zeros((len(self.enduse_fuel), nr_hours_to_plot))

    # Iterate enduse
    for k, enduse in enumerate(self.enduse_fuel):
        legend_entries.append(enduse)
        sum_fuels_h = self.__getattr__subclass__(enduse, 'enduse_fuel_yh') #np.around(fuel_end_use_h,10)

        list_all_h = []

        #Get data of a fueltype
        for _, fuel_data in enumerate(sum_fuels_h[fueltype][day_start_plot:day_end_plot]):

            for h in fuel_data:
                list_all_h.append(h)

        Y_init[k] = list_all_h

    #color_list = ["green", "red", "#6E5160"]

    sp = ax.stackplot(x, Y_init)
    proxy = [mpl.patches.Rectangle((0, 0), 0, 0, facecolor=pol.get_facecolor()[0]) for pol in sp]

    ax.legend(proxy, legend_entries)

    #ticks x axis
    ticks_x = range(24)
    plt.xticks(ticks_x)

    #plt.xticks(range(3), ['A', 'Big', 'Cat'], color='red')
    plt.axis('tight')

    plt.xlabel("Hours")
    plt.ylabel("Energy demand in GWh")
    plt.title("Stacked energy demand for region{}".format(reg_name))

    #from matplotlib.patches import Rectangle
    #legend_boxes = []
    #for i in color_list:
    #    box = Rectangle((0, 0), 1, 1, fc=i)
    #    legend_boxes.append(box)
    #ax.legend(legend_boxes, legend_entries)

    #ax.stackplot(x, Y_init)
    plt.show()
