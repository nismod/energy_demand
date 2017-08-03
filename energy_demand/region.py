"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
import sys
from datetime import date
import numpy as np
import energy_demand.technological_stock as ts
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_shape_handling import hdd_cdd
from energy_demand.scripts_geography import weather_station_location as wl
from energy_demand.scripts_initalisations import helper_functions

class Region(object):
    """Region class

    For every Region, a Region object needs to be generated.

    Parameters
    ----------
    region_name : str
        Unique identifyer of region_name
    data : dict
        Dictionary containing data

    Info
    -------------------------
    - For each region_name, a technology stock is defined with help of regional temperature data technology specific
    - regional specific fuel shapes are assigned to technologies
    """
    def __init__(self, region_name, data):
        """Constructor
        """
        self.region_name = region_name

        # Fuels of different sectors
        self.rs_enduses_fuel = data['rs_fueldata_disagg'][region_name]
        self.ss_enduses_sectors_fuels = data['ss_fueldata_disagg'][region_name]
        self.is_enduses_sectors_fuels = data['is_fueldata_disagg'][region_name]
        self.ts_fuels = data['ts_fueldata_disagg'][region_name]

        # Get closest weather station and temperatures
        closest_station_id = wl.get_closest_station(data['reg_coordinates'][region_name]['longitude'], data['reg_coordinates'][region_name]['latitude'], data['weather_stations'])
        temp_by = data['temperature_data'][closest_station_id][data['base_yr']]
        temp_cy = data['temperature_data'][closest_station_id][data['curr_yr']]

        # Get base temperatures for base and current year
        rs_t_base_heating_cy = hdd_cdd.sigm_t_base(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_heating')
        rs_t_base_cooling_cy = hdd_cdd.sigm_t_base(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_cooling')

        ss_t_base_heating_cy = hdd_cdd.sigm_t_base(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_heating')
        ss_t_base_cooling_cy = hdd_cdd.sigm_t_base(data['curr_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_cooling')

        rs_t_base_heating_by = hdd_cdd.sigm_t_base(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_heating')
        rs_t_base_cooling_by = hdd_cdd.sigm_t_base(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'rs_t_base_cooling')

        ss_t_base_heating_by = hdd_cdd.sigm_t_base(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_heating')
        ss_t_base_cooling_by = hdd_cdd.sigm_t_base(data['base_yr'], data['assumptions'], data['base_yr'], data['end_yr'], 'ss_t_base_cooling')

        # ----------------------------------------------------------------------------------------
        # Calculate HDD and CDD for calculating heating and cooling service demand (for rs and ss)
        # ----------------------------------------------------------------------------------------
        print("   ...calculating weather related variables")
        # Residential
        rs_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, rs_t_base_heating_by)
        rs_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, rs_t_base_cooling_by)

        rs_hdd_cy, rs_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy)
        rs_cdd_cy, rs_fuel_shape_cooling_yd = hdd_cdd.get_reg_cdd(temp_cy, rs_t_base_cooling_cy)

        # Service
        ss_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by)
        ss_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by)

        ss_hdd_cy, ss_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy)
        ss_cdd_cy, ss_fuel_shape_cooling_yd = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy)

        # yd peak factors for heating and cooling (factor to calculate max daily demand from yearly demand)
        rs_peak_yd_heating_factor = self.get_shape_peak_yd_factor(rs_hdd_cy)
        rs_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(rs_cdd_cy)

        ss_peak_yd_heating_factor = self.get_shape_peak_yd_factor(ss_hdd_cy)
        ss_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(ss_cdd_cy)

        # Climate change correction factors (Assumption: Demand for heat correlates directly with fuel)
        self.rs_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(rs_hdd_by))) * np.sum(rs_hdd_cy)
        self.rs_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(rs_cdd_by))) * np.sum(rs_cdd_cy)

        self.ss_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(ss_hdd_by))) * np.sum(ss_hdd_cy)
        self.ss_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(ss_cdd_by))) * np.sum(ss_cdd_cy)

        # Create region_name specific technological stock
        print("   ...creating technology stocks in region_name")
        self.rs_tech_stock = ts.TechStock('rs_tech_stock', data, temp_by, temp_cy, data['assumptions']['rs_t_base_heating']['base_yr'], data['rs_all_enduses'], rs_t_base_heating_cy, data['assumptions']['rs_all_specified_tech_enduse_by'])
        self.ss_tech_stock = ts.TechStock('ss_tech_stock', data, temp_by, temp_cy, data['assumptions']['ss_t_base_heating']['base_yr'], data['ss_all_enduses'], ss_t_base_heating_cy, data['assumptions']['ss_all_specified_tech_enduse_by'])
        self.is_tech_stock = ts.TechStock('is_tech_stock', data, temp_by, temp_cy, data['assumptions']['ss_t_base_heating']['base_yr'], data['is_all_enduses'], ss_t_base_heating_cy, data['assumptions']['is_all_specified_tech_enduse_by'])

        # Create region_name specific shape stock
        self.rs_load_profiles = shape_handling.LoadProfileStock("rs_load_profiles")
        self.ss_load_profiles = shape_handling.LoadProfileStock("ss_load_profiles")
        self.is_load_profiles = shape_handling.LoadProfileStock("is_load_profiles")


        # -------------------------------------------------------------------------------------------
        # Load and calculate fuel shapes for different technologies and assign to technological stock
        # -------------------------------------------------------------------------------------------
        print("   ...assign individual technology shapes")
        # --Heating technologies for residential sector
        rs_fuel_shape_storage_heater_yh, rs_fuel_shape_storage_heater_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_space_heating_storage_heater_elec_heating_dh')
        rs_fuel_shape_elec_heater_yh, rs_fuel_shape_elec_heater_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_space_heating_second_elec_heating_dh')

        rs_fuel_shape_boilers_yh, rs_fuel_shape_boilers_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_heating_boilers_dh') # boiler, non-peak
        rs_fuel_shape_hp_yh, rs_fuel_shape_hp_y_dh = self.get_fuel_shape_heating_hp_yh(data, self.rs_tech_stock, rs_hdd_cy, 'rs_shapes_heating_heat_pump_dh') # heat pumps, non-peak

        rs_fuel_shape_hybrid_tech_yh = self.get_shape_heating_hybrid_yh(self.rs_tech_stock, 'rs_space_heating', rs_fuel_shape_boilers_y_dh, rs_fuel_shape_hp_y_dh, rs_fuel_shape_heating_yd, 'hybrid_gas_electricity') #, 'boiler_gas', 'heat_pumps_electricity') # Hybrid gas electric

        # Cooling residential
        rs_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, rs_fuel_shape_cooling_yd, 'rs_shapes_cooling_dh')

        # --Heating technologies for service sector (the heating shape follows the gas shape of aggregated sectors)
        ss_fuel_shape_any_tech, ss_fuel_shape = self.ss_get_sector_enduse_shape(data, ss_fuel_shape_heating_yd, 'ss_space_heating')

        # Cooling service
        #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_cooling_yd, 'ss_shapes_cooling_dh') # Service cooling
        #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_heating_yd, 'ss_shapes_cooling_dh') # Service cooling #USE HEAT YD BUT COOLING SHAPE
        #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, shape_handling.absolute_to_relative(ss_hdd_cy + ss_cdd_cy), 'ss_shapes_cooling_dh') # hdd & cdd

        ss_fuel_shape_hybrid_gas_elec_yh = self.get_shape_heating_hybrid_yh(self.ss_tech_stock, 'ss_space_heating', ss_fuel_shape, ss_fuel_shape, ss_fuel_shape_heating_yd, 'hybrid_gas_electricity') #, 'boiler_gas', 'heat_pumps_electricity') # Hybrid

        # Heating boiler
        self.rs_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_const'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            sectors=data['rs_sectors'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_boilers_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=data['rs_shapes_heating_boilers_dh']['peakday']
            )

        self.ss_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_const'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=data['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_peak_dh=data['ss_shapes_dh'] # peak for multiple sectors
            )

        self.is_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_const'],
            enduses=['is_space_heating'],
            sectors=data['is_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_peak_dh=data['is_shapes_dh'] # peak for multiple sectors
            )

        # Electric heating, primary...(storage)
        self.rs_load_profiles.add_load_profile(
            technologies=data['assumptions']['primary_heating_electricity'],
            enduses=['rs_space_heating'],
            sectors=data['rs_sectors'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_storage_heater_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=data['rs_shapes_space_heating_storage_heater_elec_heating_dh']['peakday']
            )

        self.ss_load_profiles.add_load_profile(
            technologies=data['assumptions']['primary_heating_electricity'],
            enduses=['ss_space_heating'],
            sectors=data['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_peak_dh=data['rs_shapes_space_heating_storage_heater_elec_heating_dh']['peakday']
            )

        self.is_load_profiles.add_load_profile(
            technologies=data['assumptions']['primary_heating_electricity'],
            enduses=['is_space_heating'],
            sectors=data['is_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_yh=ss_fuel_shape_any_tech
            )

        # Electric heating, secondary...
        self.rs_load_profiles.add_load_profile(
            technologies=data['assumptions']['secondary_heating_electricity'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            sectors=data['rs_sectors'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_elec_heater_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=data['rs_shapes_space_heating_second_elec_heating_dh']['peakday']
            )

        self.ss_load_profiles.add_load_profile(
            technologies=data['assumptions']['secondary_heating_electricity'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            sectors=data['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor
            #shape_peak_dh=data['rs_shapes_space_heating_second_elec_heating_dh']['peakday']
            )

        self.is_load_profiles.add_load_profile(
            technologies=data['assumptions']['secondary_heating_electricity'],
            enduses=['is_space_heating'],
            sectors=data['is_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            )

        # Hybrid heating
        self.rs_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_hybrid'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            sectors=data['rs_sectors'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_hybrid_tech_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            #shape_peak_dh=   #OTHERdata['rs_shapes_heating_heat_pump_dh']['peakday']
            )

        self.ss_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_hybrid'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=data['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_hybrid_gas_elec_yh,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            )

        self.is_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_hybrid'],
            enduses=['is_space_heating'],
            sectors=data['is_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            )

        # Heat pump heating
        self.rs_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_temp_dep'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            sectors=data['rs_sectors'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_hp_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=data['rs_shapes_heating_heat_pump_dh']['peakday']
            )

        self.ss_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_temp_dep'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=data['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            #shape_peak_dh=data['rs_shapes_heating_heat_pump_dh']['peakday']
            )

        self.is_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_heating_temp_dep'],
            enduses=['is_space_heating'],
            sectors=data['is_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_peak_dh=data['is_shapes_dh'] #   data['rs_shapes_heating_heat_pump_dh']['peakday']
            )

        # Lighting (residential)
        self.rs_load_profiles.add_load_profile(
            technologies=data['assumptions']['list_tech_rs_lighting'],
            enduses=['rs_lighting'],
            sectors=data['rs_sectors'],
            shape_yd=data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'],
            shape_yh=data['rs_shapes_dh']['rs_lighting']['shape_non_peak_dh'] * data['rs_shapes_yd']['rs_lighting']['shape_non_peak_yd'][:, np.newaxis],
            enduse_peak_yd_factor=data['rs_shapes_yd']['rs_lighting']['shape_peak_yd_factor'],
            shape_peak_dh=data['rs_shapes_dh']['rs_lighting']['shape_peak_dh']
            )

        # -- dummy rs technologies
        for enduse in data['assumptions']['rs_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['rs_fuel_enduse_tech_p_by'][enduse])

            self.rs_load_profiles.add_load_profile(
                technologies=tech_list,
                enduses=enduse,
                sectors=data['rs_sectors'],
                shape_yd=data['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                shape_yh=data['rs_shapes_dh'][enduse]['shape_non_peak_dh'] * data['rs_shapes_yd'][enduse]['shape_non_peak_yd'][:, np.newaxis],
                enduse_peak_yd_factor=data['rs_shapes_yd'][enduse]['shape_peak_yd_factor'], # * (1 / (365)),
                shape_peak_dh=data['rs_shapes_dh'][enduse]['shape_peak_dh']
                )

        # - dummy is technologies
        for enduse in data['assumptions']['ss_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['ss_fuel_enduse_tech_p_by'][enduse])
            for sector in data['ss_sectors']:
                self.ss_load_profiles.add_load_profile(
                    technologies=tech_list,
                    enduses=enduse,
                    sectors=sector,
                    shape_yd=data['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=data['ss_shapes_dh'][sector][enduse]['shape_non_peak_dh'] * data['ss_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    enduse_peak_yd_factor=data['ss_shapes_yd'][sector][enduse]['shape_peak_yd_factor'], #  * (1 / (365)),
                    shape_peak_dh=data['ss_shapes_dh']#[sector][enduse]['shape_peak_dh']
                    )

        # dummy is
        for enduse in data['assumptions']['is_dummy_enduses']:
            tech_list = helper_functions.get_nested_dict_key(data['assumptions']['is_fuel_enduse_tech_p_by'][enduse])
            for sector in data['is_sectors']:
                self.is_load_profiles.add_load_profile(
                    technologies=tech_list,
                    enduses=enduse,
                    sectors=sector,
                    shape_yd=data['is_shapes_yd'][sector][enduse]['shape_non_peak_yd'],
                    shape_yh=data['is_shapes_dh'][sector][enduse]['shape_non_peak_dh'] * data['is_shapes_yd'][sector][enduse]['shape_non_peak_yd'][:, np.newaxis],
                    enduse_peak_yd_factor=data['is_shapes_yd'][sector][enduse]['shape_peak_yd_factor']  * (1 / (365)),
                    shape_peak_dh=data['is_shapes_dh']#[sector][enduse]['shape_peak_dh']
                    )

    def assign_fuel_peak_dh_shape_tech_stock(self, tech_stock, technologies, enduses, sectors, shape_peak_dh):
        """Assign technology specific yd and yh shape

        Parameters
        ----------
        tech_stock : object
            Technology stock to assign shape
        technologies : list
            Technologies to which the shape gets assigned
        enduses : list
            Enduses where the technologies are used
        shape_peak_dh : array
            Fuel shape
        """
        for enduse in enduses:
            for sector in sectors:
                for technology in technologies:
                    tech_stock.set_tech_attribute_enduse(technology, 'shape_peak_dh', shape_peak_dh, enduse, sector)

    def get_shape_heating_hybrid_yh(self, tech_stock, enduse, fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, hybrid_tech): #, tech_low_temp, tech_high_temp):
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

        Note
        -----
        This is for hybrid_gas_elec technology

        The shapes are the same for any hybrid technology with boiler and heat pump
        """
        fuel_shape_yh = np.zeros((365, 24))

        # Create dh shapes for every day from relative dh shape of hybrid technologies
        fuel_shape_hybrid_y_dh = shape_handling.get_hybrid_fuel_shapes_y_dh(
            fuel_shape_boilers_y_dh=fuel_shape_boilers_y_dh,
            fuel_shape_hp_y_dh=fuel_shape_hp_y_dh,
            tech_low_high_p=tech_stock.get_tech_attr(enduse, hybrid_tech, 'service_distr_hybrid_h_p_cy')
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

    '''def get_reg_hdd(self, temperatures, t_base_heating):
        """Calculate HDD for every day and daily yd shape of cooling demand

        Based on temperatures of a year, the HDD are calculated for every
        day in a year. Based on the sum of all HDD of all days, the relative
        share of heat used for any day is calculated.

        The Heating Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        temperatures : array
            Temperatures
        t_base_heating : float
            Base temperature for heating

        Return
        ------
        hdd_d : array
            Heating degree days for every day in a year (365, 1)

        Info
        -----
        The shape_yd can be calcuated as follows: 1/ np.sum(hdd_d) * hdd_d

        The diffusion is assumed to be sigmoid
        """
        hdd_d = hdd_cdd.calc_hdd(t_base_heating, temperatures)
        shape_hdd_d = shape_handling.absolute_to_relative(hdd_d)

        # Error testing
        if np.sum(hdd_d) == 0:
            sys.exit("Error: No heating degree days means no fuel for heating is necessary")

        return hdd_d, shape_hdd_d
    '''

    '''def get_reg_cdd(self, temperatures, t_base_cooling):
        """Calculate CDD for every day and daily yd shape of cooling demand

        Based on temperatures of a year, the CDD are calculated for every
        day in a year. Based on the sum of all CDD of all days, the relative
        share of heat used for any day is calculated.

        The Cooling Degree Days are calculated based on assumptions of
        the base temperature of the current year.

        Parameters
        ----------
        temperatures : array
            Temperatures
        t_base_cooling : array
            Base temperature cooling

        Return
        ------
        shape_yd : array
            Fraction of heat for every day. Array-shape: 365, 1
        """
        cdd_d = hdd_cdd.calc_cdd(t_base_cooling, temperatures)
        shape_cdd_d = shape_handling.absolute_to_relative(cdd_d)

        return cdd_d, shape_cdd_d
    '''

    def get_fuel_shape_heating_hp_yh(self, data, tech_stock, rs_hdd_cy, tech_to_get_shape):
        """Convert daily shapes to houly based on robert sansom daily load for heatpump

        This is for non-peak.

        Parameters
        ---------
        data : dict
            data
        tech_stock : object
            Technology stock
        rs_hdd_cy : array
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

        list_dates = date_handling.fullyear_dates(start=date(data['base_yr'], 1, 1), end=date(data['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):

            # Take respectve daily fuel curve depending on weekday or weekend from Robert Sansom for heat pumps
            if date_handling.get_weekday_type(date_gasday) == 'holiday':
                daily_fuel_profile = np.divide(data[tech_to_get_shape]['holiday'], np.sum(data[tech_to_get_shape]['holiday'])) # WkendHourly gas shape. Robert Sansom hp curve
            else:
                daily_fuel_profile = np.divide(data[tech_to_get_shape]['workday'], np.sum(data[tech_to_get_shape]['workday'])) # Wkday Hourly gas shape. Robert Sansom hp curve

            # Calculate weighted average daily efficiency of heat pump
            average_eff_d = 0
            for hour, heat_share_h in enumerate(daily_fuel_profile):
                tech_eff = tech_stock.get_tech_attr('rs_space_heating', 'heat_pumps_gas', 'eff_cy')
                average_eff_d += heat_share_h * tech_eff[day][hour] # Hourly heat demand * heat pump efficiency

            # Convert daily service demand to fuel (Heat demand / efficiency = fuel)
            hp_daily_fuel = np.divide(rs_hdd_cy[day], average_eff_d)

            fuel_shape_d = hp_daily_fuel * daily_fuel_profile # Fuel distribution within day
            shape_yh_hp[day] = fuel_shape_d  # Distribute fuel of day according to fuel load curve
            shape_y_dh[day] = shape_handling.absolute_to_relative(fuel_shape_d) # Add normalised daily fuel curve

        # Convert absolute hourly fuel demand to relative fuel demand within a year
        shape_yh = np.divide(1, np.sum(shape_yh_hp)) * shape_yh_hp

        return shape_yh, shape_y_dh

    def get_shape_cooling_yh(self, data, cooling_shape, tech_to_get_shape):
        """Convert daily shape to hourly based on robert sansom daily load for boilers

        This is for non-peak.

        Every the day same

        Residential:
        Taken from Denholm, P., Ong, S., & Booten, C. (2012). Using Utility Load Data to
        Estimate Demand for Space Cooling and Potential for Shiftable Loads,
        (May), 23. Retrieved from http://www.nrel.gov/docs/fy12osti/54509.pdf

        Service:
        Knight, Dunn, Environments Carbon and Cooling in Uk Office Environments

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

    def ss_get_sector_enduse_shape(self, data, heating_shape, enduse):
        """Read generic shape for all technologies in a service sector enduse

        Parameters
        ---------
        data : dict
            data
        heating_shape : array
            Daily (yd) service demand shape for heat (percentage of yearly heat demand for every day)
        enduse : str
            Enduse where technology is used

        Returns
        -------
        shape_boilers_yh : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_boilers_y_dh : array
            Shape of distribution of fuel within every day of a year (total sum == 365)
        """
        shape_yh_generic_tech = np.zeros((365, 24))
        shape_y_dh_generic_tech = np.zeros((365, 24))

        if enduse not in data['ss_all_tech_shapes_dh']:
            pass
        else:
            shape_non_peak_dh = data['ss_all_tech_shapes_dh'][enduse]['shape_non_peak_dh']

            for day in range(365):
                shape_yh_generic_tech[day] = heating_shape[day] * shape_non_peak_dh[day]
                shape_y_dh_generic_tech[day] = shape_non_peak_dh[day]

        return shape_yh_generic_tech, shape_y_dh_generic_tech

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
        shape_boilers_yh : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_boilers_y_dh : array
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
        shape_boilers_yh = np.zeros((365, 24))
        shape_boilers_y_dh = np.zeros((365, 24))

        list_dates = date_handling.fullyear_dates(start=date(data['base_yr'], 1, 1), end=date(data['base_yr'], 12, 31))

        for day, date_gasday in enumerate(list_dates):

            # See wether day is weekday or weekend
            weekday_type = date_handling.get_weekday_type(date_gasday)

            # Take respectve daily fuel curve depending on weekday or weekend
            if weekday_type == 'holiday':
                # -----
                # The percentage of totaly yearly heat demand (heating_shape[day]) is distributed with daily fuel shape of boilers
                # Because boiler eff is constant, the  reflects the needed heat per hour
                # ------
                # Wkend Hourly gas shape. Robert Sansom boiler curve
                shape_boilers_yh[day] = heating_shape[day] * data[tech_to_get_shape]['holiday']

                shape_boilers_y_dh[day] = data[tech_to_get_shape]['holiday']
            else:
                # Wkday Hourly gas shape. Robert Sansom boiler curve
                shape_boilers_yh[day] = heating_shape[day] * data[tech_to_get_shape]['workday'] #yd shape

                shape_boilers_y_dh[day] = data[tech_to_get_shape]['workday'] #dh shape

        # Testing
        np.testing.assert_almost_equal(np.sum(shape_boilers_yh), 1, err_msg="Error in shape_boilers_yh: The sum of hourly shape is not 1: {}".format(np.sum(shape_boilers_yh)))

        return shape_boilers_yh, shape_boilers_y_dh
