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
    base_yr : int
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
    #   Model calibration factors
    # ============================================================
    #
    #   These calibration factors are used to match the modelled
    #   electrictiy demand better with the validation data.
    #
    #   Weekend effects are used to distribut energy demands
    #   between working and weekend days. With help of these
    #   factors, the demand on weekends and holidays can be
    #   be lowered compared to working days.
    #   This factor can be applied either directly to an enduse
    #   or to the hdd or cdd calculations (to correct cooling
    #   or heating demand)
    #
    #       ss_t_cooling_weekend_factor : float
    #           Weekend effect for cooling enduses
    #       ss_weekend_factor : float
    #           WWeekend effect for service submodel enduses
    #       is_weekend_factor : float
    #           Weekend effect for industry submodel enduses
    # ------------------------------------------------------------
    assumptions['ss_t_cooling_weekend_factor'] = 0.6    # 0.6
    assumptions['ss_weekend_factor'] = 0.8              # 0.8
    assumptions['is_weekend_factor'] = 0.4              # 0.4

    # ============================================================
    #   Modelled day related factors
    # ============================================================
    #
    #   Weekend
    #
    #       model_yeardays_nrs : int
    #           Number of modelled yeardays (default=365)
    #       model_yearhours_nrs : int
    #           Number of modelled yearhours (default=8760)
    #        model_yeardays_date : dict
    #           Contains for the base year for each days
    #           the information wheter this is a working or holiday
    # ------------------------------------------------------------
    assumptions['model_yeardays'] = list(range(365))

    # Calculate dates of modelled days
    assumptions['model_yeardays_date'] = []
    for yearday in assumptions['model_yeardays']:
        assumptions['model_yeardays_date'].append(
            date_prop.yearday_to_date(base_yr, yearday))

    assumptions['model_yeardays_nrs'] = len(assumptions['model_yeardays'])
    assumptions['model_yearhours_nrs'] = len(assumptions['model_yeardays']) * 24

    # ============================================================
    #   Dwelling stock related assumptions
    # ============================================================
    #
    #   Assumptions to generate a virtual dwelling stock
    #
    #       assump_diff_floorarea_pp : float
    #           Change in floor area per person (%, 1=100%)
    #       assump_diff_floorarea_pp_yr_until_changed : int
    #           Year until this change in floor area happens
    #       assump_dwtype_distr_by : dict
    #           Housing Stock Distribution by Type
    #               Source: UK Housing Energy Fact File, Table 4c
    #       assump_dwtype_distr_future : dict
    #           welling type distribution end year
    #               Source: UK Housing Energy Fact File, Table 4c
    #       assump_dwtype_floorarea_by : dict
    #           Floor area per dwelling type (Annex Table 3.1)
    #               Source: UK Housing Energy Fact File, Table 4c
    #       assump_dwtype_floorarea_future : dict
    #           Floor area per dwelling type
    #               Source: UK Housing Energy Fact File, Table 4c
    #       dwtype_age_distr : dict
    #           Floor area per dwelling type
    #               Source: Housing Energy Fact Sheet)
    #       yr_until_changed : int
    #           Year until change is realised
    #
    # https://www.gov.uk/government/statistics/english-housing-survey-2014-to-2015-housing-stock-report
    # ------------------------------------------------------------
    assumptions['assump_diff_floorarea_pp'] = 1.0

    assumptions['assump_diff_floorarea_pp_yr_until_changed'] = yr_until_changed_all_things

    assumptions['assump_dwtype_distr_by'] = {
        'semi_detached': 0.26,
        'terraced': 0.283,
        'flat': 0.203,
        'detached': 0.166,
        'bungalow': 0.088}

    assumptions['assump_dwtype_distr_future'] = {

        # Year until change is implemented
        'yr_until_changed': yr_until_changed_all_things,

        'semi_detached': 0.26,
        'terraced': 0.283,
        'flat': 0.203,
        'detached': 0.166,
        'bungalow': 0.088}

    assumptions['assump_dwtype_floorarea_by'] = {
        'semi_detached': 96,
        'terraced': 82.5,
        'flat': 61,
        'detached': 147,
        'bungalow': 77}

    assumptions['assump_dwtype_floorarea_future'] = {

        'yr_until_changed': yr_until_changed_all_things,

        'semi_detached': 96,
        'terraced': 82.5,
        'flat': 61,
        'detached': 147,
        'bungalow': 77}

    # (Average builing age within age class, fraction)
    # Note: the number of refurbished houses can be changed ?? TODO: IMPELEMENT AS SCENARIO
    assumptions['dwtype_age_distr'] = {
        2015: {
            '1918' :0.21,
            '1941': 0.36,
            '1977.5': 0.3,
            '1996.5': 0.08,
            '2002': 0.05}}

    # ============================================================
    #   Scenario drivers TODO: CHECK all scenario drivers
    # ============================================================
    #
    #   For every enduse the relevant factors which affect enduse
    #   consumption can be added in a list.
    #
    #   Note:   If e.g. floorarea and population are added, the
    #           effects will be overestimates (i.e. no multi-
    #           collinearity are considered).
    #
    #       scenario_drivers : dict
    #           Scenario drivers per enduse
    # ------------------------------------------------------------
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
    #   Cooling related assumptions
    # ============================================================
    #
    #   Parameters related to cooling enduses are defined here.
    #
    #   assump_cooling_floorarea : int
    #       The percentage of cooled floor space in the base year
    #
    #   Literature
    #   ----------
    #   Abela, A. et al. (2016). Study on Energy Use by Air
    #   Conditioning. Bre, (June), 31. Retrieved from
    #   https://www.bre.co.uk/filelibrary/pdf/projects/aircon-energy-use
    #   /StudyOnEnergyUseByAirConditioningFinalReport.pdf
    # ------------------------------------------------------------
    assumptions['assump_cooling_floorarea'] = {}

    # (see Abela et al. 2016)
    assumptions['assump_cooling_floorarea']['cooled_ss_floorarea_by'] = 0.35

    # ============================================================
    # Smart meter related base year assumptions
    # ============================================================
    #
    #   Parameters related to smart metering
    #
    #   smart_meter_p_by : int
    #       The percentage of households with smart meters in by
    #   smart_meter_diff_params : dict
    #       Sigmoid diffusion parameter of smater meters        
    # ------------------------------------------------------------
    assumptions['smart_meter_assump'] = {}
    assumptions['smart_meter_assump']['smart_meter_p_by'] = 0.1
    assumptions['smart_meter_assump']['smart_meter_diff_params'] = {
        'sig_midpoint': 0,
        'sig_steeppness': 1}

    # ============================================================
    # Base temperature assumptions
    # ============================================================
    #
    #   Parameters related to smart metering
    #
    #   rs_t_heating_by : int
    #       Residential submodel base temp of heating of base year
    #   rs_t_cooling_by : int
    #       Residential submodel base temp of cooling of base year
    #   base_temp_diff_params : dict
    #       Sigmoid temperature diffusion parameters
    #   ...
    #
    #   Note
    #   ----
    #   Because demand for cooling cannot directly be linked to
    #   calculated cdd, the paramters 'ss_t_cooling_by' is used
    #   as a calibration factor. By artifiallcy lowering this
    #   parameter, the energy demand assignement over the days
    #   in a year is improved.
    # ------------------------------------------------------------
    assumptions['t_bases'] = {}
    assumptions['t_bases']['rs_t_heating_by'] = 15.5    #
    assumptions['t_bases']['rs_t_cooling_by'] = 21

    assumptions['t_bases']['ss_t_heating_by'] = 15.5    #
    assumptions['t_bases']['ss_t_cooling_by'] = 5       #

    assumptions['t_bases']['is_t_heating_by'] = 15.5    #
    #assumptions['t_bases']['is_t_cooling_by'] = Not implemented
    
    assumptions['base_temp_diff_params'] = {
        'sig_midpoint': 0,
        'sig_steeppness': 1,
        'yr_until_changed': yr_until_changed_all_things}

    # ============================================================
    # Enduses lists affed by hdd/cdd
    # ============================================================
    #
    #   These lists show for which enduses temperature related
    #   calculations are performed.
    #
    #   enduse_space_heating : list
    #       All enduses for which hdd are used for yd calculations
    #   enduse_rs_space_cooling : list
    #       All residential enduses for which cdd are used for
    #       yd calculations
    #   ss_enduse_space_cooling : list
    #       All service submodel enduses for which cdd are used for
    #       yd calculations
    # ------------------------------------------------------------
    assumptions['enduse_space_heating'] = [
        'rs_space_heating', 'ss_space_heating', 'is_space_heating']

    assumptions['enduse_rs_space_cooling'] = []
    #['ss_fans', 'ss_cooling_humidification', 'ss_cooled_storage']
    assumptions['ss_enduse_space_cooling'] = ['ss_cooling_humidification']

    #TODO: REPLAE NON DEFINED TECH IN FLUETPYES NOT WITH DUMMY TECH BUT ONLY IF NONE TECHNOLOGY AT ALL IS DEFINED
    # ============================================================
    # Assumption related to technologies
    # ============================================================
    #
    #   Assumptions related to technologies
    #
    #   split_hp_gshp_to_ashp_by : list
    #       Split between GSHP and ASHP (in %, 1=100%),
    #       Share of installed heat pumps in base year (ASHP to GSHP)
    # ------------------------------------------------------------
    assumptions['split_hp_gshp_to_ashp_by'] = 0.1

    assumptions['technologies'], assumptions['tech_list'] = read_data.read_technologies(
        paths['path_technologies'],
        fueltypes)

    assumptions['installed_heat_pump_by'] = tech_related.generate_ashp_gshp_split(
        assumptions['split_hp_gshp_to_ashp_by'])

    # Add heat pumps to technologies
    assumptions['technologies'], assumptions['tech_list']['tech_heating_temp_dep'], assumptions['heat_pumps'] = tech_related.generate_heat_pump_from_split(
        assumptions['technologies'],
        assumptions['installed_heat_pump_by'],
        fueltypes)

    # Collect all heating technologies
    assumptions['heating_technologies'] = assumptions[
        'tech_list']['tech_CHP'] + assumptions[
            'tech_list']['tech_heating_const'] + assumptions[
                'tech_list']['tech_heating_temp_dep'] + assumptions[
                    'tech_list']['tech_district_heating']

    # ============================================================
    # Enduse diffusion paramters
    # ============================================================
    #
    #   Assumptions related to general diffusion
    #
    #   This parameters are used to specify e.g. diffusion of
    #   an enduse which is not specified by technologies
    #   or the diffusion of a policy of changing a parameter
    #   over time.
    # ------------------------------------------------------------
    assumptions['enduse_overall_change'] = {}
    assumptions['enduse_overall_change']['other_enduse_mode_info'] = {
        'diff_method': 'linear', # sigmoid or linear
        'sigmoid': {
            'sig_midpoint': 0,
            'sig_steeppness': 1}}

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
    # Read in fuel and capacity switches
    # ============================================================

    # Read in scenaric fuel switches
    assumptions['rs_fuel_switches'] = read_data.read_fuel_switches(
        paths['rs_path_fuel_switches'], enduses, fueltypes)
    assumptions['ss_fuel_switches'] = read_data.read_fuel_switches(
        paths['ss_path_fuel_switches'], enduses, fueltypes)
    assumptions['is_fuel_switches'] = read_data.read_fuel_switches(
        paths['is_path_fuel_switches'], enduses, fueltypes)

    # Read in scenaric service switches
    assumptions['rs_service_switches'] = read_data.service_switch(
        paths['rs_path_service_switch'], assumptions['technologies'])
    assumptions['ss_service_switches'] = read_data.service_switch(
        paths['ss_path_service_switch'], assumptions['technologies'])
    assumptions['is_service_switches'] = read_data.service_switch(
        paths['is_path_industry_switch'], assumptions['technologies'])

    # Read in scenaric capacity switches
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

    assumptions['rs_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['rs_fuel_tech_p_by'])
    assumptions['ss_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['ss_fuel_tech_p_by'])
    assumptions['is_dummy_enduses'] = tech_related.get_enduses_with_dummy_tech(
        assumptions['is_fuel_tech_p_by'])

    testing_functions.testing_fuel_tech_shares(
        assumptions['rs_fuel_tech_p_by'])
    testing_functions.testing_fuel_tech_shares(
        assumptions['ss_fuel_tech_p_by'])
    testing_functions.testing_fuel_tech_shares(
        assumptions['is_fuel_tech_p_by'])
    testing_functions.testing_tech_defined(
        assumptions['technologies'], assumptions['rs_specified_tech_enduse_by'])
    testing_functions.testing_tech_defined(
        assumptions['technologies'], assumptions['ss_specified_tech_enduse_by'])
    testing_functions.testing_tech_defined(
        assumptions['technologies'], assumptions['is_specified_tech_enduse_by'])

    return assumptions

def update_assumptions(
        technologies,
        factor_achieved,
        split_hp_gshp_to_ashp_ey
    ):
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
