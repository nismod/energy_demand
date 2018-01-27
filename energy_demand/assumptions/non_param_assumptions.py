"""All assumptions are either loaded in this file or definied here
"""
import logging
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions, date_prop
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.initalisations import helpers

def load_non_param_assump(
        base_yr,
        paths,
        enduses,
        fueltypes,
        fueltypes_nr
    ):
    """Initialise assumptions and load all assumptions
    which are not defined as parameters for smif (e.g. base
    year values for assumptions)

    Parameters
    ----------
    base_yr : dict
        Simulation parameters
    paths : dict
        Paths
    enduses : dict
        Enduses
    fueltypes : dict
        Fueltypes lookup
    """
    logging.debug("... load non parameter assumptions")
    assumptions = {}

    yr_until_changed_all_things = 2050 #TODO

    # ============================================================
    # Modelled yeardays (if model whole year, set to 365)
    # ============================================================
    assumptions['model_yeardays'] = list(range(365))

    # Calculate dates of modelled days
    assumptions['model_yeardays_date'] = []
    for yearday in assumptions['model_yeardays']:
        assumptions['model_yeardays_date'].append(
            date_prop.yearday_to_date(base_yr, yearday))

    # Nr of modelled days and hours
    assumptions['model_yeardays_nrs'] = len(assumptions['model_yeardays'])
    assumptions['model_yearhours_nrs'] = len(assumptions['model_yeardays']) * 24

    # ============================================================
    # Dwelling stock related assumptions
    # ============================================================
    # Change in floor area per person up to end_yr 1.0 = 100%
    assumptions['assump_diff_floorarea_pp'] = 1
    assumptions['assump_diff_floorarea_pp_yr_until_changed'] = yr_until_changed_all_things

    # Dwelling type distribution base year (fixed)
    # Source: Table 4c: Housing Stock Distribution by Type, UK Housing Energy Fact File
    assumptions['assump_dwtype_distr_by'] = {
        'semi_detached': 0.26,
        'terraced': 0.283,
        'flat': 0.203,
        'detached': 0.166,
        'bungalow': 0.088}

    # Dwelling type distribution end year
    # Source: Housing Energy Fact File, Table 4c: Housing Stock Distribution by Type
    assumptions['assump_dwtype_distr_future'] = {

        # Year until change is implemented
        'yr_until_changed': yr_until_changed_all_things,

        'semi_detached': 0.26,
        'terraced': 0.283,
        'flat': 0.203,
        'detached': 0.166,
        'bungalow': 0.088}

    # Floor area per dwelling type (Annex Table 3.1)
    # https://www.gov.uk/government/statistics/english-housing-survey-2014-to-2015-housing-stock-report
    assumptions['assump_dwtype_floorarea_by'] = {
        'semi_detached': 96,
        'terraced': 82.5,
        'flat': 61,
        'detached': 147,
        'bungalow': 77}

    # Floor area per dwelling type
    assumptions['assump_dwtype_floorarea_future'] = {

        # Year until change is implemented
        'yr_until_changed': yr_until_changed_all_things,

        'semi_detached': 96,
        'terraced': 82.5,
        'flat': 61,
        'detached': 147,
        'bungalow': 77}

    # Assumption about age distribution (Source: Housing Energy Fact Sheet)
    # (Average builing age within age class, fraction)
    # Note: By changing this fraction, the number of refurbished houses can be
    # be changed
    assumptions['dwtype_age_distr'] = {
        2015: {
            '1918' :0.21,
            '1941': 0.36,
            '1977.5': 0.3,
            '1996.5': 0.08,
            '2002': 0.05}}

    # ============================================================
    # Scenario drivers
    # TODO: CHECK all scenario drivers
    # ============================================================
    assumptions['scenario_drivers'] = {}

    # --Residential SubModel
    assumptions['scenario_drivers']['rs_submodule'] = {
        'rs_space_heating': ['floorarea', 'hlc'], # Do not use HDD or pop because otherweise double count
        'rs_water_heating': ['population'],
        'rs_lighting': ['population', 'floorarea'],
        'rs_cooking': ['population'],
        'rs_cold': ['population'],
        'rs_wet': ['population'],
        'rs_consumer_electronics': ['population'],
        'rs_home_computing': ['population']}

    # --Service Submodel (Table 5.5a)
    assumptions['scenario_drivers']['ss_submodule'] = {
        'ss_space_heating': ['floorarea'],
        'ss_water_heating': ['population'],
        'ss_lighting': ['floorarea'],
        'ss_catering': ['population'],
        'ss_ICT_equipment': ['population'],
        'ss_cooling_humidification': ['floorarea'],
        'ss_fans': ['floorarea'],
        'ss_small_power': ['population'],
        'ss_cooled_storage': ['floorarea'],
        'ss_other_gas': ['floorarea'],
        'ss_other_electricity': ['floorarea']}

    # --Industry Submodel
    assumptions['scenario_drivers']['is_submodule'] = {
        'is_high_temp_process': ['gva'],
        'is_low_temp_process': ['gva'],
        'is_drying_separation': ['gva'],
        'is_motors': ['gva'],
        'is_compressed_air': ['gva'],
        'is_lighting': ['gva'],
        'is_space_heating': ['gva'],
        'is_other': ['gva'],
        'is_refrigeration': ['gva']}


    # ============================================================
    # Cooling related assumptions
    # ============================================================
    assumptions['assump_cooling_floorarea'] = {}
    assumptions['assump_cooling_floorarea']['cooled_ss_floorarea_by'] = 0.35

    # ============================================================
    # Smart meter related base year assumptions
    # ============================================================
    assumptions['smart_meter_assump'] = {}
    assumptions['smart_meter_assump']['smart_meter_p_by'] = 0.1
    assumptions['smart_meter_assump']['smart_meter_diff_params'] = {
        'sig_midpoint': 0,
        'sig_steeppness': 1}

    # ============================================================
    # Base temperature related base year assumptions
    # ============================================================
    assumptions['t_bases'] = {}
    assumptions['t_bases']['rs_t_heating_by'] = 15.5    #
    assumptions['t_bases']['rs_t_cooling_by'] = 0

    assumptions['t_bases']['ss_t_heating_by'] = 15.5    #.5
    assumptions['t_bases']['ss_t_cooling_by'] = 5       # 12

    assumptions['t_bases']['is_t_heating_by'] = 15.5    #.5
    #assumptions['t_bases']['is_t_cooling_by'] = Not implemented

    # -------
    # Model calibration factors to incorporate weekend effects
    # -------
    assumptions['ss_t_cooling_weekend_factor'] = 0.6    # 0.6
    assumptions['ss_weekend_factor'] = 0.8              # 0.8
    assumptions['is_weekend_factor'] = 0.4              # 0.4

    # ============================================================
    # Enduse technology definition lists
    # Define which end uses are affected by temperatures
    # ============================================================
    assumptions['enduse_space_heating'] = [
        'rs_space_heating', 'ss_space_heating', 'is_space_heating']
    assumptions['enduse_water_heating'] = [
        'rs_water_heating', 'ss_water_heating']

    assumptions['enduse_rs_space_cooling'] = []
    assumptions['ss_enduse_space_cooling'] = ['ss_fans', 'ss_cooling_humidification', 'ss_cooled_storage']#['ss_cooling_humidification']#, 'ss_fans'] #['ss_fans', 'ss_cooling_humidification', 'ss_cooled_storage']

    #TODO: REPLAE NON DEFINED TECH IN FLUETPYES NOT WITH DUMMY TECH BUT ONLY IF NONE TECHNOLOGY AT ALL IS DEFINED
    # ============================================================
    # Assumption related to technologies
    # ============================================================
    assumptions['technologies'], assumptions['tech_list'] = read_data.read_technologies(
        paths['path_technologies'],
        fueltypes)

    # --Heat pumps. Share of installed heat pumps in base year (ASHP to GSHP)
    assumptions['split_hp_gshp_to_ashp_by'] = 0.1
    assumptions['installed_heat_pump_by'] = tech_related.generate_ashp_gshp_split(
        assumptions['split_hp_gshp_to_ashp_by'])

    # Add heat pumps to technologies
    assumptions['technologies'], assumptions['tech_list']['tech_heating_temp_dep'], assumptions['heat_pumps'] = tech_related.generate_heat_pump_from_split(
        assumptions['technologies'],
        assumptions['installed_heat_pump_by'],
        fueltypes)

    # Define specifically all heating technologies
    assumptions['heating_technologies'] = [
        'boiler_solid_fuel',
        'boiler_gas',
        'boiler_electricity',
        'boiler_oil',
        'boiler_biomass',
        'boiler_hydrogen',
        'boiler_condensing_gas',
        'boiler_condensing_oil',
        'stirling_micro_CHP_gas',
        'fuel_cell_CHP',
        'storage_heater_electricity',
        'secondary_heater_electricity',
        'heat_pumps_hydrogen',
        'heat_pumps_electricity',
        'district_heating_electricity',
        'district_heating_gas',
        'district_heating_biomass']

    # ============================================================
    # Enduse diffusion parameters
    # ============================================================
    assumptions['enduse_overall_change'] = {}
    assumptions['enduse_overall_change']['other_enduse_mode_info'] = {
        'diff_method': 'linear', # sigmoid or linear
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1}}

    # ============================================================
    # Temperature diffusion parameters
    # Sigmoid parameters for temperature
    # ============================================================
    assumptions['base_temp_diff_params'] = {
        'sig_midpoint': 0,
        'sig_steeppness': 1,
        'yr_until_changed': yr_until_changed_all_things}

    # ============================================================
    # Fuel Stock Definition
    # Provide for every fueltype of an enduse
    # the share of fuel which is used by technologies for thebase year
    # ============================================================
    assumptions = assumptions_fuel_shares.assign_by_fuel_tech_p(
        assumptions,
        enduses,
        fueltypes,
        fueltypes_nr)

    # ============================================================
    # Scenaric fuel switches
    # ============================================================
    assumptions['rs_fuel_switches'] = read_data.read_fuel_switches(
        paths['rs_path_fuel_switches'], enduses, fueltypes)
    assumptions['ss_fuel_switches'] = read_data.read_fuel_switches(
        paths['ss_path_fuel_switches'], enduses, fueltypes)
    assumptions['is_fuel_switches'] = read_data.read_fuel_switches(
        paths['is_path_fuel_switches'], enduses, fueltypes)

    # ============================================================
    # Read in scenaric service switches
    # ============================================================
    assumptions['rs_service_switches'] = read_data.service_switch(
        paths['rs_path_service_switch'], assumptions['technologies'])
    assumptions['ss_service_switches'] = read_data.service_switch(
        paths['ss_path_service_switch'], assumptions['technologies'])
    assumptions['is_service_switches'] = read_data.service_switch(
        paths['is_path_industry_switch'], assumptions['technologies'])

    # ============================================================
    # Read in scenaric capacity switches
    # Warning: Overwrites other switches
    # ============================================================
    # Reading in assumptions on capacity installations from csv file
    assumptions['capacity_switches'] = {}
    assumptions['capacity_switches']['rs_capacity_switches'] = read_data.capacity_installations(
        paths['rs_path_capacity_installation'])
    assumptions['capacity_switches']['ss_capacity_switches'] = read_data.capacity_installations(
        paths['ss_path_capacity_installation'])
    assumptions['capacity_switches']['is_capacity_switches'] = read_data.capacity_installations(
        paths['is_path_capacity_installation'])

    # ========================================
    # Helper functions
    # ========================================
    assumptions['rs_fuel_tech_p_by'], assumptions['rs_specified_tech_enduse_by'], assumptions['technologies'] = tech_related.insert_dummy_tech(
        assumptions['technologies'], assumptions['rs_fuel_tech_p_by'], assumptions['rs_specified_tech_enduse_by'])
    assumptions['ss_fuel_tech_p_by'], assumptions['ss_specified_tech_enduse_by'], assumptions['technologies'] = tech_related.insert_dummy_tech(
        assumptions['technologies'], assumptions['ss_fuel_tech_p_by'], assumptions['ss_specified_tech_enduse_by'])
    assumptions['is_fuel_tech_p_by'], assumptions['is_specified_tech_enduse_by'], assumptions['technologies'] = tech_related.insert_dummy_tech(
        assumptions['technologies'], assumptions['is_fuel_tech_p_by'], assumptions['is_specified_tech_enduse_by'])

    # All enduses with dummy technologies
    assumptions['rs_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['rs_fuel_tech_p_by'])
    assumptions['ss_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['ss_fuel_tech_p_by'])
    assumptions['is_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['is_fuel_tech_p_by'])

    # ============================================================
    # Helper functions
    # ============================================================
    testing_functions.testing_fuel_tech_shares(assumptions['rs_fuel_tech_p_by'])
    testing_functions.testing_fuel_tech_shares(assumptions['ss_fuel_tech_p_by'])
    testing_functions.testing_fuel_tech_shares(assumptions['is_fuel_tech_p_by'])

    testing_functions.testing_tech_defined(
        assumptions['technologies'], assumptions['rs_specified_tech_enduse_by'])
    testing_functions.testing_tech_defined(
        assumptions['technologies'], assumptions['ss_specified_tech_enduse_by'])
    testing_functions.testing_tech_defined(
        assumptions['technologies'], assumptions['is_specified_tech_enduse_by'])

    return assumptions

def update_assumptions(technologies, factor_achieved, split_hp_gshp_to_ashp_ey):
    """Updates technology related properties based on
    scenario assumptions. Calculate average efficiency of
    heat pumps depending on mix of GSHP and ASHP,
    set the efficiency achieval factor of all factor according
    to strategy assumptions

    Parameters
    ----------
    technologies : dict
        Technologies
    factor_achieved : float
        Factor achieved
    split_hp_gshp_to_ashp_ey : float
        Mix of GSHP and GSHP

    Note
    ----
    This needs to be run everytime an assumption is changed
    """
    # Assign same achieved efficiency factor for all technologies
    technologies = helpers.set_same_eff_all_tech(
        technologies,
        factor_achieved)

    # Calculate average eff of hp depending on fraction of GSHP to ASHP
    installed_heat_pump_ey = tech_related.generate_ashp_gshp_split(
        split_hp_gshp_to_ashp_ey)

    technologies = tech_related.calc_av_heat_pump_eff_ey(
        technologies, installed_heat_pump_ey)

    return technologies
