"""
Weather Region
===============
Depending on the number of weather stations, a ``WeatherRegion``
is generated per weather station. Within this regions,
regional load profiles are calculated.
"""
import uuid
import numpy as np
from energy_demand.technologies import technological_stock
from energy_demand.profiles import load_profile
from energy_demand.profiles import hdd_cdd

class WeatherRegion(object):
    """WeaterRegion

    Arguments
    ----------
    weather_region_name : str
        Unique identifyer of region_name
    TODO
    modeltype : str
        Model type

    Note
    ----
    - For each region_name, a technology stock is defined with help of
      regional temperature data technology specific
    - regional specific fuel shapes are assigned to technologies
    """
    def __init__(
            self,
            weather_region_name,
            sim_param,
            assumptions,
            lookups,
            all_enduses,
            temperature_data,
            tech_lp,
            sectors
        ):
        """Constructor of weather region
        """
        self.weather_region_name = weather_region_name

        # Temperatures
        temp_by = temperature_data[weather_region_name][sim_param['base_yr']]
        temp_cy = temperature_data[weather_region_name][sim_param['curr_yr']]

        rs_t_base_heating_cy = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'rs_t_base_heating')
        rs_t_base_cooling_cy = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'rs_t_base_cooling')
        rs_t_base_heating_by = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'rs_t_base_heating')
        rs_t_base_cooling_by = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'rs_t_base_cooling')
        ss_t_base_heating_cy = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'ss_t_base_heating')
        ss_t_base_cooling_cy = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'ss_t_base_cooling')
        ss_t_base_heating_by = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'ss_t_base_heating')
        ss_t_base_cooling_by = hdd_cdd.sigm_temp(
            sim_param, assumptions, 'ss_t_base_cooling')

        # -------------------
        # Technology stock
        # -------------------
        self.is_tech_stock = technological_stock.TechStock(
            'is_tech_stock',
            assumptions,
            sim_param,
            lookups,
            temp_by,
            temp_cy,
            assumptions['ss_t_base_heating']['base_yr'],
            all_enduses['is_all_enduses'],
            ss_t_base_heating_cy,
            assumptions['is_specified_tech_enduse_by']
            )

        self.rs_tech_stock = technological_stock.TechStock(
            'rs_tech_stock',
            assumptions,
            sim_param,
            lookups,
            temp_by,
            temp_cy,
            assumptions['rs_t_base_heating']['base_yr'],
            all_enduses['rs_all_enduses'],
            rs_t_base_heating_cy,
            assumptions['rs_specified_tech_enduse_by']
            )

        self.ss_tech_stock = technological_stock.TechStock(
            'ss_tech_stock',
            assumptions,
            sim_param,
            lookups,
            temp_by,
            temp_cy,
            assumptions['ss_t_base_heating']['base_yr'],
            all_enduses['ss_all_enduses'],
            ss_t_base_heating_cy,
            assumptions['ss_specified_tech_enduse_by']
            )

        # -------------------
        # Load profiles
        # ------------------
        self.rs_load_profiles = load_profile.LoadProfileStock("rs_load_profiles")

        # --------HDD/CDD
        rs_hdd_by, _ = hdd_cdd.get_reg_hdd(
            temp_by, rs_t_base_heating_by, assumptions['model_yeardays'])
        rs_cdd_by, _ = hdd_cdd.get_reg_cdd(
            temp_by, rs_t_base_cooling_by, assumptions['model_yeardays'], assumptions['model_yeardays_nrs'])
        rs_hdd_cy, rs_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(
            temp_cy, rs_t_base_heating_cy, assumptions['model_yeardays'])
        rs_cdd_cy, _ = hdd_cdd.get_reg_cdd(
            temp_cy, rs_t_base_cooling_cy, assumptions['model_yeardays'], assumptions['model_yeardays_nrs'])

        # Climate change correction factors
        try:
            self.rs_heating_factor_y = np.nan_to_num(
                1.0 / float(np.sum(rs_hdd_by))) * np.sum(rs_hdd_cy)
            self.rs_cooling_factor_y = np.nan_to_num(
                1.0 / float(np.sum(rs_cdd_by))) * np.sum(rs_cdd_cy)
        except ZeroDivisionError:
            self.rs_heating_factor_y = 1
            self.rs_cooling_factor_y = 1

        # yd peak factors for heating and cooling
        # (Needss full year necessary of temp data to calc peak days)
        rs_peak_yd_heating_factor = self.get_shape_peak_yd_factor(rs_hdd_cy)
        #rs_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(rs_cdd_cy)

        # --Specific heating technologies for residential sector
        rs_profile_storage_heater_yh, _ = self.get_shape_heating_boilers_yh(
            tech_lp,
            rs_fuel_shape_heating_yd,
            'rs_lp_storage_heating_dh',
            assumptions['model_yeardays'],
            assumptions['model_yeardays_nrs'],
            assumptions['model_yeardays_daytype'])

        rs_profile_elec_heater_yh, _ = self.get_shape_heating_boilers_yh(
            tech_lp,
            rs_fuel_shape_heating_yd,
            'rs_lp_second_heating_dh',
            assumptions['model_yeardays'],
            assumptions['model_yeardays_nrs'],
            assumptions['model_yeardays_daytype']
            )

        # boiler, non-peak
        rs_profile_boilers_yh, rs_profile_boilers_y_dh = self.get_shape_heating_boilers_yh(
            tech_lp,
            rs_fuel_shape_heating_yd,
            'rs_lp_heating_boilers_dh',
            assumptions['model_yeardays'],
            assumptions['model_yeardays_nrs'],
            assumptions['model_yeardays_daytype']
            )

        # heat pumps, non-peak
        rs_fuel_shape_hp_yh, rs_fuel_shape_hp_y_dh = self.get_fuel_shape_heating_hp_yh(
            tech_lp,
            self.rs_tech_stock,
            rs_hdd_cy,
            'rs_lp_heating_hp_dh',
            assumptions['model_yeardays'],
            assumptions['model_yeardays_daytype'])

        '''rs_fuel_shape_hybrid_tech_yh = self.get_shape_heating_hybrid_yh(
            self.rs_tech_stock,
            'rs_space_heating',
            rs_profile_boilers_y_dh,
            rs_fuel_shape_hp_y_dh,
            rs_fuel_shape_heating_yd,
            'hybrid_gas_electricity'
            )'''

        # Cooling residential
        #rs_fuel_shape_cooling_yh = self.get_shape_cooling_yh(
        # data, rs_fuel_shape_cooling_yd, 'rs_shapes_cooling_dh')

        # Heating boiler
        self.rs_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_const'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_profile_boilers_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=tech_lp['rs_lp_heating_boilers_dh']['peakday']
            )

        # Electric heating, primary...(storage)
        self.rs_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['primary_heating_electricity'],
            enduses=['rs_space_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_profile_storage_heater_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=tech_lp['rs_lp_storage_heating_dh']['peakday']
            )

        # Electric heating, secondary...
        self.rs_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['secondary_heating_electricity'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_profile_elec_heater_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=tech_lp['rs_lp_second_heating_dh']['peakday']
            )

        # Hybrid heating
        '''self.rs_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_hybrid'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_hybrid_tech_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor
            )'''

        # Heat pump heating
        self.rs_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_temp_dep'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_yh=rs_fuel_shape_hp_yh,
            enduse_peak_yd_factor=rs_peak_yd_heating_factor,
            shape_peak_dh=tech_lp['rs_lp_heating_hp_dh']['peakday']
            )

        #Service submodel
        self.ss_load_profiles = load_profile.LoadProfileStock("ss_load_profiles")

        # --------HDD/CDD
        ss_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by, assumptions['model_yeardays'])
        ss_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by, assumptions['model_yeardays'], assumptions['model_yeardays_nrs'])

        ss_hdd_cy, ss_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy, assumptions['model_yeardays'])
        ss_cdd_cy, _ = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy, assumptions['model_yeardays'], assumptions['model_yeardays_nrs'])

        try:
            self.ss_heating_factor_y = np.nan_to_num(
                1.0 / float(np.sum(ss_hdd_by))) * np.sum(ss_hdd_cy)
            self.ss_cooling_factor_y = np.nan_to_num(
                1.0 / float(np.sum(ss_cdd_by))) * np.sum(ss_cdd_cy)
        except ZeroDivisionError:
            self.ss_heating_factor_y = 1
            self.ss_cooling_factor_y = 1

        ss_peak_yd_heating_factor = self.get_shape_peak_yd_factor(ss_hdd_cy)
        #ss_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(ss_cdd_cy)

        # --Heating technologies for service sector
        # (the heating shape follows the gas shape of aggregated sectors)
        ss_fuel_shape_any_tech, ss_fuel_shape = self.ss_get_sector_enduse_shape(
            tech_lp, ss_fuel_shape_heating_yd, 'ss_space_heating', assumptions['model_yeardays_nrs'])

        # Cooling service
        #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_cooling_yd, 'ss_shapes_cooling_dh') # Service cooling
        #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_heating_yd, 'ss_shapes_cooling_dh') # Service cooling #USE HEAT YD BUT COOLING SHAPE
        #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, load_profile.abs_to_rel(ss_hdd_cy + ss_cdd_cy), 'ss_shapes_cooling_dh') # hdd & cdd

        # Hybrid
        '''ss_profile_hybrid_gas_elec_yh = self.get_shape_heating_hybrid_yh(
            self.ss_tech_stock,
            'ss_space_heating',
            ss_fuel_shape,
            ss_fuel_shape,
            ss_fuel_shape_heating_yd,
            'hybrid_gas_electricity')'''

        self.ss_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_const'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=sectors['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_peak_dh=tech_lp['ss_shapes_dh']
            )

        self.ss_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['primary_heating_electricity'],
            enduses=['ss_space_heating'],
            sectors=sectors['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            shape_peak_dh=tech_lp['rs_lp_storage_heating_dh']['peakday']
            )

        self.ss_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['secondary_heating_electricity'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            sectors=sectors['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor
            )

        '''self.ss_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_hybrid'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=sectors['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_profile_hybrid_gas_elec_yh,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor,
            )'''

        self.ss_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_temp_dep'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=sectors['ss_sectors'],
            shape_yd=ss_fuel_shape_heating_yd,
            shape_yh=ss_fuel_shape_any_tech,
            enduse_peak_yd_factor=ss_peak_yd_heating_factor
            )

        # Industry submodel
        self.is_load_profiles = load_profile.LoadProfileStock("is_load_profiles")

        # --------HDD/CDD
        is_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by, assumptions['model_yeardays'])
        is_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by, assumptions['model_yeardays'], assumptions['model_yeardays_nrs'])

        # Take same base temperature as for service sector
        is_hdd_cy, is_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, ss_t_base_heating_cy, assumptions['model_yeardays'])
        is_cdd_cy, _ = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy, assumptions['model_yeardays'], assumptions['model_yeardays_nrs'])

        try:
            self.is_heating_factor_y = np.nan_to_num(1.0 / float(np.sum(is_hdd_by))) * np.sum(is_hdd_cy)
            self.is_cooling_factor_y = np.nan_to_num(1.0 / float(np.sum(is_cdd_by))) * np.sum(is_cdd_cy)
        except ZeroDivisionError:
            self.is_heating_factor_y = 1
            self.is_cooling_factor_y = 1

        is_peak_yd_heating_factor = self.get_shape_peak_yd_factor(is_hdd_cy)
        #is_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(is_cdd_cy)

        # --Heating technologies for service sector (the heating shape follows
        # the gas shape of aggregated sectors)
        #Take from service sector
        is_fuel_shape_any_tech, _ = self.ss_get_sector_enduse_shape(
            tech_lp, is_fuel_shape_heating_yd, 'ss_space_heating', assumptions['model_yeardays_nrs'])

        self.is_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_const'],
            enduses=['is_space_heating'],
            sectors=sectors['is_sectors'],
            shape_yd=is_fuel_shape_heating_yd,
            shape_yh=is_fuel_shape_any_tech,
            enduse_peak_yd_factor=is_peak_yd_heating_factor
            )

        self.is_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['primary_heating_electricity'],
            enduses=['is_space_heating'],
            sectors=sectors['is_sectors'],
            shape_yd=is_fuel_shape_heating_yd,
            enduse_peak_yd_factor=is_peak_yd_heating_factor,
            shape_yh=is_fuel_shape_any_tech
            )

        self.is_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['secondary_heating_electricity'],
            enduses=['is_space_heating'],
            sectors=sectors['is_sectors'],
            shape_yd=is_fuel_shape_heating_yd,
            shape_yh=is_fuel_shape_any_tech,
            enduse_peak_yd_factor=is_peak_yd_heating_factor,
            )

        '''self.is_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_hybrid'],
            enduses=['is_space_heating'],
            sectors=sectors['is_sectors'],
            shape_yd=is_fuel_shape_heating_yd,
            shape_yh=is_fuel_shape_any_tech,
            enduse_peak_yd_factor=is_peak_yd_heating_factor,
            )'''

        self.is_load_profiles.add_load_profile(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions['tech_list']['tech_heating_temp_dep'],
            enduses=['is_space_heating'],
            sectors=sectors['is_sectors'],
            shape_yd=is_fuel_shape_heating_yd,
            shape_yh=is_fuel_shape_any_tech,
            enduse_peak_yd_factor=is_peak_yd_heating_factor
            )

    '''@classmethod
    def get_shape_heating_hybrid_yh(cls, tech_stock, enduse, fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, hybrid_tech):
        """Use yd shapes and dh shapes of hybrid technologies to generate yh shape

        Arguments
        ----------
        tech_stock : TODO
        enduse :
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
        fuel_shape_hybrid_y_dh = load_profile.get_hybrid_fuel_shapes_y_dh(
            fuel_shape_boilers_y_dh=fuel_shape_boilers_y_dh,
            fuel_shape_hp_y_dh=fuel_shape_hp_y_dh,
            tech_low_high_p=tech_stock.get_tech_attr(
                enduse, hybrid_tech, 'service_distr_hybrid_h_p')
            )

        # Calculate yh fuel shape
        fuel_shape_yh = fuel_shape_hybrid_y_dh * fuel_shape_heating_yd[:, np.newaxis]

        return fuel_shape_yh
    '''

    @classmethod
    def get_shape_peak_yd_factor(cls, demand_yd):
        """From yd shape calculate maximum relative yearly service demand which is provided in a day

        Arguments
        ----------
        demand_yd : shape
            Demand for energy service for every day in year

        Return
        ------
        max_factor_yd : float
            yd maximum factor

        Note
        -----
        If the shape is taken from heat and cooling demand the assumption is made that
        HDD and CDD are directly proportional to fuel usage
        """
        tot_demand_y = np.sum(demand_yd) # Total yearly demand
        max_demand_d = np.max(demand_yd) # Maximum daily demand
        max_factor_yd = (1.0 / tot_demand_y) * max_demand_d

        return max_factor_yd

    @classmethod
    def get_fuel_shape_heating_hp_yh(cls, tech_lp, tech_stock, rs_hdd_cy, tech, model_yeardays, model_yeardays_daytype):
        """Convert daily shapes to houly based on robert sansom daily load for heatpump TODO

        This is for non-peak.

        Arguments
        ---------
        sim_param : dict
            Simulation parameters
        tech_stock : object
            Technology stock
        rs_hdd_cy : array
            Heating Degree Days (model_yeardays_nrs, 1)
        tech : str
            Technology to get profile

        Returns
        -------
        hp_shape : array
            Daily shape how yearly fuel can be distributed to hourly
        shape_y_dh : array
            Shape of fuel shape for every day in a year (total sum = nr_of_days)

        Note
        ----
        The service is calculated based on the efficiency of gas
        heat pumps ``av_heat_pump_gas``

        The daily heat demand is converted to daily fuel depending on efficiency of
        heatpumps (assume if 100% heat pumps). In a final step the hourly fuel
        is converted to percentage of yearly fuel demand.

        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily fuel demand curve for heat pumps taken from:
        *Sansom, R. (2014). Decarbonising low grade heat for low carbon future.
        Dissertation, Imperial College London.*
        """
        shape_yh_hp = np.zeros((365, 24), dtype=float)
        shape_y_dh = np.zeros((365, 24), dtype=float)

        tech_eff = tech_stock.get_tech_attr('rs_space_heating', 'heat_pumps_gas', 'eff_cy')

        # from Robert Sansom for heat pump
        daily_fuel_profile_holiday = tech_lp[tech]['holiday'] / np.sum(tech_lp[tech]['holiday'])
        daily_fuel_profile_workday = tech_lp[tech]['workday'] / np.sum(tech_lp[tech]['workday'])

        for day_array_nr, yearday in enumerate(range(365)):
            if model_yeardays_daytype[yearday] == 'holiday':
                daily_fuel_profile = daily_fuel_profile_holiday
            else:
                daily_fuel_profile = daily_fuel_profile_workday

            # Calculate weighted average daily efficiency of heat pump
            # (Hourly heat demand * heat pump efficiency)
            #average_eff_d = np.sum(tech_eff[day_array_nr] * daily_fuel_profile)
            average_eff_d = tech_eff #BELUG
    
            # Convert daily service demand to fuel (Heat demand / efficiency = fuel)
            hp_daily_fuel = rs_hdd_cy[day_array_nr] / average_eff_d

            # Fuel distribution within day
            fuel_shape_d = hp_daily_fuel * daily_fuel_profile

            # Distribute fuel of day according to fuel load curve
            shape_yh_hp[day_array_nr] = fuel_shape_d

            # Add normalised daily fuel curve
            shape_y_dh[day_array_nr] = load_profile.abs_to_rel_no_nan(fuel_shape_d)

        # Convert absolute hourly fuel demand to relative fuel demand within a year
        shape_yh = load_profile.abs_to_rel(shape_yh_hp)

        # Select only modelled days
        shape_yh_selection = shape_yh[[model_yeardays]]
        shape_y_dh_selection = shape_y_dh[[model_yeardays]]

        return shape_yh_selection, shape_y_dh_selection

    @classmethod
    def get_shape_cooling_yh(cls, data, cooling_shape, tech):
        """Convert daily shape to hourly based on robert sansom daily load for boilers

        Arguments
        ---------
        data : dict
            data
        cooling_shape : array
            Cooling profile
        tech : str
            Technology to get profile

        Returns
        -------
        shape_yd_cooling_tech : array
            Shape of cooling devices

        Note
        ----
        The daily cooling demand (calculated with cdd) is distributed within the day
        fuel demand curve from:

        - **Residential**: Taken from *Denholm, P., Ong, S., & Booten, C. (2012).
          Using Utility Load Data to Estimate Demand for Space Cooling and
          Potential for Shiftable Loads, (May), 23.
          Retrieved from http://www.nrel.gov/docs/fy12osti/54509.pdf*

        - **Service**: *Knight, Dunn, Environments Carbon and Cooling in
          Uk Office Environments*
        """
        shape_yd_cooling_tech = data[tech] * cooling_shape[:, np.newaxis]

        return shape_yd_cooling_tech

    @classmethod
    def ss_get_sector_enduse_shape(cls, tech_lp, heating_shape, enduse, model_yeardays_nrs):
        """Read generic shape for all technologies in a service sector enduse

        Arguments
        ---------
        data : dict
            data
        heating_shape : array
            Daily (yd) service demand shape for heat (percentage of yearly
            heat demand for every day)
        enduse : str
            Enduse where technology is used

        Returns
        -------
        shape_boilers_yh : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_boilers_y_dh : array
            Shape of distribution of fuel within every day of a year (total sum == nr_of_days)
        """
        shape_yh_generic_tech = np.zeros((model_yeardays_nrs, 24), dtype=float)
        if enduse not in tech_lp['ss_all_tech_shapes_dh']:
            pass
        else:
            shape_non_peak_y_dh = tech_lp['ss_all_tech_shapes_dh'][enduse]['shape_non_peak_y_dh']

            shape_yh_generic_tech = heating_shape[:, np.newaxis] * shape_non_peak_y_dh
            shape_y_dh_generic_tech = shape_non_peak_y_dh

        return shape_yh_generic_tech, shape_y_dh_generic_tech

    @classmethod
    def get_shape_heating_boilers_yh(cls, tech_lp, heating_shape, technology, model_yeardays, model_yeardays_nrs, model_yeardays_daytype):
        """Convert daily fuel shape to hourly based on robert sansom daily load for boilers

        Arguments
        ---------
        sim_param : dict
            Simulation parameters
        heating_shape : array
            Profile (yh) for heat (percentage of yearly heat demand for every day)
        technology : str
            Technology to get shape

        Returns
        -------
        shape_boilers_yh : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_boilers_y_dh : array
            Shape of distribution of fuel within every day of a year (total sum == nr_of_days)

        Note
        ----
        - The assumption is made that boilers have constant efficiency for every hour in a year.
          Therefore the fuel demand correlates directly with the heat service demand.

        -  Furthermore the assumption is made that the profile is the same for all fueltypes.

        The daily heat demand (calculated with hdd) is distributed within the day
        fuel demand curve for boilers from:

        *Sansom, R. (2014). Decarbonising low grade heat for low carbon
        future. Dissertation, Imperial College London.*
        """
        shape_boilers_yh = np.zeros((model_yeardays_nrs, 24), dtype=float)
        shape_boilers_y_dh = np.zeros((model_yeardays_nrs, 24), dtype=float)

        for day_array_nr, yearday in enumerate(model_yeardays):
            if model_yeardays_daytype[yearday] == 'holiday':
                shape_boilers_yh[day_array_nr] = heating_shape[day_array_nr] * tech_lp[technology]['holiday']
                shape_boilers_y_dh[day_array_nr] = tech_lp[technology]['holiday']
            else: # Wkday Hourly gas shape.
                shape_boilers_yh[day_array_nr] = heating_shape[day_array_nr] * tech_lp[technology]['workday'] #yd
                shape_boilers_y_dh[day_array_nr] = tech_lp[technology]['workday'] #dh

        return shape_boilers_yh, shape_boilers_y_dh
