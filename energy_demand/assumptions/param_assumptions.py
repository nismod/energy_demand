"""
Assumptions provided as parameters to smif
This script can be run to write out all paramters as YAML
file
"""
import logging
from energy_demand.read_write import read_data, write_data
from energy_demand.technologies import tech_related
from energy_demand.basic import testing_functions as testing
from energy_demand.assumptions import assumptions_fuel_shares
from energy_demand.initalisations import helpers
from energy_demand.basic import date_prop
from energy_demand.technologies import fuel_service_switch
from energy_demand.basic import basic_functions

def load_param_assump(paths, assumptions):
    """All assumptions of the energy demand model
    are loaded and added to the data dictionary

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict
    """
    logging.debug("... write assumptions to yaml file")

    yr_until_changed_all_things = 2050 #TODO

    # ============================================================
    #  Demand management assumptions (daily demand shape)
    #  An improvement in load factor improvement can be assigned
    #  for every enduse (peak shaving)
    #
    #  Example: 0.2 --> Improvement in load factor until ey
    # ============================================================
    assumptions['demand_management'] = {}
    assumptions['demand_management']['param_infos'] = [{
        "name": "demand_management_yr_until_changed",
        "absolute_range": "(10, 20)",
        "description": "Year until demand management assumptions are fully realised",
        "suggested_range": "(2015 - 2100)",
        "default_value": '2050',
        "units": 'years'}]

    # Year until ld if implemented
    assumptions['demand_management']['demand_management_yr_until_changed'] = yr_until_changed_all_things

    assumptions['demand_management']['enduses_demand_managent'] = {

        #Residential submodule
        'demand_management_improvement__rs_space_heating': 0,
        'demand_management_improvement__rs_water_heating': 0,
        'demand_management_improvement__rs_lighting': 0,
        'demand_management_improvement__rs_cooking': 0,
        'demand_management_improvement__rs_cold': 0,
        'demand_management_improvement__rs_wet': 0,
        'demand_management_improvement__rs_consumer_electronics': 0,
        'demand_management_improvement__rs_home_computing': 0,

        # Service submodule
        'demand_management_improvement__ss_space_heating': 0,
        'demand_management_improvement__ss_water_heating': 0,
        'demand_management_improvement__ss_lighting': 0,
        'demand_management_improvement__ss_catering': 0,
        'demand_management_improvement__ss_computing': 0,
        'demand_management_improvement__ss_space_cooling': 0,
        'demand_management_improvement__ss_other_gas': 0,
        'demand_management_improvement__ss_other_electricity': 0,

        # Industry submodule
        'demand_management_improvement__is_high_temp_process': 0,
        'demand_management_improvement__is_low_temp_process': 0,
        'demand_management_improvement__is_drying_separation': 0,
        'demand_management_improvement__is_motors': 0,
        'demand_management_improvement__is_compressed_air': 0,
        'demand_management_improvement__is_lighting': 0,
        'demand_management_improvement__is_space_heating': 0,
        'demand_management_improvement__is_other': 0,
        'demand_management_improvement__is_refrigeration': 0}

    # Helper function to create description of parameters for all enduses
    for demand_name, _ in assumptions['demand_management']['enduses_demand_managent'].items():
        assumptions['demand_management']['param_infos'].append({
            "name": "demand_management_improvement__{}".format(demand_name),
            "absolute_range": "0, 100)",
            "description": "reduction in load factor for enduse {}".format(demand_name),
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'})

    # =======================================
    # Climate Change assumptions
    # Temperature changes for every month for future year
    # =======================================
    assumptions['climate_change_temp_diff_month'] = {}
    assumptions['climate_change_temp_diff_month']['param_infos'] = [
        {
            "name": "climate_change_temp_diff_yr_until_changed",
            "absolute_range": "2015-2100",
            "description": "Year until climate temperature changes are fully realised",
            "suggested_range": "(2030, 2100)",
            "default_value": '2050',
            "units": 'year'
        }
    ]

    assumptions['climate_change_temp_diff_month']['temps'] = {
        'climate_change_temp_d__Jan': 0,
        'climate_change_temp_d__Feb': 0,
        'climate_change_temp_d__Mar': 0,
        'climate_change_temp_d__Apr': 0,
        'climate_change_temp_d__May': 0,
        'climate_change_temp_d__Jun': 0,
        'climate_change_temp_d__Jul': 0,
        'climate_change_temp_d__Aug': 0,
        'climate_change_temp_d__Sep': 0,
        'climate_change_temp_d__Oct': 0,
        'climate_change_temp_d__Nov': 0,
        'climate_change_temp_d__Dec': 0}
    
    assumptions['climate_change_temp_diff_month']['climate_change_temp_diff_yr_until_changed'] = yr_until_changed_all_things

    for month_python, _ in enumerate(assumptions['climate_change_temp_diff_month']['temps']):
        month_str = basic_functions.get_month_from_int(month_python + 1)
        assumptions['demand_management']['param_infos'].append(
            {
                "name": "climate_change_temp_d__{}".format(month_str),
                "absolute_range": (-10, 10),
                "description": "Temperature change for month {}".format(month_str),
                "suggested_range": (-5, 5),
                "default_value": 0,
                "units": '°C'
            })

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # The diffusion is asumed to be linear
    # ============================================================
    # Parameters info
    assumptions['rs_t_base_heating']['param_infos'] = [{
        "name": "rs_t_base_heating_future_yr",
        "absolute_range": "(10, 20)",
        "description": "Base temperature assumption residential heating",
        "suggested_range": "(13, 17)",
        "default_value": assumptions['rs_t_base_heating']['rs_t_base_heating_base_yr'],
        "units": '°C'}]

    # Future base year temperature
    assumptions['rs_t_base_heating']['rs_t_base_heating_future_yr'] = 15.5

    # Parameters info
    assumptions['ss_t_base_heating']['param_infos'] = [{
        "name": "ss_t_base_heating",
        "absolute_range": "(10, 20)",
        "description": "Base temperature assumption service sector heating",
        "suggested_range": "(13, 17)",
        "default_value": assumptions['ss_t_base_heating']['ss_t_base_heating_base_yr'],
        "units": '°C'}]

        # Future base year temperature
    assumptions['ss_t_base_heating']['ss_t_base_heating_future_yr'] = 15.5

    # Cooling base temperature
    assumptions['rs_t_base_cooling']['param_infos'] = [{
        "name": "ss_t_base_heating",
        "absolute_range": "(20, 25)",
        "description": "Base temperature assumption residential sector cooling",
        "suggested_range": "(13, 17)",
        "default_value": assumptions['rs_t_base_cooling']['rs_t_base_cooling_base_yr'],
        "units": '°C'}]

    # Future base year temperature
    assumptions['rs_t_base_cooling']['rs_t_base_cooling_future_yr'] = 21.0

    assumptions['ss_t_base_cooling']['param_infos'] = [{
        "name": "ss_t_base_cooling",
        "absolute_range": "(20, 25)",
        "description": "Base temperature assumption service sector cooling",
        "suggested_range": "(13, 17)",
        "default_value": assumptions['ss_t_base_cooling']['ss_t_base_cooling_base_yr'],
        "units": '°C'}]

    # Future base year temperature
    assumptions['ss_t_base_cooling']['ss_t_base_cooling_future_yr'] = 21.0

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 0.03 and 0.01 (DECC 2015)
    # ============================================================
    assumptions['smart_meter_assump']['param_infos'] = [
        {
            "name": "smart_meter_p_future",
            "absolute_range": "(0, 1)",
            "description": "Population diffusion of smart meters",
            "suggested_range": "(10, 100)",
            "default_value": '{}'.format(assumptions['smart_meter_assump']['smart_meter_p_by']),
            "units": '%'},
        {
            "name": "smart_meter_yr_until_changed",
            "absolute_range": "(0, 1)",
            "description": "Year until smart meter assumption is implemented",
            "suggested_range": "2015 - 2100",
            "default_value": '2050',
            "units": 'year'
        }
        ]

    # Fraction of population for future year
    assumptions['smart_meter_assump']['smart_meter_p_future'] = 0.1

    # Year until change is implemented
    assumptions['smart_meter_assump']['smart_meter_yr_until_changed'] = yr_until_changed_all_things

    # Long term smart meter induced general savings, purley as a result of having a smart meter
    assumptions['smart_meter_assump']['savings_smart_meter'] = {

        # Residential
        'rs_cold': -0.03,
        'rs_cooking': -0.03,
        'rs_lighting': -0.03,
        'rs_wet': -0.03,
        'rs_consumer_electronics': -0.03,
        'rs_home_computing': -0.03,
        'rs_space_heating': -0.03,

        # Service
        'ss_space_heating': -0.03,

        # Industry
        'is_space_heating': -0.03}

    # Helper function to create description of parameters for all enduses
    for enduse_name, _ in assumptions['smart_meter_assump']['savings_smart_meter'].items():
        assumptions['smart_meter_assump']['param_infos'].append({
            "name": "smart_meter_improvement_{}".format(enduse_name),
            "absolute_range": "(0, 100)",
            "description": "Smart meter induced savings for enduse {}".format(enduse_name),
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'})

    # ============================================================
    # Heat recycling & Reuse
    # ============================================================
    assumptions['heat_recovered'] = {}
    assumptions['heat_recovered']['param_infos'] = [
        {
            "name": "rs_space_heating",
            "absolute_range": "(0, 1)",
            "description": "Reduction in heat because of heat recovery and recycling (residential sector)",
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'
        },
        {
            "name": "ss_space_heating",
            "absolute_range": "(0, 1)",
            "description": "Reduction in heat because of heat recovery and recycling (service sector)",
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'
        },
        {
            "name": "is_space_heating",
            "absolute_range": "(0, 1)",
            "description": "Reduction in heat because of heat recovery and recycling (industry sector)",
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'
        },
        {
            "name": "heat_recovered_yr_until_changed",
            "absolute_range": "(2015, 2100)",
            "description": "Year until heat recyling is full implemented",
            "suggested_range": "(2015, 2100)",
            "default_value": '2050',
            "units": 'year'
        },
    ]

    # Heat recycling assumptions (e.g. 0.2 = 20% reduction)
    assumptions['heat_recovered']['rs_space_heating'] = 0.0
    assumptions['heat_recovered']['ss_space_heating'] = 0.0
    assumptions['heat_recovered']['is_space_heating'] = 0.0

    # Year until recycling is fully realised
    assumptions['heat_recovered']['heat_recovered_yr_until_changed'] = yr_until_changed_all_things

    # ---------------------------------------------------------
    # General change in fuel consumption for specific enduses
    # ---------------------------------------------------------
    #   With these assumptions, general efficiency gain (across all fueltypes)
    #   can be defined for specific enduses. This may be e.g. due to general
    #   efficiency gains or anticipated increases in demand.
    #   NTH: Specific hanges per fueltype (not across al fueltesp)
    #
    #   Change in fuel until the simulation end year (
    #   if no change set to 1, if e.g. 10% decrease change to 0.9)
    # -------------------------------------------------------
    assumptions['enduse_overall_change']['param_infos'] = [
        {
            "name": "enduse_specific_change_yr_until_changed",
            "absolute_range": "(0, 1)",
            "description": "Year until change in enduse assumption is implemented",
            "suggested_range": "(2015, 2100)",
            "default_value": '2050',
            "units": 'year'
        }
    ]

    # Year until fuel consumption is reduced
    assumptions['enduse_overall_change']['enduse_specific_change_yr_until_changed'] = yr_until_changed_all_things

    assumptions['enduse_overall_change']['enduses'] = {

        # Submodel Residential
        'rs_space_heating': 1,
        'rs_water_heating': 1,
        'rs_lighting': 1,
        'rs_cooking': 1,
        'rs_cold': 1,
        'rs_wet': 1,
        'rs_consumer_electronics': 1,
        'rs_home_computing': 1,

        # Submodel Service
        'ss_catering': 1,
        'ss_computing': 1,
        'ss_cooling_ventilation': 1,
        'ss_space_heating': 1,
        'ss_water_heating': 1,
        'ss_lighting': 1,
        'ss_other_gas': 1,
        'ss_other_electricity': 1,

        # Submodel Industry
        'is_high_temp_process': 1,
        'is_low_temp_process': 1,
        'is_drying_separation': 1,
        'is_motors': 1,
        'is_compressed_air': 1,
        'is_lighting': 1,
        'is_space_heating': 1,
        'is_other': 1,
        'is_refrigeration': 1}

    # Helper function to create description of parameters for all enduses
    for enduse_name, _ in assumptions['enduse_overall_change']['enduses'].items():
        assumptions['enduse_overall_change']['param_infos'].append({
            "name": "smart_meter_improvement_{}".format(enduse_name),
            "absolute_range": "(0, 100)",
            "description": "Enduse specific change {}".format(enduse_name),
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'})

    # ============================================================
    # Technologies & efficiencies
    # ============================================================

    # --Assumption how much of technological efficiency is reached
    assumptions['eff_achiev_f'] = {}
    assumptions['eff_achiev_f']['param_infos'] = [
        {
            "name": "eff_achiev_f",
            "absolute_range": "(0, 1)",
            "description": "Fraction achieved of efficiency improvements",
            "suggested_range": "(0, 100)",
            "default_value": '0',
            "units": '%'
        }]

    assumptions['eff_achiev_f']['factor_achieved'] = 1.0

    # -----------------------
    # Create parameter file only with fully descried parameters
    # and write to yaml file
    # -----------------------
    write_data.write_yaml_param_complete(paths['yaml_parameters_complete'], assumptions)

    assumptions['testing'] = True
    return
