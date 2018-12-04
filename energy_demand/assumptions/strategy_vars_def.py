"""Strategy variable assumptions provided as parameters to smif
"""
from collections import defaultdict

from energy_demand.read_write import narrative_related

def generate_default_parameter_narratives(
        default_streategy_vars,
        end_yr=2050,
        base_yr=2015):
    """Load default parameters and create default timesteps

    Arguments
    ---------
    default_streategy_vars : dict
        Default parameter values
    end_yr : int
        Simulation end year
    base_yr : int
        Base year

    Returns
    -------

    """
    strategy_vars = defaultdict(dict)
    # ------------------------------------------------------------
    # Create default narrative for every simulation parameter
    # ------------------------------------------------------------
    for var_name, var_entries in default_streategy_vars.items():
        crit_single_dim = narrative_related.crit_dim_var(var_entries)

        if crit_single_dim:

            scenario_value = var_entries['default_value']

            # Create default narrative with only one timestep from simulation base year to simulation end year
            strategy_vars[var_name] = narrative_related.default_narrative(
                end_yr=end_yr,
                value_by=var_entries['default_value'],                # Base year value,
                value_ey=scenario_value,
                diffusion_choice=var_entries['diffusion_type'],       # Sigmoid or linear,
                base_yr=base_yr,
                regional_specific=var_entries['regional_specific'])   # Criteria whether the same for all regions or not

        else:
            # Standard narrative for multidimensional narrative
            for sub_var_name, sub_var_entries in var_entries.items():

                scenario_value = sub_var_entries['scenario_value']

                # -----------------------------------
                # Crate single-step default narratives (up to end_year)
                # -----------------------------------
                strategy_vars[var_name][sub_var_name] = narrative_related.default_narrative(
                    end_yr=end_yr,
                    value_by=sub_var_entries['default_value'],
                    value_ey=scenario_value,
                    diffusion_choice=sub_var_entries['diffusion_type'],
                    base_yr=base_yr,
                    regional_specific=sub_var_entries['regional_specific'])

    strategy_vars = dict(strategy_vars)

    return strategy_vars

