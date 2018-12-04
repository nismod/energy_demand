""" A ``WeatherRegion`` object is is generated per
weather station and regional load profile and technology
stocks are assigned."""
import uuid
import numpy as np

from energy_demand.technologies import technological_stock
from energy_demand.profiles import load_profile
from energy_demand.profiles import hdd_cdd
from energy_demand.basic import basic_functions
from energy_demand import enduse_func
from energy_demand.initalisations import helpers
from energy_demand.profiles import generic_shapes
from energy_demand.basic import lookup_tables

class WeatherRegion(object):
    """WeaterRegion

    Arguments
    ----------
    name : str
        Unique identifyer of weather region
    latitude, longitude : float
        Coordinates
    assumptions : dict
        Assumptions
    technologies : list
        All technology assumptions
    enduses : list
        All enduses
    temp_by, temp_ey : array
        Temperature data
    tech_lp : dict
        Technology load profiles
    sectors : list
        Sectors

    Note
    ----
    - For each region, a technology stock is defined
    - regional specific fuel shapes are assigned to technologies
    """
    def __init__(
            self,
            name,
            latitude,
            longitude,
            assumptions,
            technologies,
            enduses,
            temp_by,
            temp_cy,
            tech_lp,
            sectors,
            crit_temp_min_max
        ):
        """Constructor of weather region
        """
        self.name = name
        self.longitude = longitude
        self.latitude = latitude

        fueltypes = lookup_tables.basic_lookups()['fueltypes']

        # Base temperatures of current year
        rs_t_base_heating_cy = assumptions.non_regional_vars['rs_t_base_heating'][assumptions.curr_yr]
        ss_t_base_heating_cy = assumptions.non_regional_vars['ss_t_base_heating'][assumptions.curr_yr]
        ss_t_base_cooling_cy = assumptions.non_regional_vars['ss_t_base_cooling'][assumptions.curr_yr]
        is_t_base_heating_cy = assumptions.non_regional_vars['is_t_base_heating'][assumptions.curr_yr]

        # ==================================================================
        # Technology stocks
        # ==================================================================
        rs_tech_stock = technological_stock.TechStock(
            'rs_tech_stock',
            technologies,
            assumptions.base_yr,
            assumptions.curr_yr,
            fueltypes,
            temp_by,
            temp_cy,
            assumptions.t_bases.rs_t_heating,
            enduses['residential'],
            rs_t_base_heating_cy,
            assumptions.specified_tech_enduse_by)

        ss_tech_stock = technological_stock.TechStock(
            'ss_tech_stock',
            technologies,
            assumptions.base_yr,
            assumptions.curr_yr,
            fueltypes,
            temp_by,
            temp_cy,
            assumptions.t_bases.ss_t_heating,
            enduses['service'],
            ss_t_base_heating_cy,
            assumptions.specified_tech_enduse_by)

        is_tech_stock = technological_stock.TechStock(
            'is_tech_stock',
            technologies,
            assumptions.base_yr,
            assumptions.curr_yr,
            fueltypes,
            temp_by,
            temp_cy,
            assumptions.t_bases.is_t_heating,
            enduses['industry'],
            ss_t_base_heating_cy,
            assumptions.specified_tech_enduse_by)

        self.tech_stock = {
            'residential': rs_tech_stock,
            'service': ss_tech_stock,
            'industry': is_tech_stock}

        # ==================================================================
        # Load profiles
        # ==================================================================
        flat_shape_yd, _, flat_shape_y_dh = generic_shapes.flat_shape()

        # ==================================================================
        # Residential submodel load profiles
        # ==================================================================
        load_profiles = load_profile.LoadProfileStock("load_profiles")
        dummy_sector = None

        # --------Calculate HDD/CDD of used weather year
        self.rs_hdd_by, _ = hdd_cdd.calc_reg_hdd(
            temp_by, assumptions.t_bases.rs_t_heating, assumptions.model_yeardays, crit_temp_min_max)
        self.rs_hdd_cy, rs_fuel_shape_heating_yd = hdd_cdd.calc_reg_hdd(
            temp_cy, rs_t_base_heating_cy, assumptions.model_yeardays, crit_temp_min_max)

        # --------Calculate HDD/CDD of base year weather year
        #self.rs_cdd_by, _ = hdd_cdd.calc_reg_cdd(
        #    temp_by, assumptions.t_bases.rs_t_cooling_by, assumptions.model_yeardays)
        #self.rs_cdd_cy, rs_fuel_shape_cooling_yd = hdd_cdd.calc_reg_cdd(
        #    temp_cy, rs_t_base_cooling_cy, assumptions.model_yeardays)

        # -------Calculate climate change correction factors
        try:
            f_heat_rs_y = np.nan_to_num(
                1.0 / float(np.sum(self.rs_hdd_by))) * np.sum(self.rs_hdd_cy)
            #self.f_cooling_rs_y = np.nan_to_num(
            #    1.0 / float(np.sum(self.rs_cdd_by))) * np.sum(self.rs_cdd_cy)
            f_cooling_rs_y = 1
        except ZeroDivisionError:
            f_heat_rs_y = 1
            f_cooling_rs_y = 1

        # Calculate rs peak day
        rs_peak_day = enduse_func.get_peak_day(self.rs_hdd_cy)

        # ========
        # Enduse specific profiles
        # ========
        # -- Apply enduse sepcific shapes for enduses with not technologies with own defined shapes
        for enduse in enduses['residential']:

            # Enduses where technology specific load profiles are defined for yh
            if enduse in ['rs_space_heating']:
                pass
            else:
                # Get all technologies of enduse
                tech_list = helpers.get_nested_dict_key(
                    assumptions.fuel_tech_p_by[enduse][dummy_sector])

                # Remove heat pumps from rs_water_heating
                tech_list = basic_functions.remove_element_from_list(tech_list, 'heat_pumps_electricity')

                shape_y_dh = insert_peak_dh_shape(
                    peak_day=rs_peak_day,
                    shape_y_dh=tech_lp['rs_shapes_dh'][enduse]['shape_non_peak_y_dh'],
                    shape_peak_dh=tech_lp['rs_shapes_dh'][enduse]['shape_peak_dh'])

                load_profiles.add_lp(
                    unique_identifier=uuid.uuid4(),
                    technologies=tech_list,
                    enduses=[enduse],
                    shape_yd=tech_lp['rs_shapes_yd'][enduse]['shape_non_peak_yd'],
                    shape_y_dh=shape_y_dh,
                    sectors=[dummy_sector],
                    model_yeardays=assumptions.model_yeardays)

        # ==========
        # Technology specific profiles for residential heating
        # ===========
        # ------Heating boiler
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['heating_const'],
            enduses=['rs_space_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_y_dh=tech_lp['rs_profile_boilers_y_dh'],
            sectors=[dummy_sector],
            model_yeardays=assumptions.model_yeardays)

        # ------Heating CHP
        rs_profile_chp_y_dh = insert_peak_dh_shape(
            peak_day=rs_peak_day,
            shape_y_dh=tech_lp['rs_profile_chp_y_dh'],
            shape_peak_dh=tech_lp['rs_lp_heating_CHP_dh']['peakday'])

        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['tech_CHP'],
            enduses=['rs_space_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_y_dh=rs_profile_chp_y_dh,
            sectors=[dummy_sector],
            model_yeardays=assumptions.model_yeardays)

        # ------Electric heating, storage heating (primary)
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['storage_heating_electricity'],
            enduses=['rs_space_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_y_dh=tech_lp['rs_profile_storage_heater_y_dh'],
            sectors=[dummy_sector],
            model_yeardays=assumptions.model_yeardays)

        # ------Electric heating secondary (direct elec heating)
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['secondary_heating_electricity'],
            enduses=['rs_space_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_y_dh=tech_lp['rs_profile_elec_heater_y_dh'],
            sectors=[dummy_sector],
            model_yeardays=assumptions.model_yeardays)

        # ------Heat pump heating
        rs_profile_hp_y_dh = insert_peak_dh_shape(
            peak_day=rs_peak_day,
            shape_y_dh=tech_lp['rs_profile_hp_y_dh'],
            shape_peak_dh=tech_lp['rs_lp_heating_hp_dh']['peakday'])

        rs_fuel_shape_hp_yh, rs_hp_shape_yd = get_fuel_shape_heating_hp_yh(
            tech_lp_y_dh=rs_profile_hp_y_dh,
            tech_stock=rs_tech_stock,
            rs_hdd_cy=self.rs_hdd_cy,
            model_yeardays=assumptions.model_yeardays)

        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['heating_non_const'],
            enduses=['rs_space_heating', 'rs_water_heating'],
            shape_y_dh=rs_profile_hp_y_dh,
            shape_yd=rs_hp_shape_yd,
            shape_yh=rs_fuel_shape_hp_yh,
            sectors=[dummy_sector],
            model_yeardays=assumptions.model_yeardays)

        # ------District_heating_electricity. Assumption made that same curve as CHP
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['tech_district_heating'],
            enduses=['rs_space_heating'],
            shape_yd=rs_fuel_shape_heating_yd,
            shape_y_dh=rs_profile_hp_y_dh,
            sectors=[dummy_sector],
            model_yeardays=assumptions.model_yeardays)

        # ==================================================================
        # Service Submodel load profiles
        # ==================================================================
        # --------HDD/CDD
        # current weather_yr
        self.ss_hdd_by, _ = hdd_cdd.calc_reg_hdd(
            temp_by, assumptions.t_bases.ss_t_heating, assumptions.model_yeardays, crit_temp_min_max)

        ss_hdd_cy, ss_fuel_shape_heating_yd = hdd_cdd.calc_reg_hdd(
            temp_cy, ss_t_base_heating_cy, assumptions.model_yeardays, crit_temp_min_max)

        self.ss_cdd_by, _ = hdd_cdd.calc_reg_cdd(
            temp_by, assumptions.t_bases.ss_t_cooling, assumptions.model_yeardays, crit_temp_min_max)

        ss_cdd_cy, ss_lp_cooling_yd = hdd_cdd.calc_reg_cdd(
            temp_cy, ss_t_base_cooling_cy, assumptions.model_yeardays, crit_temp_min_max)

        try:
            f_heat_ss_y = np.nan_to_num(
                1.0 / float(np.sum(self.ss_hdd_by))) * np.sum(ss_hdd_cy)
            f_cooling_ss_y = np.nan_to_num(
                1.0 / float(np.sum(self.ss_cdd_by))) * np.sum(ss_cdd_cy)
        except ZeroDivisionError:
            f_heat_ss_y = 1
            f_cooling_ss_y = 1

        # ========
        # Enduse specific profiles
        # ========
        # - Assign to each enduse the carbon fuel trust dataset
        for enduse in enduses['service']:

            # Skip temperature dependent end uses (regional) because load profile in regional load profile stock
            if enduse in assumptions.enduse_space_heating or enduse in assumptions.ss_enduse_space_cooling:
                pass
            else:
                for sector in sectors['service']:

                    # Get technologies with assigned fuel shares
                    tech_list = helpers.get_nested_dict_key(
                        assumptions.fuel_tech_p_by[enduse][sector])

                    # Apply correction factor for weekend_effect
                    shape_non_peak_yd_weighted = load_profile.abs_to_rel(
                        tech_lp['ss_shapes_yd'][enduse][sector]['shape_non_peak_yd'] * assumptions.ss_weekend_f)

                    load_profiles.add_lp(
                        unique_identifier=uuid.uuid4(),
                        technologies=tech_list,
                        enduses=[enduse],
                        shape_yd=shape_non_peak_yd_weighted,
                        shape_y_dh=tech_lp['ss_shapes_dh'][enduse][sector]['shape_non_peak_y_dh'],
                        model_yeardays=assumptions.model_yeardays,
                        sectors=[sector])

        # Apply correction factor for weekend_effect for space heating
        ss_fuel_shape_heating_yd_weighted = load_profile.abs_to_rel(
            ss_fuel_shape_heating_yd * assumptions.ss_weekend_f)

        # ========
        # Technology specific profiles
        # ========

        # Flatten list of all potential technologies
        ss_space_heating_tech_lists = list(assumptions.tech_list.values())
        all_techs_ss_space_heating = [item for sublist in ss_space_heating_tech_lists for item in sublist]


        # -----Heat pump (RESIDENTIAL HEAT PUMP PROFILE FOR SERVICE SECTOR)
        all_techs_ss_space_heating = basic_functions.remove_element_from_list(
            all_techs_ss_space_heating, 'heat_pumps_electricity')

        ss_fuel_shape_hp_yh, ss_hp_shape_yd = get_fuel_shape_heating_hp_yh(
            tech_lp_y_dh=rs_profile_hp_y_dh,
            tech_stock=rs_tech_stock,
            rs_hdd_cy=ss_hdd_cy,
            model_yeardays=assumptions.model_yeardays)

        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['heating_non_const'],
            enduses=['ss_space_heating', 'ss_water_heating'],
            sectors=sectors['service'],
            shape_y_dh=rs_profile_hp_y_dh,
            shape_yd=ss_hp_shape_yd,
            shape_yh=ss_fuel_shape_hp_yh,
            model_yeardays=assumptions.model_yeardays)

        # ---secondary_heater_electricity Info: The residential direct heating load profile is used
        all_techs_ss_space_heating = basic_functions.remove_element_from_list(
            all_techs_ss_space_heating, 'secondary_heater_electricity')

        # Get aggregated electricity load profile
        #ALTERNATIVE :tech_lp['ss_all_tech_shapes_dh']['ss_other_electricity']['shape_non_peak_y_dh']
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['secondary_heating_electricity'],
            enduses=['ss_space_heating'],
            sectors=sectors['service'],
            shape_yd=ss_fuel_shape_heating_yd_weighted,
            shape_y_dh=tech_lp['rs_profile_elec_heater_y_dh'],
            model_yeardays=assumptions.model_yeardays)
            # ELEC CURVE ss_fuel_shape_electricity # DIRECT HEATING ss_profile_elec_heater_yh

        # ---Heating technologies (all other)
        # (the heating shape follows the gas shape of aggregated sectors)
        # meaning that for all technologies, the load profile is the same
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=all_techs_ss_space_heating,
            enduses=['ss_space_heating'],
            sectors=sectors['service'],
            shape_yd=ss_fuel_shape_heating_yd_weighted,
            shape_y_dh=tech_lp['ss_all_tech_shapes_dh']['ss_space_heating']['shape_non_peak_y_dh'],
            model_yeardays=assumptions.model_yeardays)

        # --Add cooling technologies for service sector
        coolings_techs = assumptions.tech_list['cooling_const']

        for cooling_enduse in assumptions.ss_enduse_space_cooling:
            for sector in sectors['service']:

                # Apply correction factor for weekend_effect 'cdd_weekend_cfactors'
                ss_lp_cooling_yd_weighted = load_profile.abs_to_rel(
                    ss_lp_cooling_yd * assumptions.cdd_weekend_cfactors)

                load_profiles.add_lp(
                    unique_identifier=uuid.uuid4(),
                    technologies=coolings_techs,
                    enduses=[cooling_enduse],
                    sectors=[sector],
                    shape_yd=ss_lp_cooling_yd_weighted,
                    shape_y_dh=tech_lp['ss_profile_cooling_y_dh'],
                    model_yeardays=assumptions.model_yeardays)

        # ==================================================================
        # Industry submodel load profiles
        # ==================================================================

        # --------HDD/CDD
        # Current weather_yr
        self.is_hdd_by, _ = hdd_cdd.calc_reg_hdd(
            temp_by, assumptions.t_bases.is_t_heating, assumptions.model_yeardays, crit_temp_min_max)

        #is_cdd_by, _ = hdd_cdd.calc_reg_cdd(
        #    temp_by, assumptions.t_bases.is_t_cooling, assumptions.model_yeardays)

        # Take same base temperature as for service sector
        is_hdd_cy, is_fuel_shape_heating_yd = hdd_cdd.calc_reg_hdd(
            temp_cy, is_t_base_heating_cy, assumptions.model_yeardays, crit_temp_min_max)
        #is_cdd_cy, _ = hdd_cdd.calc_reg_cdd(
        #    temp_cy, ss_t_base_cooling_cy, assumptions.model_yeardays)

        try:
            f_heat_is_y = np.nan_to_num(1.0 / float(np.sum(self.is_hdd_by))) * np.sum(is_hdd_cy)
            #self.f_cooling_is_y = np.nan_to_num(1.0 / float(np.sum(is_cdd_by))) * np.sum(is_cdd_cy)
            f_cooling_is_y = 1
        except ZeroDivisionError:
            f_heat_is_y = 1
            f_cooling_is_y = 1

        # ========
        # Technology specific profiles
        # ========

        # --Heating technologies

        # Flatten list of all potential heating technologies
        is_space_heating_tech_lists = list(assumptions.tech_list.values())
        all_techs_is_space_heating = [item for sublist in is_space_heating_tech_lists for item in sublist]

        # Apply correction factor for weekend_effect for space heating load profile
        is_fuel_shape_heating_yd_weighted = load_profile.abs_to_rel(
            is_fuel_shape_heating_yd * assumptions.is_weekend_f)

        # - Direct electric heating
        # Remove tech from all space heating techs
        all_techs_is_space_heating = basic_functions.remove_element_from_list(
            all_techs_is_space_heating, 'secondary_heater_electricity')

        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=assumptions.tech_list['secondary_heating_electricity'],
            enduses=['is_space_heating'],
            sectors=sectors['industry'],
            shape_yd=is_fuel_shape_heating_yd_weighted,
            shape_y_dh=tech_lp['rs_profile_elec_heater_y_dh'],
            model_yeardays=assumptions.model_yeardays)

        # Add flat load profiles for non-electric heating technologies
        load_profiles.add_lp(
            unique_identifier=uuid.uuid4(),
            technologies=all_techs_is_space_heating,
            enduses=['is_space_heating'],
            sectors=sectors['industry'],
            shape_yd=is_fuel_shape_heating_yd_weighted,
            shape_y_dh=flat_shape_y_dh,
            model_yeardays=assumptions.model_yeardays)

        # Apply correction factor for weekend_effect to flat load profile for industry
        flat_shape_yd = flat_shape_yd * assumptions.is_weekend_f
        flat_shape_yd_weighted = load_profile.abs_to_rel(flat_shape_yd)

        # ========
        # Enduse specific profiles
        # ========
        for enduse in enduses['industry']:
            if enduse == "is_space_heating":
                pass # Do not create non regional stock because temp dependent
            else:
                for sector in sectors['industry']:

                    tech_list = helpers.get_nested_dict_key(
                        assumptions.fuel_tech_p_by[enduse][sector])

                    load_profiles.add_lp(
                        unique_identifier=uuid.uuid4(),
                        technologies=tech_list,
                        enduses=[enduse],
                        shape_yd=flat_shape_yd_weighted,
                        shape_y_dh=flat_shape_y_dh,
                        model_yeardays=assumptions.model_yeardays,
                        sectors=[sector])

        # ---------------
        # Load profiles
        # ---------------
        self.load_profiles = load_profiles

        self.f_heat = {
            'residential': f_heat_rs_y,
            'service': f_heat_ss_y,
            'industry': f_heat_is_y}

        self.f_colling = {
            'residential': f_cooling_rs_y,
            'service': f_cooling_ss_y,
            'industry': f_cooling_is_y}

