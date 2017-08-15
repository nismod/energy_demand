"""Residential model"""
# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member
from datetime import date
import uuid
import numpy as np
import energy_demand.technological_stock as technological_stock
from energy_demand.scripts_basic import date_handling
from energy_demand.scripts_shape_handling import shape_handling
from energy_demand.scripts_shape_handling import hdd_cdd
from energy_demand.scripts_shape_handling import generic_shapes

class WeatherRegion(object):
    """WeaterRegion

    TODO: CREAT SHAPE WITH WEATHER STATION

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
    def __init__(self, weather_region_name, data, modeltype):
        """Constructor
        """
        # Weather region station name
        self.weather_region_name = weather_region_name

        # Temperatures
        temp_by = data['temperature_data'][weather_region_name][data['base_sim_param']['base_yr']]
        temp_cy = data['temperature_data'][weather_region_name][data['base_sim_param']['curr_yr']]

        # Base temperatures
        rs_t_base_heating_cy = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'rs_t_base_heating')
        rs_t_base_cooling_cy = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'rs_t_base_cooling')
        rs_t_base_heating_by = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'rs_t_base_heating')
        rs_t_base_cooling_by = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'rs_t_base_cooling')
        ss_t_base_heating_cy = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'ss_t_base_heating')
        ss_t_base_cooling_cy = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'ss_t_base_cooling')
        ss_t_base_heating_by = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'ss_t_base_heating')
        ss_t_base_cooling_by = hdd_cdd.sigm_t_base(data['base_sim_param'], data['assumptions'], 'ss_t_base_cooling')

        # -------------------
        # Technology stock
        # -------------------
        if modeltype == 'is_submodel':
            self.is_tech_stock = technological_stock.TechStock(
                'is_tech_stock',
                data,
                temp_by,
                temp_cy,
                data['assumptions']['ss_t_base_heating']['base_yr'],
                data['is_all_enduses'],
                ss_t_base_heating_cy,
                data['assumptions']['is_all_specified_tech_enduse_by']
                )
        elif modeltype == 'rs_submodel':
            self.rs_tech_stock = technological_stock.TechStock(
                'rs_tech_stock',
                data,
                temp_by,
                temp_cy,
                data['assumptions']['rs_t_base_heating']['base_yr'],
                data['rs_all_enduses'],
                rs_t_base_heating_cy,
                data['assumptions']['rs_all_specified_tech_enduse_by']
                )
        elif modeltype == 'ss_submodel':
            self.ss_tech_stock = technological_stock.TechStock(
                'ss_tech_stock',
                data,
                temp_by,
                temp_cy,
                data['assumptions']['ss_t_base_heating']['base_yr'],
                data['ss_all_enduses'],
                ss_t_base_heating_cy,
                data['assumptions']['ss_all_specified_tech_enduse_by']
                )

        # -------------------
        # Load profiles
        # -------------------
        if modeltype == 'rs_submodel':

            # --------Profiles
            self.rs_load_profiles = shape_handling.LoadProfileStock("rs_load_profiles")

            # --------HDD/CDD
            rs_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, rs_t_base_heating_by)
            rs_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, rs_t_base_cooling_by)
            rs_hdd_cy, rs_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy)
            rs_cdd_cy, rs_fuel_shape_cooling_yd = hdd_cdd.get_reg_cdd(temp_cy, rs_t_base_cooling_cy)

            # Climate change correction factors (Assumption: Demand for heat correlates directly with fuel)
            self.rs_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(rs_hdd_by))) * np.sum(rs_hdd_cy) #could be slightly speed up with np.isnan
            self.rs_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(rs_cdd_by))) * np.sum(rs_cdd_cy)

            # yd peak factors for heating and cooling (factor to calculate max daily demand from yearly demand)
            rs_peak_yd_heating_factor = self.get_shape_peak_yd_factor(rs_hdd_cy)
            rs_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(rs_cdd_cy)

            # --Specific heating technologies for residential sector
            rs_fuel_shape_storage_heater_yh, rs_fuel_shape_storage_heater_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_space_heating_storage_heater_elec_heating_dh')
            rs_fuel_shape_elec_heater_yh, rs_fuel_shape_elec_heater_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_space_heating_second_elec_heating_dh')

            rs_fuel_shape_boilers_yh, rs_fuel_shape_boilers_y_dh = self.get_shape_heating_boilers_yh(data, rs_fuel_shape_heating_yd, 'rs_shapes_heating_boilers_dh') # boiler, non-peak
            rs_fuel_shape_hp_yh, rs_fuel_shape_hp_y_dh = self.get_fuel_shape_heating_hp_yh(data, self.rs_tech_stock, rs_hdd_cy, 'rs_shapes_heating_heat_pump_dh') # heat pumps, non-peak

            rs_fuel_shape_hybrid_tech_yh = self.get_shape_heating_hybrid_yh(self.rs_tech_stock, 'rs_space_heating', rs_fuel_shape_boilers_y_dh, rs_fuel_shape_hp_y_dh, rs_fuel_shape_heating_yd, 'hybrid_gas_electricity') #, 'boiler_gas', 'heat_pumps_electricity') # Hybrid gas electric

            # Cooling residential
            rs_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, rs_fuel_shape_cooling_yd, 'rs_shapes_cooling_dh')

            # Heating boiler
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_const'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                sectors=data['rs_sectors'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_boilers_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_heating_boilers_dh']['peakday']
                )

            # Electric heating, primary...(storage)
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['primary_heating_electricity'],
                enduses=['rs_space_heating'],
                sectors=data['rs_sectors'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_storage_heater_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_space_heating_storage_heater_elec_heating_dh']['peakday']
                )

            # Electric heating, secondary...
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['secondary_heating_electricity'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                sectors=data['rs_sectors'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_elec_heater_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_space_heating_second_elec_heating_dh']['peakday']
                )

            # Hybrid heating
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_hybrid'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                sectors=data['rs_sectors'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_hybrid_tech_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor
                )

            # Heat pump heating
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_temp_dep'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                sectors=data['rs_sectors'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_hp_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_heating_heat_pump_dh']['peakday']
                )

        elif modeltype == 'ss_submodel':

            # --------Profiles
            self.ss_load_profiles = shape_handling.LoadProfileStock("ss_load_profiles")

            # --------HDD/CDD
            ss_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by)
            ss_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by)

            ss_hdd_cy, ss_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy)
            ss_cdd_cy, ss_fuel_shape_cooling_yd = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy)

            self.ss_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(ss_hdd_by))) * np.sum(ss_hdd_cy)
            self.ss_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(ss_cdd_by))) * np.sum(ss_cdd_cy)
    
            ss_peak_yd_heating_factor = self.get_shape_peak_yd_factor(ss_hdd_cy)
            ss_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(ss_cdd_cy)

            # --Heating technologies for service sector (the heating shape follows the gas shape of aggregated sectors)
            ss_fuel_shape_any_tech, ss_fuel_shape = self.ss_get_sector_enduse_shape(data, ss_fuel_shape_heating_yd, 'ss_space_heating')
                       
            # Cooling service
            #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_cooling_yd, 'ss_shapes_cooling_dh') # Service cooling
            #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_heating_yd, 'ss_shapes_cooling_dh') # Service cooling #USE HEAT YD BUT COOLING SHAPE
            #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, shape_handling.absolute_to_relative(ss_hdd_cy + ss_cdd_cy), 'ss_shapes_cooling_dh') # hdd & cdd
            ss_fuel_shape_hybrid_gas_elec_yh = self.get_shape_heating_hybrid_yh(self.ss_tech_stock, 'ss_space_heating', ss_fuel_shape, ss_fuel_shape, ss_fuel_shape_heating_yd, 'hybrid_gas_electricity') #, 'boiler_gas', 'heat_pumps_electricity') # Hybrid

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_const'],
                enduses=['ss_space_heating', 'ss_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor,
                shape_peak_dh=data['ss_shapes_dh']
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['primary_heating_electricity'],
                enduses=['ss_space_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_space_heating_storage_heater_elec_heating_dh']['peakday']
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['secondary_heating_electricity'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_hybrid'],
                enduses=['ss_space_heating', 'ss_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_hybrid_gas_elec_yh,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor,
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_temp_dep'],
                enduses=['ss_space_heating', 'ss_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor
                )

        elif modeltype == 'is_submodel':
            
            # --------Profiles
            self.is_load_profiles = shape_handling.LoadProfileStock("is_load_profiles")

            # --------HDD/CDD
            is_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by)
            is_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by)

            # Take same base temperature as for service sector
            is_hdd_cy, is_fuel_shape_heating_yd  = hdd_cdd.get_reg_hdd(temp_cy, ss_t_base_heating_cy)
            is_cdd_cy, is_fuel_shape_cooling_yd  = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy)

            self.is_heating_factor_y = np.nan_to_num(np.divide(1.0, np.sum(is_hdd_by))) * np.sum(is_hdd_cy)
            self.is_cooling_factor_y = np.nan_to_num(np.divide(1.0, np.sum(is_cdd_by))) * np.sum(is_cdd_cy)
            
            is_peak_yd_heating_factor = self.get_shape_peak_yd_factor(is_hdd_cy)
            is_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(is_cdd_cy)

            # --Heating technologies for service sector (the heating shape follows the gas shape of aggregated sectors)
            #Take from service sector
            is_fuel_shape_any_tech, is_fuel_shape = self.ss_get_sector_enduse_shape(data, is_fuel_shape_heating_yd, 'ss_space_heating')

            #Flat profiles
            shape_peak_dh, shape_non_peak_dh, shape_peak_yd_factor, shape_non_peak_yd, shape_non_peak_yh = generic_shapes.generic_flat_shape()

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_const'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                shape_peak_dh=shape_peak_dh
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['primary_heating_electricity'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                shape_yh=is_fuel_shape_any_tech
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['secondary_heating_electricity'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_hybrid'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_temp_dep'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                shape_peak_dh=shape_peak_dh
                )

    def get_shape_heating_hybrid_yh(self, tech_stock, enduse, fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, hybrid_tech):
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
        # Create dh shapes for every day from relative dh shape of hybrid technologies
        fuel_shape_hybrid_y_dh = shape_handling.get_hybrid_fuel_shapes_y_dh(
            fuel_shape_boilers_y_dh=fuel_shape_boilers_y_dh,
            fuel_shape_hp_y_dh=fuel_shape_hp_y_dh,
            tech_low_high_p=tech_stock.get_tech_attr(enduse, hybrid_tech, 'service_distr_hybrid_h_p')
            )

        # Calculate yh fuel shape
        fuel_shape_yh = fuel_shape_hybrid_y_dh * fuel_shape_heating_yd[:, np.newaxis]

        # Testing
        ## TESTINGnp.testing.assert_almost_equal(np.sum(fuel_shape_yh), 1, decimal=3, err_msg="ERROR XY: The hybridy yh shape does not sum up to 1.0")

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

        daily_fuel_profile_holiday = np.divide(data[tech_to_get_shape]['holiday'], np.sum(data[tech_to_get_shape]['holiday']))
        daily_fuel_profile_workday = np.divide(data[tech_to_get_shape]['workday'], np.sum(data[tech_to_get_shape]['workday']))

        tech_eff = tech_stock.get_tech_attr('rs_space_heating', 'heat_pumps_gas', 'eff_cy')

        for day, date_gasday in enumerate(data['base_sim_param']['list_dates']):

            # Take respectve daily fuel curve depending on weekday or weekend from Robert Sansom for heat pumps
            if date_handling.get_weekday_type(date_gasday) == 'holiday':
                daily_fuel_profile = daily_fuel_profile_holiday
            else:
                daily_fuel_profile = daily_fuel_profile_workday

            # Calculate weighted average daily efficiency of heat pump
            average_eff_d = 0
            for hour, heat_share_h in enumerate(daily_fuel_profile):
                average_eff_d += heat_share_h * tech_eff[day][hour] # Hourly heat demand * heat pump efficiency

            # Convert daily service demand to fuel (Heat demand / efficiency = fuel)
            hp_daily_fuel = np.divide(rs_hdd_cy[day], average_eff_d)

            # Fuel distribution within day
            fuel_shape_d = hp_daily_fuel * daily_fuel_profile

            # Distribute fuel of day according to fuel load curve
            shape_yh_hp[day] = fuel_shape_d

            # Add normalised daily fuel curve
            shape_y_dh[day] = shape_handling.absolute_to_relative_without_nan(fuel_shape_d)

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
        shape_yd_cooling_tech = data[tech_to_get_shape] * cooling_shape[:, np.newaxis]

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

        if enduse not in data['ss_all_tech_shapes_dh']:
            pass
        else:
            shape_non_peak_dh = data['ss_all_tech_shapes_dh'][enduse]['shape_non_peak_dh']

            shape_yh_generic_tech = heating_shape[:, np.newaxis] * shape_non_peak_dh #Multiplyacross row (365, ) with (365,24)
            shape_y_dh_generic_tech = shape_non_peak_dh

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

        list_dates = date_handling.fullyear_dates(
            start=date(data['base_sim_param']['base_yr'], 1, 1),
            end=date(data['base_sim_param']['base_yr'], 12, 31)
            )

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
        ## TESTINGnp.testing.assert_almost_equal(np.sum(shape_boilers_yh), 1, err_msg="Error in shape_boilers_yh: The sum of hourly shape is not 1: {}".format(np.sum(shape_boilers_yh)))

        return shape_boilers_yh, shape_boilers_y_dh
