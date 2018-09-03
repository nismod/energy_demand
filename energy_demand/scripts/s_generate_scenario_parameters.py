"""Generate scenario paramters for every year
"""
import os
from collections import defaultdict
from energy_demand.technologies import diffusion_technologies

def calc_annual_switch_params(
    reg_strategy_vars,
    rs_sig_param_tech,
    ss_sig_param_tech,
    is_sig_param_tech):
    """
    """
    '''annual_tech_diff_params = {}

    for enduse, region_tech_vals in rs_sig_param_tech.items():

        for region in region_tech_vals.keys():

            for tech in region_tech_vals[region].keys():
                # Sigmoid diffusion values
                midpoint = region_tech_vals[tech]['midpoint']
                steepness = region_tech_vals[tech]['steepness']
                l_parameter = region_tech_vals[tech]['l_parameter']

                # Iterate every year
                for sim_yr in range(2015, 2051):

                    if midpoint = 'linear':

                    else:
                        annual_tech_diff_params[region][enduse][tech][sim_yr] = 
   
    reg_strategy_vars["annual_tech_diff_params"] = annual_tech_diff_params'''
    return reg_strategy_vars

def generate_annual_param_vals(
        regions,
        strategy_vars,
        simulated_yrs,
        path=False
    ):
    """
    Calculate parameter values for every year based
    on defined narratives.

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
    container_reg_param = defaultdict(dict)
    container_non_reg_param = {}

    for parameter_name in strategy_vars.keys():

        path_file = os.path.join(
            path, "params_{}.{}".format(parameter_name, "csv"))

        # Calculate annual parameter value 
        regional_strategy_vary = generate_general_parameter(
            regions=regions,
            narratives=strategy_vars[parameter_name]['narratives'],
            simulated_yrs=simulated_yrs,
            path=path_file)

        # Test if regional specific or not based on first narrative
        for narrative in strategy_vars[parameter_name]['narratives'][:1]:
            reg_specific_crit = narrative['regional_specific']

        if reg_specific_crit:
            for region in regions:
                container_reg_param[region][parameter_name] = regional_strategy_vary[region]
        else:
            container_non_reg_param[parameter_name] = regional_strategy_vary

    return dict(container_reg_param), dict(container_non_reg_param)

def generate_general_parameter(
        regions,
        narratives,
        simulated_yrs,
        path=False
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
    #entries = []

    for narrative in narratives:

        # -- Regional paramters of narrative step
        if not narrative['sig_midpoint']:
            sig_midpoint = 0
        if not narrative['sig_steepness']:
            sig_steepness = 1

        # Modelled years
        narrative_yrs = range(narrative['base_yr'], narrative['end_yr'] + 1, 1)

        if not narrative['regional_specific']:

            for curr_yr in narrative_yrs:

                if curr_yr in simulated_yrs:

                    if narrative['diffusion_choice'] == 'linear':

                        lin_diff_factor = diffusion_technologies.linear_diff(
                            narrative['base_yr'],
                            curr_yr,
                            narrative['regional_vals_by'],
                            narrative['regional_vals_ey'],
                            narrative['end_yr'])

                        change_cy = lin_diff_factor

                    elif narrative['diffusion_choice'] == 'sigmoid': # Sigmoid diffusion

                        diff_value = narrative['regional_vals_ey'] - narrative['regional_vals_by']

                        sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                            narrative['base_yr'],
                            curr_yr,
                            narrative['end_yr'],
                            sig_midpoint,
                            sig_steepness)

                        change_cy = diff_value * sig_diff_factor

                    container[curr_yr] = change_cy
        else:
            for region in regions:

                # Iterate every modelled year
                for curr_yr in narrative_yrs:

                    if curr_yr in simulated_yrs:

                        if narrative['diffusion_choice'] == 'linear':

                            lin_diff_factor = diffusion_technologies.linear_diff(
                                narrative['base_yr'],
                                curr_yr,
                                narrative['regional_vals_by'][region],
                                narrative['regional_vals_ey'][region],
                                narrative['end_yr'])

                            change_cy = lin_diff_factor
                        elif narrative['diffusion_choice'] == 'sigmoid':

                            diff_value = narrative['regional_vals_ey'][region] - narrative['regional_vals_by'][region]

                            sig_diff_factor = diffusion_technologies.sigmoid_diffusion(
                                narrative['base_yr'],
                                curr_yr,
                                narrative['end_yr'],
                                sig_midpoint,
                                sig_steepness)

                            change_cy = diff_value * sig_diff_factor

                        container[region][curr_yr] = change_cy

                        '''entry = []
                        entry.append(region)
                        entry.append(curr_yr)
                        entry.append(change_cy)
                        entries.append(entry)'''

    # Write out to txt files
    '''# Create dataframe to store values of parameter
    col_names = ["region", "year", "value"]
    my_df = pd.DataFrame(entries, columns=col_names)
    my_df.to_csv(path, index=False) #Index prevents writing index rows'''
    return container