def get_fuel_shape_heating_hp_yh(tech_lp_y_dh, tech_stock, rs_hdd_cy, model_yeardays):
    """Convert daily shapes to houly based on load for heatpump

    This is for non-peak.

    Arguments
    ---------
    tech_lp_y_dh : dict
        Technology load profiles
    tech_stock : object
        Technology stock
    rs_hdd_cy : array
        Heating Degree Days
    model_yeardays : array
        Modelled year days

    Returns
    -------
    shape_yh : array
        Yearly shape to calculate hourly load (total sum == 1)
    hp_yd : array
        Yd shape

    Note
    ----
    -  An average heat pump efficiency is calculated for the whole day
       depending on hourly temperatures.

    -  See XY in documentation for source of heat pumps
    """
    shape_yh_hp = np.zeros((365, 24), dtype="float")
    shape_y_dh = np.zeros((365, 24), dtype="float")

    tech_eff = tech_stock.get_tech_attr(
        'rs_space_heating',
        None,
        'heat_pumps_electricity',
        'eff_cy')

    # Convert daily service demand to fuel (fuel = Heat demand / efficiency)
    # As only the shape is of interest, the HDD
    # can be used as an indicator for fuel use (which correlates) directly
    hp_yd = rs_hdd_cy[:, np.newaxis] / tech_eff

    # Distribute daily according to fuel load curves of heat pumps
    shape_yh_hp = hp_yd * tech_lp_y_dh

    # Convert absolute hourly fuel demand to relative fuel demand within a year
    shape_yh = load_profile.abs_to_rel(shape_yh_hp)

    # Convert for every day the shape to absolute shape (tot sum for a full year == 365)
    _shape_y_dh_sum_rows = np.sum(shape_yh_hp, axis=1)

    with np.errstate(divide='ignore', invalid='ignore'):
        shape_y_dh = shape_yh_hp / _shape_y_dh_sum_rows[:, np.newaxis]
    shape_y_dh[np.isnan(shape_y_dh)] = 0

    # Select only modelled days
    return shape_yh[model_yeardays], hp_yd

