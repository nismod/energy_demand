"""Generate scenario paramters for every year
"""
import os
from collections import defaultdict

from energy_demand.technologies import diffusion_technologies
from energy_demand import enduse_func
from energy_demand.read_write import narrative_related

def get_correct_narrative_timestep(
        sim_yr,
        narrative_timesteps
    ):
    """Based on simulated year select the correct
    narrative timestep, i.e. the year which is
    to be used from the narrative

    Arguments
    ---------
    sim_yr : int
        Simulation year
    narrative_timesteps : list
        All defined timesteps in narrative

    Returns
    -------
    timestep : int
        Narrative timestep to use for calculation

    Example
    -------
    If we have a two-step narrative such as:
        year: 2015 - 2030, 2030 - 2050

    for the sim_yr 2020, the calculated values for
    2030 would need to be used. For the year 2031,
    the values 2050 would need to be used.
    """
    narrative_timesteps.sort()

    # Get corresponding narrative timestep
    if len(narrative_timesteps) == 1:
        timestep = narrative_timesteps[0]
    else:

        # Test if current year is larger than any narrative_timestep
        # and use last defined timestep if this is true. Otherwise
        # get correct timestep from narrative_timesteps
        if sim_yr > narrative_timesteps[-1]:
            timestep = narrative_timesteps[-1]
        else:
            for year_narrative in narrative_timesteps:

                if sim_yr <= year_narrative:
                    timestep = year_narrative
                else:
                    pass

    return timestep

def calc_annual_switch_params(
        simulated_yrs,
        regions,
        sig_param_tech
    ):
    """Calculate annual diffusion parameters
    for technologies based on sigmoid diffusion parameters

    Arguments
    ---------
    simulated_yrs : list
        Simulated years
    regions : list
        Regions
    sig_param_tech : dict
        Sigmoid parameters per submodel

    Returns
    -------
    """
    annual_tech_diff_params = {}

    for region in regions:
        annual_tech_diff_params[region] = {}

        # Iterate enduses
        for enduse, sector_region_tech_vals in sig_param_tech.items():
            annual_tech_diff_params[region][enduse] = {}

            # Iterate sectors
            for sector, reg_vals in sector_region_tech_vals.items():

                if reg_vals != {}:
                    annual_tech_diff_params[region][enduse][sector] = defaultdict(dict)

                    # Iterate simulation years
                    for sim_yr in simulated_yrs:

                        narrative_timesteps = list(sector_region_tech_vals[sector].keys())

                        correct_narrative_timestep = get_correct_narrative_timestep(
                            sim_yr=sim_yr, narrative_timesteps=narrative_timesteps)

                        for tech in reg_vals[correct_narrative_timestep][region].keys():

                            # Sigmoid parameters
                            param = reg_vals[correct_narrative_timestep][region][tech]

                            p_s_tech = enduse_func.get_service_diffusion(
                                param, sim_yr)

                            annual_tech_diff_params[region][enduse][sector][tech][sim_yr] = p_s_tech
                else:
                    annual_tech_diff_params[region][enduse][sector] = []

    return annual_tech_diff_params

