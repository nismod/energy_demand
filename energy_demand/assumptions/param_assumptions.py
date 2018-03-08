"""
-------------------------------------------
Assumptions provided as parameters to smif
-------------------------------------------
This script can be run to write out all paramters as YAML
file. This file is not executed when running the ed model
from within smif.
"""
import logging
from energy_demand.read_write import write_data
from energy_demand.basic import basic_functions

def load_param_assump(paths, assumptions):
    """All assumptions of the energy demand model
    are loaded and added to the data dictionary

    Arguments
    ---------
    paths : dict
        Paths
    assumptions : dict
        Assumptions

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict
    """
    logging.debug("... write assumptions to yaml file")

    strategy_variables = []
    strategy_vars = {}

    yr_until_changed_all_things = 2050 #TODO

    # ----------------------
    # Heat pump GASHP & ASHP fraction assumptions
    # Relative GSHP (%) to GSHP+ASHP
    # ----------------------
    strategy_vars['split_hp_gshp_to_ashp_ey'] = 0.5

    strategy_variables.append({
        "name": "split_hp_gshp_to_ashp_ey",
        "absolute_range": (0, 1),
        "description": "Relative GSHP (%) to GSHP+ASHP",
        "suggested_range": (assumptions['split_hp_gshp_to_ashp_by'], 0.5),
        "default_value": assumptions['split_hp_gshp_to_ashp_by'],
        "units": '%'})

    # ============================================================
    #  Demand management assumptions (daily demand shape)
    #  An improvement in load factor improvement can be assigned
    #  for every enduse (peak shaving)
    #
    #  Example: 0.2 --> Improvement in load factor until ey
    # ============================================================

    # Year until ld if implemented
    strategy_vars['demand_management_yr_until_changed'] = yr_until_changed_all_things

    strategy_variables.append({
        "name": "demand_management_yr_until_changed",
        "absolute_range": (0, 20),
        "description": "Year until demand management assumptions are fully realised",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'years'})

    enduses_demand_managent = {

        #Residential submodule
        'demand_management_improvement__rs_space_heating': 0,
        'demand_management_improvement__rs_water_heating': 0,
        'demand_management_improvement__rs_lighting': 0,
        'demand_management_improvement__rs_cooking': 0,
        'demand_management_improvement__rs_cold': 0,
        'demand_management_improvement__rs_wet': 0,
        'demand_management_improvement__rs_consumer_electronics': 0,
        'demand_management_improvement__rs_home_computing': 0,

        # Submodel Service (Table 5.5a)
        'demand_management_improvement__ss_space_heating': 0,
        'demand_management_improvement__ss_water_heating': 0,
        'demand_management_improvement__ss_cooling_humidification': 0,
        'demand_management_improvement__ss_fans': 0,
        'demand_management_improvement__ss_lighting': 0,
        'demand_management_improvement__ss_catering': 0,
        'demand_management_improvement__ss_small_power': 0,
        'demand_management_improvement__ss_ICT_equipment': 0,
        'demand_management_improvement__ss_cooled_storage': 0,
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
    for demand_name, scenario_value in enduses_demand_managent.items():
        strategy_variables.append({
            "name": demand_name,
            "absolute_range": (0, 1),
            "description": "reduction in load factor for enduse {}".format(demand_name),
            "suggested_range": (0, 1),
            "default_value": 0,
            "units": '%'})

        strategy_vars[demand_name] = scenario_value

    # =======================================
    # Climate Change assumptions
    # Temperature changes for every month for future year
    # =======================================
    strategy_vars['climate_change_temp_diff_yr_until_changed'] = yr_until_changed_all_things

    strategy_variables.append(
        {
            "name": "climate_change_temp_diff_yr_until_changed",
            "absolute_range": (2015, 2100),
            "description": "Year until climate temperature changes are fully realised",
            "suggested_range": (2030, 2100),
            "default_value": 2050,
            "units": 'year'
        })

    temps = {
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

    for month_python, _ in enumerate(temps):
        month_str = basic_functions.get_month_from_int(month_python + 1)
        strategy_variables.append(
            {
                "name": "climate_change_temp_d__{}".format(month_str),
                "absolute_range": (-0, 10),
                "description": "Temperature change for month {}".format(month_str),
                "suggested_range": (-5, 5),
                "default_value": 0,
                "units": '°C'
            })

    # Helper function to move temps one level down
    for enduse_name, value_param in temps.items():
        strategy_vars[enduse_name] = value_param

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # The diffusion is asumed to be linear
    # ============================================================
    # Parameters info
    strategy_variables.append({
        "name": "rs_t_base_heating_future_yr",
        "absolute_range": (0, 20),
        "description": "Base temperature assumption residential heating",
        "suggested_range": (13, 17),
        "default_value": assumptions['t_bases']['rs_t_heating_by'],
        "units": '°C'})

    # Future base year temperature
    strategy_vars['rs_t_base_heating_future_yr'] = 15.5

    # Parameters info
    strategy_variables.append({
        "name": "ss_t_base_heating_future_yr",
        "absolute_range": (0, 20),
        "description": "Base temperature assumption service sector heating",
        "suggested_range": (13, 17),
        "default_value": assumptions['t_bases']['ss_t_heating_by'],
        "units": '°C'})

        # Future base year temperature
    strategy_vars['ss_t_base_heating_future_yr'] = 15.5

    # Cooling base temperature
    '''strategy_variables.append({
        "name": "rs_t_base_cooling_future_yr",
        "absolute_range": (0, 25),
        "description": "Base temperature assumption residential sector cooling",
        "suggested_range": (13, 17),
        "default_value": assumptions['t_bases']['rs_t_cooling_by'],
        "units": '°C'})'''

    # Future base year temperature
    strategy_vars['rs_t_base_cooling_future_yr'] = 5

    strategy_variables.append({
        "name": "ss_t_base_cooling_future_yr",
        "absolute_range": (0, 25),
        "description": "Base temperature assumption service sector cooling",
        "suggested_range": (13, 17),
        "default_value": assumptions['t_bases']['ss_t_cooling_by'],
        "units": '°C'})

    # Future base year temperature
    strategy_vars['ss_t_base_cooling_future_yr'] = 5

    # Parameters info
    strategy_variables.append({
        "name": "is_t_base_heating_future_yr",
        "absolute_range": (0, 20),
        "description": "Base temperature assumption service sector heating",
        "suggested_range": (13, 17),
        "default_value": assumptions['t_bases']['is_t_heating_by'],
        "units": '°C'})

        # Future base year temperature
    strategy_vars['is_t_base_heating_future_yr'] = 15.5

    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 0.03 and 0.01 (DECC 2015)
    # ============================================================
    strategy_variables.append({
        "name": "smart_meter_p_future",
        "absolute_range": (0, 1),
        "description": "Population diffusion of smart meters",
        "suggested_range": (10, 100),
        "default_value": '{}'.format(assumptions['smart_meter_assump']['smart_meter_p_by']),
        "units": '%'})

    strategy_variables.append({
        "name": "smart_meter_yr_until_changed",
        "absolute_range": (0, 1),
        "description": "Year until smart meter assumption is implemented",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'year'})

    # Fraction of population for future year
    strategy_vars['smart_meter_p_future'] = 0.1

    # Year until change is implemented
    strategy_vars['smart_meter_yr_until_changed'] = yr_until_changed_all_things

    # Long term smart meter induced general savings, purley as
    # a result of having a smart meter (e.g. 0.03 --> 3% savings)
    savings_smart_meter = {

        # Residential
        'smart_meter_improvement_rs_cold': 0.03,
        'smart_meter_improvement_rs_cooking': 0.03,
        'smart_meter_improvement_rs_lighting': 0.03,
        'smart_meter_improvement_rs_wet': 0.03,
        'smart_meter_improvement_rs_consumer_electronics': 0.03,
        'smart_meter_improvement_rs_home_computing': 0.03,
        'smart_meter_improvement_rs_space_heating': 0.03,

        # Service
        'smart_meter_improvement_ss_space_heating': 0.03,
        'smart_meter_improvement_ss_water_heating': 0,
        'smart_meter_improvement_ss_cooling_humidification': 0,
        'smart_meter_improvement_ss_fans': 0,
        'smart_meter_improvement_ss_lighting': 0,
        'smart_meter_improvement_ss_catering': 0,
        'smart_meter_improvement_ss_small_power': 0,
        'smart_meter_improvement_ss_ICT_equipment': 0,
        'smart_meter_improvement_ss_cooled_storage': 0,
        'smart_meter_improvement_ss_other_gas': 0,
        'smart_meter_improvement_ss_other_electricity': 0,

        # Industry submodule
        'smart_meter_improvement_is_high_temp_process': 0,
        'smart_meter_improvement_is_low_temp_process': 0,
        'smart_meter_improvement_is_drying_separation': 0,
        'smart_meter_improvement_is_motors': 0,
        'smart_meter_improvement_is_compressed_air': 0,
        'smart_meter_improvement_is_lighting': 0,
        'smart_meter_improvement_is_space_heating': 0.03,
        'smart_meter_improvement_is_other': 0,
        'smart_meter_improvement_is_refrigeration': 0}

    # Helper function to create description of parameters for all enduses
    for enduse_name, param_value in savings_smart_meter.items():
        strategy_variables.append({
            "name": enduse_name,
            "absolute_range": (0, 1),
            "description": "Smart meter induced savings for enduse {}".format(enduse_name),
            "suggested_range": (0, 1),
            "default_value": '0',
            "units": '%'})

        strategy_vars[enduse_name] = param_value

    # ============================================================
    # Cooling
    # ============================================================
    strategy_variables.append({
        "name": "cooled_floorarea__ss_cooling_humidification",
        "absolute_range": (0, 1),
        "description": "Percentage of floorarea which is cooled (service sector)",
        "suggested_range": (0, 1),
        "default_value": assumptions['cooled_ss_floorarea_by'],
        "units": '%'})

    # How much of the floorarea is cooled in end year (example: 0.5 --> 50% of floorarea is cooled)
    # Carbon Trust. (2012). Air conditioning. Maximising comfort, minimising energy consumption.
    strategy_vars['cooled_floorarea__ss_cooling_humidification'] = 0.35

    strategy_variables.append({
        "name": "cooled_floorarea_yr_until_changed",
        "absolute_range": (0, 1),
        "description": "Year until floor area is fully changed",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'year'})

    # Year until floor area change is fully realised
    strategy_vars['cooled_floorarea_yr_until_changed'] = yr_until_changed_all_things

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Industrial processes
    # ============================================================
    strategy_vars['hot_cold_rolling_yr_until_changed'] = yr_until_changed_all_things

    strategy_variables.append({
        "name": "hot_cold_rolling_yr_until_changed",
        "absolute_range": (0, 1),
        "description": "Year until cold rolling steel manufacturing change is fully realised",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'year'})

    strategy_variables.append({
        "name": "p_cold_rolling_steel",
        "absolute_range": (0, 1),
        "description": "Share of cold rolling given in percent)",
        "suggested_range": (0, 1),
        "default_value": assumptions['p_cold_rolling_steel_by'],
        "units": '%'})

    strategy_vars['p_cold_rolling_steel'] = assumptions['p_cold_rolling_steel_by']

    # ============================================================
    # Heat recycling & reuse
    # ============================================================
    strategy_variables.append({
        "name": "heat_recoved__rs_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of heat recovery and recycling (residential sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": '%'})

    strategy_variables.append({
        "name": "heat_recoved__ss_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of heat recovery and recycling (service sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": '%'})

    strategy_variables.append({
        "name": "heat_recoved__is_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of heat recovery and recycling (industry sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": '%'})

    strategy_variables.append({
        "name": "heat_recovered_yr_until_changed",
        "absolute_range": (2015, 2100),
        "description": "Year until heat recyling is full implemented",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'year'})

    # Heat recycling assumptions (e.g. 0.2 = 20% reduction)
    strategy_vars['heat_recoved__rs_space_heating'] = 0.0
    strategy_vars['heat_recoved__ss_space_heating'] = 0.0
    strategy_vars['heat_recoved__is_space_heating'] = 0.0

    # Year until recycling is fully realised
    strategy_vars['heat_recovered_yr_until_changed'] = yr_until_changed_all_things

    # ============================================================
    # Air leakage
    # ============================================================
    strategy_variables.append({
        "name": "air_leakage__rs_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of air leakage improvement (residential sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": '%'})

    strategy_variables.append({
        "name": "air_leakage__ss_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of of air leakage improvementservice sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": '%'})

    strategy_variables.append({
        "name": "air_leakage__is_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of air leakage improvement (industry sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": '%'})

    strategy_variables.append({
        "name": "air_leakage_yr_until_changed",
        "absolute_range": (2015, 2100),
        "description": "Year until heat air leakage improvement is full implemented",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'year'})

    # Heat recycling assumptions (e.g. 0.2 = 20% improvement and thus 20% reduction)
    strategy_vars['air_leakage__rs_space_heating'] = 0.0
    strategy_vars['air_leakage__ss_space_heating'] = 0.0 #TODO: ADD
    strategy_vars['air_leakage__is_space_heating'] = 0.0 #TODO: ADD

    # Year until recycling is fully realised
    strategy_vars['air_leakage_yr_until_changed'] = yr_until_changed_all_things

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
    strategy_variables.append({
        "name": "enduse_specific_change_yr_until_changed",
        "absolute_range": (0, 1),
        "description": "Year until change in enduse assumption is implemented",
        "suggested_range": (2015, 2100),
        "default_value": 2050,
        "units": 'year'})

    # Year until fuel consumption is reduced
    strategy_vars['enduse_specific_change_yr_until_changed'] = yr_until_changed_all_things

    enduse_overall_change_enduses = {

        # Submodel Residential
        'enduse_change__rs_space_heating': 1,
        'enduse_change__rs_water_heating': 1,
        'enduse_change__rs_lighting': 1,
        'enduse_change__rs_cooking': 1,
        'enduse_change__rs_cold': 1,
        'enduse_change__rs_wet': 1,
        'enduse_change__rs_consumer_electronics': 1,
        'enduse_change__rs_home_computing': 1,

        # Submodel Service (Table 5.5a)
        # same % improvements from baseline for all sectors
        'enduse_change__ss_space_heating': 1,
        'enduse_change__ss_water_heating': 1,
        'enduse_change__ss_cooling_humidification': 1,
        'enduse_change__ss_fans': 1,
        'enduse_change__ss_lighting': 1,
        'enduse_change__ss_catering': 1,
        'enduse_change__ss_small_power': 1,
        'enduse_change__ss_ICT_equipment': 1,
        'enduse_change__ss_cooled_storage': 1,
        'enduse_change__ss_other_gas': 1,
        'enduse_change__ss_other_electricity': 1,

        # Submodel Industry
        # same % improvements from baseline for all sectors
        'enduse_change__is_high_temp_process': 1,
        'enduse_change__is_low_temp_process': 1,
        'enduse_change__is_drying_separation': 1,
        'enduse_change__is_motors': 1,
        'enduse_change__is_compressed_air': 1,
        'enduse_change__is_lighting': 1,
        'enduse_change__is_space_heating': 1,
        'enduse_change__is_other': 1,
        'enduse_change__is_refrigeration': 1}

    # Helper function to create description of parameters for all enduses
    for enduse_name, param_value in enduse_overall_change_enduses.items():
        strategy_variables.append({
            "name": enduse_name,
            "absolute_range": (0, 1),
            "description": "Enduse specific change {}".format(enduse_name),
            "suggested_range": (0, 1),
            "default_value": 1,
            "units": '%'})
        strategy_vars[enduse_name] = param_value

    # ============================================================
    # Technologies & efficiencies
    # ============================================================

    # --Assumption how much of technological efficiency is reached
    strategy_variables.append({
        "name": "eff_achiev_f",
        "absolute_range": (0, 1),
        "description": "Fraction achieved of efficiency improvements",
        "suggested_range": (0, 1),
        "default_value": 1.0,
        "units": '%'})

    strategy_vars["eff_achiev_f"] = 1.0

    # -----------------------
    # Create parameter file only with fully descried parameters
    # and write to yaml file
    # -----------------------
    basic_functions.del_file(paths['yaml_parameters_constrained'])

    write_data.write_yaml_param_complete(
        paths['yaml_parameters_constrained'],
        strategy_variables)

    basic_functions.del_file(paths['yaml_parameters_scenario'])
    write_data.write_yaml_param_scenario(
        paths['yaml_parameters_scenario'],
        strategy_vars)

    # Replace strategy variables
    assumptions['strategy_variables'] = strategy_vars

    return