def get_shape_cooling_yh(tech_shape, cooling_shape):
    """Convert daily shape to hourly

    Arguments
    ---------
    tech_shape : dict
        Technology shape
    cooling_shape : array
        Cooling profile

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
    shape_yd_cooling_tech = tech_shape * cooling_shape[:, np.newaxis]

    return shape_yd_cooling_tech

def ss_get_sector_enduse_shape(tech_lps, heating_lp_yd, enduse):
    """Read generic shape for all technologies in a service sector enduse

    Arguments
    ---------
    tech_lps : array
        Technology load profiles
    heating_lp_yd : array
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
    shape_yh_generic_tech = np.zeros((365, 24), dtype="float")

    if enduse not in tech_lps:
        pass
    else:
        shape_y_dh_generic_tech = tech_lps[enduse]['shape_non_peak_y_dh']
        shape_yh_generic_tech = heating_lp_yd[:, np.newaxis] * shape_y_dh_generic_tech

    return shape_yh_generic_tech, shape_y_dh_generic_tech

def insert_peak_dh_shape(
        peak_day,
        shape_y_dh,
        shape_peak_dh
    ):
    """Insert peak specific load profile of a technology
    Arguments
    ---------
    peak_day : int
        Peak day nr
    shape_y_dh : array
        Shape of technology for every day (total sum = 365)
    tech_lp_tech : dict
        Technolgy specific load profiles for different day types
    Returns
    -------
    shape_y_dh_inserted : array
        Array where on peak day the peak shape is inserted
    """
    shape_y_dh_inserted = np.copy(shape_y_dh)
    #print(np.sum(shape_y_dh_inserted))

    shape_y_dh_inserted[peak_day] = shape_peak_dh

    #print(np.sum(shape_y_dh_inserted))
    #assert np.sum(shape_y_dh_inserted) == 365.0

    return shape_y_dh_inserted

def get_weather_station_selection(
        all_weather_stations,
        counter,
        weather_yr
    ):
    """Select weather stations based on
    position in list

    Arguments
    --------
    counter : int
        Count to get weather station nr
    """
    all_stations_of_weather_yr = list(all_weather_stations[weather_yr].keys())

    # Sort
    all_stations_of_weather_yr.sort()

    try:
        # Select station according ot position in list
        station_id = all_stations_of_weather_yr[counter]

        all_weather_stations_out = {station_id: all_weather_stations[weather_yr][station_id]}
    except:
        # Not enough stations to select position in list
        station_id = False
        all_weather_stations_out = []
        print("... no weather station found")

    return all_weather_stations_out, station_id