def generate_annual_param_vals(
        regions,
        strategy_vars,
        simulated_yrs,
        path=False
    ):
    """
    Calculate parameter values for every year based
    on defined narratives and also add a generic
    container of other information necessary
    for parameter.

    Inputs
    -------
    regions : dict
        Regions
    strategy_vars : dict4
        Strategy variable infirmation
    simulated_yrs : list
        Simulated years
    path : str
        Path to local data

    Returns
    -------
    container_reg_param : dict
        Values for all simulated years for every region (all parameters for which values
        are provided for every region)
    container_non_reg_param : dict
        Values for all simulated years (all the same for very region)
    """
    reg_param = {}
    non_reg_param = defaultdict(dict)

    for region in regions:
        reg_param[region] = defaultdict(dict)

    for var_name, strategy_vars_values in strategy_vars.items():
        if var_name == 'generic_fuel_switch':
            print("..")
        single_dim_var = narrative_related.crit_dim_var(
            strategy_vars_values)

        if single_dim_var:

            # Additional dictionary passed along with every
            # variable containing additional information
            param_info = {}

            # Generic container of parameter
            try:
                param_info['enduse'] = strategy_vars_values[0]['enduse']
            except KeyError:
                param_info['enduse'] = [] # all sectors
            try:
                param_info['sector'] = strategy_vars_values[0]['sector']
            except KeyError:
                param_info['sector'] = True # all sectors
            try:
                param_info['fueltype_replace'] = strategy_vars_values[0]['fueltype_replace']
            except KeyError:
                pass
            try:
                param_info['fueltype_new'] = strategy_vars_values[0]['fueltype_new']
            except KeyError:
                pass

            # Calculate annual parameter value
            regional_strategy_vary = generate_general_parameter(
                regions=regions,
                narratives=strategy_vars_values,
                simulated_yrs=simulated_yrs)

            # Test if regional specific or not based on first narrative
            for narrative in strategy_vars_values[:1]:
                reg_specific_crit = narrative['regional_specific']

            if reg_specific_crit:
                for region in regions:
                    reg_param[region][var_name] = regional_strategy_vary[region]
                    reg_param[region][var_name]['param_info'] = param_info
            else:
                non_reg_param[var_name] = regional_strategy_vary
                non_reg_param[var_name]['param_info'] = param_info
        else:
            for sub_var_name, sub_var_values in strategy_vars_values.items():

                param_info = {}

                all_sectors = narrative_related.get_all_sectors_of_narratives(
                    sub_var_values)

                for sector in all_sectors:

                    get_sector_narrative = narrative_related.get_sector_narrative(
                        sector, sub_var_values)
                    
                    # Generic container of parameter
                    try:
                        param_info['enduse'] = get_sector_narrative[0]['enduse']
                    except KeyError:
                        param_info['enduse'] = [] # all sectors
                    try:
                        param_info['sector'] = get_sector_narrative[0]['sector']
                    except KeyError:
                        param_info['sector'] = True # all sectors
                    try:
                        param_info['fueltype_replace'] = get_sector_narrative[0]['fueltype_replace']
                    except KeyError:
                        pass
                    try:
                        param_info['fueltype_new'] = get_sector_narrative[0]['fueltype_new']
                    except KeyError:
                        pass

                    # Calculate annual parameter value
                    regional_strategy_vary = generate_general_parameter(
                        regions=regions,
                        narratives=get_sector_narrative,
                        simulated_yrs=simulated_yrs)

                    # Test if regional specific or not based on first narrative
                    for narrative in get_sector_narrative[:1]:
                        reg_specific_crit = narrative['regional_specific']

                    if reg_specific_crit:
                        for region in regions:
                            reg_param[region][var_name][sub_var_name] = regional_strategy_vary[region]
                            reg_param[region][var_name][sub_var_name] = dict(reg_param[region][var_name][sub_var_name])
                            reg_param[region][var_name][sub_var_name]['param_info'] = param_info
                    else:
                        non_reg_param[var_name][sub_var_name] = regional_strategy_vary
                        non_reg_param[var_name][sub_var_name]['param_info'] = param_info

    return dict(reg_param), dict(non_reg_param)

def generate_general_parameter(
        regions,
        narratives,
        simulated_yrs
    ):
    """Based on narrative input, calculate
    the parameter value for every modelled year

    Arguments
    ---------
    regions : list
        Regions
    narratives : List
        List containing all narratives of how a model
        parameter changes over time
    simulated_yrs : list
        Simulated years

    Returns
    --------
    container : dict
        All model paramters containing either:
        - all values for each region and year
        - all values for each region
    """
    container = defaultdict(dict)

    # Get latest narrative timestep as it could be that the narrative is
    # not defined as long enough as the simulated years (e.g. narrative only up
    # to 2040 but the year 2050 is simulated). In these cases, use the largest
    # narrative timestep (maximum assumed to stay constant from this time onwards)
    latest_narrative_timestep = 0
    for narrative in narratives:
        if narrative['end_yr'] > latest_narrative_timestep:
            latest_narrative_timestep = narrative['end_yr']

    for sim_yr in simulated_yrs:

        # -----------------------------------------------
        # Set curry_yr to largest year defined narrative if
        # sim_yr is larger
        # -----------------------------------------------
        if sim_yr > latest_narrative_timestep:
            curr_yr = latest_narrative_timestep
        else:
            curr_yr = sim_yr

        for narrative in narratives:

            # Years which narrative covers
            narrative_yrs = range(narrative['base_yr'], narrative['end_yr'] + 1, 1)

            if curr_yr in narrative_yrs:

                if not narrative['regional_specific']:

                    if narrative['diffusion_choice'] == 'linear':

                        lin_diff_factor = diffusion_technologies.linear_diff(
                            narrative['base_yr'],
                            curr_yr,
                            narrative['regional_vals_by'],
                            narrative['regional_vals_ey'],
                            narrative['end_yr'])

                        change_cy = lin_diff_factor

                    elif narrative['diffusion_choice'] == 'sigmoid':

                        diff_value = narrative['regional_vals_ey'] - narrative['regional_vals_by']

                        sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                            narrative['base_yr'],
                            curr_yr,
                            narrative['end_yr'],
                            narrative['sig_midpoint'],
                            narrative['sig_steepness'])

                        change_cy = diff_value * sig_diff_factor

                    container[sim_yr] = change_cy
                else:
                    for region in regions:

                        if narrative['diffusion_choice'] == 'linear':

                            lin_diff_factor = diffusion_technologies.linear_diff(
                                narrative['base_yr'],
                                curr_yr,
                                narrative['regional_vals_by'][region],
                                narrative['regional_vals_ey'][region],
                                narrative['end_yr'])

                            change_cy = lin_diff_factor

                        elif narrative['diffusion_choice'] == 'sigmoid':

                            diff_value = narrative['regional_vals_ey'] - narrative['regional_vals_by']

                            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                                narrative['base_yr'],
                                curr_yr,
                                narrative['end_yr'],
                                narrative['sig_midpoint'][region],
                                narrative['sig_steepness'][region])

                            change_cy = diff_value * sig_diff_factor

                        container[region][sim_yr] = change_cy

    return container