def load_param_assump(
        default_values=None,
        hard_coded_default_val=True
    ):
    """All assumptions of the energy demand model
    are loaded and added to the data dictionary

    Arguments
    ---------

    Returns
    -------
    data : dict
        Data dictionary with added ssumption dict
    """
    strategy_vars = defaultdict(dict)

    if hard_coded_default_val:
        default_values = {
            'ss_t_cooling': 5,
            'is_t_heating': 15.5,
            'gshp_fraction': 0.1,
            'p_cold_rolling_steel_by': 0.2,
            'rs_t_heating': 15.5,
            'smart_meter_p_by': 0.05,
            'cooled_ss_floorarea_by': 0.35,
            'speed_con_max': 1,
            'spatial_explicit_diffusion': 0,
            'ss_t_heating': 15.5}

    default_enduses = {

        # Submodel Residential
        'rs_space_heating': 0,
        'rs_water_heating': 0,
        'rs_lighting': 0,
        'rs_cooking': 0,
        'rs_cold': 0,
        'rs_wet': 0,
        'rs_consumer_electronics': 0,
        'rs_home_computing': 0,

        # Submodel Service (Table 5.5a)
        # same % improvements from baseline over all sectors
        'ss_space_heating': 0,
        'ss_water_heating': 0,
        'ss_cooling_humidification': 0,
        'ss_fans': 0,
        'ss_lighting': 0,
        'ss_catering': 0,
        'ss_small_power': 0,
        'ss_ICT_equipment': 0,
        'ss_cooled_storage': 0,
        'ss_other_gas': 0,
        'ss_other_electricity': 0,

        # Submodel Industry
        # same % improvements from baseline over all sectors
        'is_high_temp_process': 0,
        'is_low_temp_process': 0,
        'is_drying_separation': 0,
        'is_motors': 0,
        'is_compressed_air': 0,
        'is_lighting': 0,
        'is_space_heating': 0,
        'is_other': 0,
        'is_refrigeration': 0}

    # ------------------
    # Spatial explicit diffusion
    # ------------------
    strategy_vars['spatial_explicit_diffusion'] = {
        "name": "spatial_explicit_diffusion",
        "description": "Criteria to define spatial or non spatial diffusion",
        "default_value": default_values['spatial_explicit_diffusion'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    strategy_vars['speed_con_max'] = {
        "name": "speed_con_max",
        "description": "Maximum speed of penetration (for spatial explicit diffusion)",
        "default_value": default_values['speed_con_max'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # ----------------------
    # Heat pump technology mix
    # Source: Hannon 2015: Raising the temperature of the UK heat pump market: Learning lessons from Finland
    # ----------------------
    strategy_vars['gshp_fraction'] = {
        "name": "gshp_fraction",
        "description": "Relative GSHP (%) to GSHP+ASHP",
        "default_value": default_values['gshp_fraction'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # ============================================================
    #  Demand management assumptions (daily demand shape)
    #  An improvement in load factor improvement can be assigned
    #  for every enduse (peak shaving)
    #
    #  Example: 0.2 --> Improvement in load factor until ey
    # ============================================================

    # Helper function to create description of parameters for all enduses
    for demand_name, scenario_value in default_enduses.items():
        strategy_vars['dm_improvement'][demand_name] = {
            "name": demand_name,

            "description": "reduction in load factor for enduse {}".format(demand_name),
            "default_value": scenario_value,
            "sector": True,
            "enduse": [demand_name],
            'regional_specific': True,
            'diffusion_type': 'linear'}

    # ============================================================
    # Base temperature assumptions for heating and cooling demand
    # The diffusion is asumed to be linear
    # ============================================================
    strategy_vars['rs_t_base_heating'] = {
        "name": "rs_t_base_heating",
        "description": "Base temperature assumption residential heating",
        "default_value": default_values['rs_t_heating'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # Future base year temperature
    strategy_vars['ss_t_base_heating'] = {
        "name": "ss_t_base_heating",
        "description": "Base temperature assumption service sector heating",
        "default_value": default_values['ss_t_heating'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # Cooling base temperature
    # Future base year temperature
    strategy_vars['ss_t_base_cooling'] = {
        "name": "ss_t_base_cooling",
        "description": "Base temperature assumption service sector cooling",
        "default_value": default_values['ss_t_cooling'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # Future base year temperature
    strategy_vars['is_t_base_heating'] = {
        "name": "is_t_base_heating",
        "description": "Base temperature assumption service sector heating",
        "default_value": default_values['is_t_heating'],
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # ============================================================
    # Smart meter penetration
    # ============================================================
    strategy_vars['smart_meter_p'] = {
        "name": "smart_meter_p",
        "description": "Improvement of smart meter penetration",
        "default_value": default_values['smart_meter_p_by'],
        "sector": True,
        'regional_specific': True,
        'diffusion_type': 'linear'}

    # ============================================================
    # Cooling
    # ============================================================
    cooled_floorarea = {
        'ss_cooling_humidification': default_values['cooled_ss_floorarea_by'],
        'ss_fans': default_values['cooled_ss_floorarea_by']}

    for sub_param_name, sub_param_value in cooled_floorarea.items():
        strategy_vars['cooled_floorarea'][sub_param_name] = {
            "name": sub_param_name,

            "description": "Change in cooling of floor area (service sector)",
            "default_value": sub_param_value,
            "sector": True,
            'regional_specific': True,
            'diffusion_type': 'linear'}

    # ============================================================
    # Industrial processes
    # ============================================================
    strategy_vars['p_cold_rolling_steel'] = {
        "name": "p_cold_rolling_steel",
        "description": "Sectoral share of cold rolling in steel manufacturing)",
        "default_value": default_values['p_cold_rolling_steel_by'],
        "sector": True,
        'regional_specific': True,
        'diffusion_type': 'linear'}

    # ============================================================
    # Heat recycling & reuse
    # ============================================================
    heat_recovered = {
        'rs_space_heating': 0,
        'ss_space_heating': 0,
        'is_space_heating': 0,
        'rs_water_heating': 0,
        'ss_water_heating': 0}

    for sub_param_name, sub_param_value in heat_recovered.items():
        strategy_vars['heat_recovered'][sub_param_name] = {
            "name": sub_param_name,

            "description": "Reduction in heat because of heat recovery and recycling",
            "default_value": sub_param_value,
            "sector": True,
            "enduse": [sub_param_name],
            'regional_specific': True,
            'diffusion_type': 'linear'}

    # ============================================================
    # Air leakage
    # ============================================================
    air_leakage = {
        'rs_space_heating': 0,
        'ss_space_heating': 0,
        'is_space_heating': 0}

    for sub_param_name, sub_param_value in air_leakage.items():
        strategy_vars['air_leakage'][sub_param_name] = {
            "name": sub_param_name,

            "description": "Reduction in heat because of air leakage improvement (residential sector)",
            "default_value": sub_param_value,
            "sector": True,
            "enduse": [sub_param_name],
            'regional_specific': True,
            'diffusion_type': 'linear'}

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

    # Helper function to create description of parameters for all enduses
    for enduse, param_value in default_enduses.items():
        strategy_vars['generic_enduse_change'][enduse] = {
            "name": enduse,
            "description": "Enduse specific change {}".format(enduse),
            "default_value": param_value,
            "sector": True,
            "enduse": [enduse],
            "sector": [],
            'regional_specific': True,
            'diffusion_type': 'linear'}

    # ============================================================
    # Technologies & efficiencies
    # ============================================================

    # --Assumption how much of technological efficiency is reached
    strategy_vars["f_eff_achieved"] = {
        "name": "f_eff_achieved",
        "description": "Fraction achieved of efficiency improvements",
        "default_value": 0, # Default is no efficiency improvement
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # --------------------------------------
    # Floor area per person change
    # ---------------------------------------
    strategy_vars["assump_diff_floorarea_pp"] = {
        "name": "assump_diff_floorarea_pp",
        "description": "Change in floor area per person (%, 1=100%)",
        "default_value": 0,
        "sector": True,
        'regional_specific': False,
        'diffusion_type': 'linear'}

    # -----------------------
    # Generic enduse and sector specific fuel switches
    # -----------------------
    for enduse, param_value in default_enduses.items():
        strategy_vars["generic_fuel_switch"][enduse] = {
            "name": "generic_fuel_switch",
            "description": "Generic fuel switches to switch fuel in any enduse and sector",
            "default_value": param_value,
            "enduse": enduse,
            "sector": True,
            'regional_specific': True,
            'diffusion_type': 'linear'}

    strategy_vars_out = autocomplete_strategy_vars(strategy_vars)

    return dict(strategy_vars_out)

def autocomplete_strategy_vars(
        strategy_vars,
        narrative_crit=False
    ):
    """Autocomplete all narratives or strategy variables with
    and 'enduse' or 'sector' in case they are not defined.

    Arguments
    ----------
    strategy_vars

    Returns
    -------
    narrative_crit : bool
        Criteria wheter inputs are a narrative or not
    """
    if not narrative_crit:
        out_dict = defaultdict(dict)

        for var_name, var_entries in strategy_vars.items():
            crit_single_dim = narrative_related.crit_dim_var(var_entries)

            if crit_single_dim:
                out_dict[var_name] = var_entries

                # If no 'enduse' defined, add empty list of affected enduses
                out_dict[var_name]['scenario_value'] = var_entries['default_value']

                if 'enduse' not in var_entries:
                    out_dict[var_name]['enduse'] = []
                if 'sector' not in var_entries:
                    out_dict[var_name]['sector'] = True  # All sector
            else:
                for sub_var_name, sub_var_entries in var_entries.items():
                    out_dict[var_name][sub_var_name] = sub_var_entries

                    out_dict[var_name][sub_var_name]['scenario_value'] = sub_var_entries['default_value']

                    # If no 'enduse' defined, add empty list of affected enduses
                    if 'enduse' not in sub_var_entries:
                        out_dict[var_name][sub_var_name]['enduse'] = []
                    if 'sector' not in sub_var_entries:
                        out_dict[var_name][sub_var_name]['sector'] = True # All sector
    else:
        # Same but narratives which need to be iterated
        out_dict = {}

        for var_name, var_entries in strategy_vars.items():
            out_dict[var_name] = {}

            crit_single_dim = narrative_related.crit_dim_var(var_entries)

            if crit_single_dim:
                updated_narratives = []

                for narrative in var_entries:
                    #If no 'enduse' defined, add empty list of affected enduses
                    if 'enduse' not in narrative:
                        narrative['enduse'] = []
                    if 'sector' not in narrative:
                        narrative['sector'] = 'dummy_sector' # All sector
                    updated_narratives.append(narrative)

                out_dict[var_name] = updated_narratives
            else:
                #print("   ...user defined variable: %s", var_name)
                for sub_var_name, sector_sub_var_entries in var_entries.items():

                    if type(sector_sub_var_entries) is dict: # If sectors are defined
                        for sector, sub_var_entries in sector_sub_var_entries.items():
                            out_dict[var_name][sub_var_name] = {}

                            updated_narratives = []
                            for narrative in sub_var_entries:

                                # If no 'enduse' defined, add empty list of affected enduses
                                if 'enduse' not in narrative:
                                    narrative['enduse'] = []
                                if 'sector' not in narrative:
                                    narrative['sector'] = sector
                                updated_narratives.append(narrative)

                            out_dict[var_name][sub_var_name][sector] = updated_narratives

                    else: # no sectors defined
                        updated_narratives = []
                        for narrative in sector_sub_var_entries:

                            if 'enduse' not in narrative:
                                narrative['enduse'] = [sub_var_name]
                            updated_narratives.append(narrative)

                        out_dict[var_name][sub_var_name] = updated_narratives

    return dict(out_dict)

def get_affected_enduse(strategy_vars, name):
    """Get all defined affected enduses of a scenario variable

    Arguments
    ---------
    strategy_vars : dict
        Dict with all defined strategy variables
    name : str
        Name of variable to get

    Returns
    -------
    enduses : list
        AFfected enduses of scenario variable
    """
    try:
        for var in strategy_vars:
            if var['name'] == name:
                enduses = var['enduse']

                return enduses
    except KeyError: # Not affected enduses defined
        enduses = []

        return enduses
