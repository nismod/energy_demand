"""All assumptions are either loaded in this file or definied here
"""
import logging
from energy_demand.read_write import read_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions, date_prop
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.initalisations import helpers
from energy_demand.technologies import fuel_service_switch

def load_non_param_assump(base_yr, paths, enduses, lookups, fuels):
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
    lookups : dict
        Lookups
    fuels : dict
        Fuels
    """
    logging.debug("... load non parameter assumptions")
    assumptions = {}

    yr_until_changed_all_things = 2050 #TODO

    # ============================================================
    # Model running mode (contrainsed or not constrained)
    # ============================================================

    # True:  Technologies are defined in ED model and fuel is provided
    # False: Heat is delievered not per technologies
    assumptions['mode_constrained'] = False

    # ============================================================
    # Modelled yeardays (if model whole year, set to 365)
    # ============================================================
    assumptions['model_yeardays'] = list(range(365))  # Modelled days

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
    #assumptions['virtual_dwelling_stock'] = True #OR newcastle is loaded

    # Change in floor area per person up to end_yr 1.0 = 100%
    # ASSUMPTION (if minus, check if new dwellings are needed)
    assumptions['assump_diff_floorarea_pp'] = 1
    assumptions['assump_diff_floorarea_pp_yr_until_changed'] = yr_until_changed_all_things

    # Specific Energy Demand factors per dwelling type could be defined
    # (e.g. per dwelling type or GVA class or residents....)

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

    # Floor area per dwelling type
    # Annex Table 3.1
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

    # Assumption about age distribution
    # Source: Housing Energy Fact Sheet
    # Average builing age within age class, fraction
    assumptions['dwtype_age_distr'] = {
        2015: {
            '1918':0.21,
            '1941': 0.36,
            '1977.5': 0.3,
            '1996.5': 0.08,
            '2002': 0.05}}

    # TODO: Get assumptions for heat loss coefficient
    # Include refurbishment of houses --> Change percentage of age distribution of houses -->
    # Which then again influences HLC
    # Change in floor depending on sector (if no change set to 1, if e.g. 10% decrease change to 0.9)

    # TODO: Project future demand based on seperate methodology
    assumptions['ss_floorarea_change_ey_p'] = {

        'yr_until_changed': yr_until_changed_all_things,

        'community_arts_leisure': 1,
        'education': 1,
        'emergency_services': 1,
        'health': 1,
        'hospitality': 1,
        'military': 1,
        'offices': 1,
        'retail': 1,
        'storage': 1,
        'other': 1}


    # ============================================================
    #  Scenario drivers
    # ============================================================
    assumptions['scenario_drivers'] = {}

    # --Residential SubModel
    assumptions['scenario_drivers']['rs_submodule'] = {
        'rs_space_heating': ['floorarea', 'hlc'], #Do not use also pop because otherwise problems that e.g. existing stock + new has smaller scen value than... floorarea already contains pop, Do not use HDD because otherweise double count
        'rs_water_heating': ['population'],
        'rs_lighting': ['population', 'floorarea'],
        'rs_cooking': ['population'],
        'rs_cold': ['population'],
        'rs_wet': ['population'],
        'rs_consumer_electronics': ['population'],
        'rs_home_computing': ['population']}

    # --Servicse Submodel
    assumptions['scenario_drivers']['ss_submodule'] = {
        'ss_space_heating': ['floorarea'],
        'ss_water_heating': [],
        'ss_lighting': ['floorarea'],
        'ss_catering': [],
        'ss_computing': [],
        'ss_space_cooling': ['floorarea'],
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
    # Smart meter related base year assumptions
    # ============================================================
    # Fraction of population with smart meters for base year
    assumptions['smart_meter_assump'] = {}
    assumptions['smart_meter_assump']['smart_meter_p_by'] = 0.1
    assumptions['smart_meter_assump']['smart_meter_diff_params'] = {
        'sig_midpoint': 0,
        'sig_steeppness': 1}

    # ============================================================
    # Base temperature related base year assumptions
    # ============================================================
    assumptions['rs_t_base_heating'] = {}
    assumptions['ss_t_base_heating'] = {}
    assumptions['rs_t_base_cooling'] = {}
    assumptions['ss_t_base_cooling'] = {}
    assumptions['rs_t_base_heating']['rs_t_base_heating_base_yr'] = 15.5
    assumptions['ss_t_base_heating']['ss_t_base_heating_base_yr'] = 15.5
    assumptions['rs_t_base_cooling']['rs_t_base_cooling_base_yr'] = 21
    assumptions['ss_t_base_cooling']['ss_t_base_cooling_base_yr'] = 21

    # ============================================================
    # Assumption related to technologies
    # ============================================================
    assumptions['technologies'], assumptions['tech_list'] = read_data.read_technologies(
        paths['path_technologies'])

    # --Heat pumps   
    # Share of installed heat pumps (ASHP to GSHP) (0.7 e.g. 0.7 ASHP and 0.3 GSHP)
    split_hp_ashp_gshp = 0.5
    assumptions['installed_heat_pump'] = tech_related.generate_ashp_gshp_split(
        split_hp_ashp_gshp)

    # Add heat pumps to technologies
    assumptions['technologies'], assumptions['tech_list']['tech_heating_temp_dep'], assumptions['heat_pumps'] = tech_related.generate_heat_pump_from_split(
        [],
        assumptions['technologies'],
        assumptions['installed_heat_pump'])

    # ============================================================
    # Enduse technology definition list
    # ============================================================
    assumptions['enduse_space_heating'] = ['rs_space_heating', 'rs_space_heating', 'is_space_heating']
    assumptions['enduse_space_cooling'] = ['rs_space_cooling', 'ss_space_cooling', 'is_space_cooling']
    assumptions['tech_list']['enduse_water_heating'] = ['rs_water_heating', 'ss_water_heating']

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
    # ============================================================
    # Sigmoid parameters for temperature
    assumptions['base_temp_diff_params'] = {
        'sig_midpoint': 0,
        'sig_steeppness': 1,
        'yr_until_changed': yr_until_changed_all_things}

    # ============================================================
    # Fuel Stock Definition
    # Provide for every fueltype of an enduse
    # the share of fuel which is used by technologies for the 
    # base year
    # ============================================================
    assumptions = assumptions_fuel_shares.assign_by_fuel_tech_p(
        assumptions,
        enduses,
        lookups)

    # ============================================================
    # Scenaric fuel switches
    # ============================================================
    assumptions['rs_fuel_switches'] = read_data.read_fuel_switches(
        paths['rs_path_fuel_switches'], enduses, lookups)
    assumptions['ss_fuel_switches'] = read_data.read_fuel_switches(
        paths['ss_path_fuel_switches'], enduses, lookups)
    assumptions['is_fuel_switches'] = read_data.read_fuel_switches(
        paths['is_path_fuel_switches'], enduses, lookups)

    # ============================================================
    # Scenaric service switches
    # ============================================================
    assumptions['rs_share_service_tech_ey_p'], assumptions['rs_enduse_tech_maxL_by_p'], assumptions['rs_service_switches'] = read_data.read_service_switch(
        paths['rs_path_service_switch'], assumptions['rs_specified_tech_enduse_by'])
    assumptions['ss_share_service_tech_ey_p'], assumptions['ss_enduse_tech_maxL_by_p'], assumptions['ss_service_switches'] = read_data.read_service_switch(
        paths['ss_path_service_switch'], assumptions['ss_specified_tech_enduse_by'])
    assumptions['is_share_service_tech_ey_p'], assumptions['is_enduse_tech_maxL_by_p'], assumptions['is_service_switches'] = read_data.read_service_switch(
        paths['is_path_industry_switch'], assumptions['is_specified_tech_enduse_by'])

    # ============================================================
    # Scenaric capacity switches
    # Warning: Overwrites other switches
    # ============================================================
    assumptions = fuel_service_switch.calc_service_switch_capacity(
        paths,
        enduses,
        assumptions,
        fuels,
        base_yr)

    # ========================================
    # Helper functions
    # ========================================

    # Generate dummy technologies
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
    ##testing_functions.testing_service_switch_insert(
    # assumptions['ss_fuel_tech_p_by'], assumptions['rs_fuel_switches'])
    ##testing_functions.testing_service_switch_insert(
    # assumptions['ss_fuel_tech_p_by'], assumptions['ss_fuel_switches'])

    # Test if fuel shares sum up to 1 within each fueltype
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

def update_assumptions(technologies, factor_achieved):
    """Updates calculations based on assumptions

    Note
    ----
    This needs to be run everytime an assumption is changedf

    """
    technologies = helpers.helper_set_same_eff_all_tech(
        technologies,
        factor_achieved)

    return technologies
