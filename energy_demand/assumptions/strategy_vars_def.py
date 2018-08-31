"""Strategy variable assumptions provided as parameters to smif
"""
import copy
import logging
from energy_demand.read_write import write_data
from energy_demand.basic import basic_functions

def default_narrative(
        end_yr,
        value_by,
        value_ey,
        diffusion_choice='linear',
        sig_midpoint=0,
        sig_steepness=1,
        base_yr=2015,
        regional_specific=True
    ):
    """Create a default single narrative with a single timestep

    E.g. from value 0.2 in 2015 to value 0.5 in 2050

    Arguments
    ----------
    end_yr : int
        End year of narrative
    value_by : float
        Value of start year of narrative
    value_ey : float
        Value at end year of narrative
    diffusion_choice : str, default='linear'
        Wheter linear or sigmoid
    sig_midpoint : float, default=0
        Sigmoid midpoint
    sig_steepness : float, default=1
        Sigmoid steepness
    base_yr : int
        Base year
    regional_specific : bool
        If regional specific or not

    Returns
    -------
    container : list
        List with narrative
    """
    container = [
        {
            'base_yr': base_yr,
            'end_yr': end_yr,
            'value_by': value_by,
            'value_ey': value_ey,
            'diffusion_choice': diffusion_choice,
            'sig_midpoint': sig_midpoint,
            'sig_steepness': sig_steepness,
            'regional_specific': regional_specific}
        ]

    return container

def load_smif_parameters(
        data_handle,
        strategy_variable_names,
        assumptions=False,
        mode='smif'
    ):
    """Get all model parameters from smif (`parameters`) depending
    on narrative. Create the dict `strategy_vars` and
    add scenario value as well as affected enduses of
    each variable.

    Arguments
    ---------
    data_handle : dict
        Data handler
    strategy_variable_names : list
        All strategy variable names
    assumptions : obj
        Assumptions
    mode : str
        Criteria to define in which mode this function is run

    Returns
    -------
    strategy_variables : dict
        Updated strategy variables
    """
    # All information of all scenario parameters
    all_info_scenario_param = load_param_assump(
        assumptions=assumptions)

    strategy_vars = {}

    # Iterate variables and assign new values
    for name in strategy_variable_names:

        # Get scenario value
        if mode == 'smif':  #smif mode
            scenario_value = data_handle.get_parameter(name)
        else: #local running
            scenario_value = data_handle[name]['default_value']

        if scenario_value == 'True':
            scenario_value = True
        elif scenario_value == 'False':
            scenario_value = False
        else:
            pass

        logging.info(
            "... loading smif parameter: %s value: %s", name, scenario_value)

        # ------------------------------------------
        # Load or generate narratives per parameter
        # ------------------------------------------

        # TODO LOAD NARRATIVE FOR PARAMETER

        # -----------------
        # Load narratives infos
        # -----------------
        yr_until_changed_all_things = 2050 #TODO MAKE GLOBAL
        regional_specific = all_info_scenario_param[name]['regional_specific']      # Criteria whether the same for all regions or not
        default_by_value = all_info_scenario_param[name]['default_value']           # Base year value
        diffusion_type = all_info_scenario_param[name]['diffusion_type']            # Sigmoid or linear

        # ----------------------------------
        # Create narrative with only one story
        # ----------------------------------
        created_narrative = default_narrative(
            end_yr=yr_until_changed_all_things,
            value_by=default_by_value,
            value_ey=scenario_value,
            diffusion_choice=diffusion_type,
            base_yr=assumptions.base_yr,
            regional_specific=regional_specific)

        strategy_vars[name] = {

            'scenario_value': scenario_value,

            # Get affected enduses of this variable defined in `load_param_assump`
            'affected_enduse': all_info_scenario_param[name]['affected_enduse'],

            # Replace by external narrative telling
            'narratives': created_narrative}

    return strategy_vars

def load_param_assump(
        paths=None,
        local_paths=None,
        assumptions=None,
        writeYAML=False
    ):
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
    strategy_variables = []
    strategy_vars = {}

    # ------------------
    # Spatial explicit diffusion
    # ------------------
    strategy_vars['spatial_explicit_diffusion'] = assumptions.spatial_explicit_diffusion

    strategy_variables.append({
        "name": "spatial_explicit_diffusion",
        "absolute_range": (0, 1),
        "description": "Criteria to define spatial or non spatial diffusion",
        "suggested_range": (0, 1),
        "default_value": assumptions.spatial_explicit_diffusion,
        "units": 'years',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    strategy_vars['speed_con_max'] = assumptions.speed_con_max

    strategy_variables.append({
        "name": "speed_con_max",
        "absolute_range": (0, 99),
        "description": "Maximum speed of penetration (for spatial explicit diffusion)",
        "suggested_range": (0, 99),
        "default_value": assumptions.speed_con_max,
        "units": None,
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # -----------
    # Demand management of heat pumps
    # -----------
    strategy_vars['flat_heat_pump_profile_both'] = assumptions.flat_heat_pump_profile_both

    strategy_variables.append({
        "name": "flat_heat_pump_profile_both",
        "absolute_range": (0, 1),
        "description": "Heat pump profile flat or with actual data",
        "suggested_range": (0, 1),
        "default_value": assumptions.flat_heat_pump_profile_both,
        "units": 'bool',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    strategy_vars['flat_heat_pump_profile_only_water'] = assumptions.flat_heat_pump_profile_only_water

    strategy_variables.append({
        "name": "flat_heat_pump_profile_only_water",
        "absolute_range": (0, 1),
        "description": "Heat pump profile flat or with actual data only for water heating",
        "suggested_range": (0, 1),
        "default_value": assumptions.flat_heat_pump_profile_only_water,
        "units": 'bool',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # ----------------------
    # Heat pump technology mix
    # Source: Hannon 2015: Raising the temperature of the UK heat pump market: Learning lessons from Finland
    # ----------------------
    strategy_vars['gshp_fraction_ey'] = assumptions.gshp_fraction

    strategy_variables.append({
        "name": "gshp_fraction_ey",
        "absolute_range": (0, 1),
        "description": "Relative GSHP (%) to GSHP+ASHP",
        "suggested_range": (assumptions.gshp_fraction, 0.5),
        "default_value": assumptions.gshp_fraction,
        "units": 'decimal',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # ============================================================
    #  Demand management assumptions (daily demand shape)
    #  An improvement in load factor improvement can be assigned
    #  for every enduse (peak shaving)
    #
    #  Example: 0.2 --> Improvement in load factor until ey
    # ============================================================
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
            "units": 'decimal',
            'affected_enduse': [demand_name.split("__")[1]],
            'regional_specific': True,
            'diffusion_type': 'linear'})

        strategy_vars[demand_name] = scenario_value

    # =======================================
    # Climate Change assumptions
    # Temperature changes for every month for future year
    # =======================================
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
        strategy_variables.append({
            "name": "climate_change_temp_d__{}".format(month_str),
            "absolute_range": (-0, 10),
            "description": "Temperature change for month {}".format(month_str),
            "suggested_range": (-5, 5),
            "default_value": 0,
            "units": '°C',
            'regional_specific': False,
            'diffusion_type': 'linear'})

    # Helper function to move temps one level down
    for enduse_name, value_param in temps.items():
        strategy_vars[enduse_name] = value_param

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # The diffusion is asumed to be linear
    # ============================================================
    # Future base year temperature
    strategy_vars['rs_t_base_heating_future_yr'] = 15.5

    strategy_variables.append({
        "name": "rs_t_base_heating_future_yr",
        "absolute_range": (0, 20),
        "description": "Base temperature assumption residential heating",
        "suggested_range": (13, 17),
        "default_value": assumptions.t_bases.rs_t_heating_by,
        "units": '°C',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # Future base year temperature
    strategy_vars['ss_t_base_heating_future_yr'] = 15.5

    strategy_variables.append({
        "name": "ss_t_base_heating_future_yr",
        "absolute_range": (0, 20),
        "description": "Base temperature assumption service sector heating",
        "suggested_range": (13, 17),
        "default_value": assumptions.t_bases.ss_t_heating_by,
        "units": '°C',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # Future base year temperature
    strategy_vars['rs_t_base_cooling_future_yr'] = 5

    # Cooling base temperature
    # Future base year temperature
    strategy_vars['ss_t_base_cooling_future_yr'] = 5

    strategy_variables.append({
        "name": "ss_t_base_cooling_future_yr",
        "absolute_range": (0, 25),
        "description": "Base temperature assumption service sector cooling",
        "suggested_range": (13, 17),
        "default_value": assumptions.t_bases.ss_t_cooling_by,
        "units": '°C',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # Future base year temperature
    strategy_vars['is_t_base_heating_future_yr'] = 15.5

    # Parameters info
    strategy_variables.append({
        "name": "is_t_base_heating_future_yr",
        "absolute_range": (0, 20),
        "description": "Base temperature assumption service sector heating",
        "suggested_range": (13, 17),
        "default_value": assumptions.t_bases.is_t_heating_by,
        "units": '°C',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # ============================================================
    # Smart meter assumptions (Residential)
    #
    # DECC 2015: Smart Metering Early Learning Project: Synthesis report
    # https://www.gov.uk/government/publications/smart-metering-early-learning-project-and-small-scale-behaviour-trials
    # Reasonable assumption is between 0.03 and 0.01 (DECC 2015)
    # ============================================================
    # Narratives
    strategy_variables.append({
        "name": "smart_meter_improvement_p",
        "absolute_range": (0, 1),
        "description": "Improvement of smart meter penetration",
        "suggested_range": (0, 0.9),
        "default_value": assumptions.smart_meter_assump['smart_meter_p_by'],
        "units": 'decimal',
        'regional_specific': True,
        'diffusion_type': 'linear'})

    # Improvement of fraction of population for future year (base year = 0.1)
    strategy_vars['smart_meter_improvement_p'] = 0

    # ============================================================
    # Cooling
    # ============================================================
    strategy_variables.append({
        "name": "cooled_floorarea__ss_cooling_humidification",
        "absolute_range": (0, 1),
        "description": "Change in cooling of floor area (service sector)",
        "suggested_range": (-1, 1),
        "default_value": assumptions.cooled_ss_floorarea_by,
        "units": 'decimal',
        'regional_specific': True,
        'diffusion_type': 'linear'})

    # Change in cooling of floor area
    strategy_vars['cooled_floorarea__ss_cooling_humidification'] = 0

    # Penetration of cooling devices
    # COLING_OENETRATION ()
    # Or Assumkp Peneetration curve in relation to HDD from PAPER #Residential
    # Assumption on recovered heat (lower heat demand based on heat recovery)

    # ============================================================
    # Industrial processes
    # ============================================================
    strategy_variables.append({
        "name": "p_cold_rolling_steel",
        "absolute_range": (0, 1),
        "description": "Sectoral share of cold rolling in steel manufacturing)",
        "suggested_range": (0, 1),
        "default_value": assumptions.p_cold_rolling_steel_by,
        "units": 'decimal',
        'regional_specific': True,
        'diffusion_type': 'linear'})

    strategy_vars['p_cold_rolling_steel'] = assumptions.p_cold_rolling_steel_by

    # ============================================================
    # Heat recycling & reuse
    # ============================================================
    strategy_variables.append({
        "name": "heat_recoved__rs_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of heat recovery and recycling (residential sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        'affected_enduse': ['rs_space_heating'],
        'regional_specific': True,
        'diffusion_type': 'linear'})

    strategy_variables.append({
        "name": "heat_recoved__ss_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of heat recovery and recycling (service sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        'affected_enduse': ['ss_space_heating'],
        'regional_specific': True,
        'diffusion_type': 'linear'})

    strategy_variables.append({
        "name": "heat_recoved__is_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of heat recovery and recycling (industry sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        'affected_enduse': ['is_space_heating'],
        'regional_specific': True,
        'diffusion_type': 'linear'})

    # Heat recycling assumptions (e.g. 0.2 = 20% reduction)
    strategy_vars['heat_recoved__rs_space_heating'] = 0.0
    strategy_vars['heat_recoved__ss_space_heating'] = 0.0
    strategy_vars['heat_recoved__is_space_heating'] = 0.0

    # ============================================================
    # Air leakage
    # ============================================================
    strategy_variables.append({
        "name": "air_leakage__rs_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of air leakage improvement (residential sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        'affected_enduse': ['rs_space_heating'],
        'regional_specific': True,
        'diffusion_type': 'linear'})

    strategy_variables.append({
        "name": "air_leakage__ss_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of of air leakage improvementservice sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        'affected_enduse': ['ss_space_heating'],
        'regional_specific': True,
        'diffusion_type': 'linear'})

    strategy_variables.append({
        "name": "air_leakage__is_space_heating",
        "absolute_range": (0, 1),
        "description": "Reduction in heat because of air leakage improvement (industry sector)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        "affected_enduse": ['is_space_heating'],
        'regional_specific': True,
        'diffusion_type': 'linear'})

    # Heat recycling assumptions (e.g. 0.2 = 20% improvement and thus 20% reduction)
    strategy_vars['air_leakage__rs_space_heating'] = 0.0
    strategy_vars['air_leakage__ss_space_heating'] = 0.0
    strategy_vars['air_leakage__is_space_heating'] = 0.0

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
    enduse_overall_change_enduses = {

        # Submodel Residential
        'enduse_change__rs_space_heating': 0,
        'enduse_change__rs_water_heating': 0,
        'enduse_change__rs_lighting': 0,
        'enduse_change__rs_cooking': 0,
        'enduse_change__rs_cold': 0,
        'enduse_change__rs_wet': 0,
        'enduse_change__rs_consumer_electronics': 0,
        'enduse_change__rs_home_computing': 0,

        # Submodel Service (Table 5.5a)
        # same % improvements from baseline for all sectors
        'enduse_change__ss_space_heating': 0,
        'enduse_change__ss_water_heating': 0,
        'enduse_change__ss_cooling_humidification': 0,
        'enduse_change__ss_fans': 0,
        'enduse_change__ss_lighting': 0,
        'enduse_change__ss_catering': 0,
        'enduse_change__ss_small_power': 0,
        'enduse_change__ss_ICT_equipment': 0,
        'enduse_change__ss_cooled_storage': 0,
        'enduse_change__ss_other_gas': 0,
        'enduse_change__ss_other_electricity': 0,

        # Submodel Industry
        # same % improvements from baseline for all sectors
        'enduse_change__is_high_temp_process': 0,
        'enduse_change__is_low_temp_process': 0,
        'enduse_change__is_drying_separation': 0,
        'enduse_change__is_motors': 0,
        'enduse_change__is_compressed_air': 0,
        'enduse_change__is_lighting': 0,
        'enduse_change__is_space_heating': 0,
        'enduse_change__is_other': 0,
        'enduse_change__is_refrigeration': 0}

    # Helper function to create description of parameters for all enduses
    for enduse_name, param_value in enduse_overall_change_enduses.items():
        strategy_variables.append({
            "name": enduse_name,
            "absolute_range": (-1, 1),
            "description": "Enduse specific change {}".format(enduse_name),
            "suggested_range": (0, 1),
            "default_value": 0,
            "units": 'decimal',
            'affected_enduse': [enduse_name.split("__")[1]],
            'regional_specific': True,
            'diffusion_type': 'linear'})

        strategy_vars[enduse_name] = param_value

    # ============================================================
    # Technologies & efficiencies
    # ============================================================

    # --Assumption how much of technological efficiency is reached
    strategy_variables.append({
        "name": "f_eff_achieved",
        "absolute_range": (0, 1),
        "description": "Fraction achieved of efficiency improvements",
        "suggested_range": (0, 1),
        "default_value": 0, # Default is no efficiency improvement
        "units": 'decimal',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    strategy_vars["f_eff_achieved"] = 0

    # ---------------------------------------
    # Floor area per person change
    # ---------------------------------------
    strategy_variables.append({
        "name": "assump_diff_floorarea_pp",
        "absolute_range": (-1, 1),
        "description": "Change in floor area per person (%, 1=100%)",
        "suggested_range": (0, 1),
        "default_value": 0,
        "units": 'decimal',
        'regional_specific': False,
        'diffusion_type': 'linear'})

    # -----------------------
    # Create parameter file only with fully descried parameters
    # and write to yaml file
    # -----------------------
    if not paths:
        pass
    else:
        strategy_variables_write = copy.copy(strategy_variables)

        # Delete affected_enduse
        for var in strategy_variables_write:
            try:
                del var['affected_enduse']
            except KeyError:
                pass

        if writeYAML:
            # Delete existing files
            basic_functions.del_file(local_paths['yaml_parameters_constrained'])
            basic_functions.del_file(local_paths['yaml_parameters_scenario'])

            # Write new files
            write_data.write_yaml_param_complete(
                local_paths['yaml_parameters_constrained'],
                strategy_variables_write)
            write_data.write_yaml_param_scenario(
                local_paths['yaml_parameters_scenario'],
                strategy_vars)

            raise Exception("The smif parameters are read and written to {}".format(local_paths['yaml_parameters_scenario']))

    # Convert to dict for loacl running purposes
    strategy_vars_out = {}
    for var in strategy_variables:

        var_name = var['name']
        strategy_vars_out[var_name] = var

        if var['default_value'] == 'True' or var['default_value'] is True:
            scenario_value = True
        elif var['default_value'] == 'False' or var['default_value'] is False:
            scenario_value = False
        elif var['default_value'] == 'None' or var['default_value'] is None:
            scenario_value = None
        else:
            scenario_value = float(var['default_value'])

        strategy_vars_out[var_name]['scenario_value'] = scenario_value

        # If no 'affected_enduse' defined, add empty list of affected enduses
        affected_enduse = get_affected_enduse(strategy_variables, var_name)
        strategy_vars_out[var['name']]['affected_enduse'] = affected_enduse

    return dict(strategy_vars_out)

def get_affected_enduse(strategy_variables, name):
    """Get all defined affected enduses of a scenario variable

    Arguments
    ---------
    strategy_variables : dict
        Dict with all defined strategy variables
    name : str
        Name of variable to get

    Returns
    -------
    enduses : list
        AFfected enduses of scenario variable
    """
    try:
        for var in strategy_variables:
            if var['name'] == name:
                enduses = var['affected_enduse']

                return enduses
    except KeyError:
        # Not affected enduses defined
        enduses = []

        return enduses
