"""Functions handling the narratives
"""
import math
import numpy as np

def get_crit_single_dim_var(var):
    """Check if nested dict or not

    Arguments
    ---------
    var : dict
        Dictionary to test wheter single or multidimensional parameter

    Returns
    -------
    single_dimension : bool
        True: Single dimension, False: Multidimensional parameter
    """
    if type(var) is list:
        single_dimension = True
    else:
        try:
            for entry in var:
                # If list is in ndested dict, then multidimensional
                if type(var[entry]) is list:
                    single_dimension = False
                    break
                else:
                    # IF no keys, then fail and thus single dimensional
                    var[entry].keys()

            single_dimension = False
        except AttributeError:
            single_dimension = True

    return single_dimension

def read_from_narrative(narratives):
    """Read from narratives the value
    of the last narrative

    """
    last_year = 0
    for narrative in narratives:

        if narrative['end_yr'] > last_year:
            last_value = narrative['value_ey']
            last_year = narrative['end_yr']

    return last_value

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
    default_narrative = [
        {
            'base_yr': base_yr,
            'end_yr': end_yr,
            'value_by': value_by,
            'value_ey': value_ey,
            'diffusion_choice': diffusion_choice,
            'sig_midpoint': sig_midpoint,
            'sig_steepness': sig_steepness,
            'regional_specific': regional_specific
        }
    ]

    return default_narrative

def create_narratives(raw_file_content, simulation_base_yr, default_streategy_vars):
    """Create multidimensional narratives. Check if each
    necessary input is defedin in csv file and otherwise
    replace with standard values

    Arguments
    ---------
    raw_file_content : panda
        Data of read csv file
    simulation_base_yr : int
        Model base year of simulation

    Outputs
    -------
    autocompleted_parameter_narratives : dict
        Parameters
    """
    parameter_narratives = {}

    # Test if single or multidimensional parameters
    try:
        for _index, row in raw_file_content.iterrows():
            sub_param_name = str(row['sub_param_name'])
            crit_single_dim_param = False
            break
    except KeyError: #sub_param_name is not provided as header argument in csv
        crit_single_dim_param = True

    # ----------------------------------------------
    # Create single or multi dimensional narratives
    # ----------------------------------------------
    for _index, row in raw_file_content.iterrows():

        # IF only single dimension parameter, add dummy mutliparameter name
        if crit_single_dim_param:
            sub_param_name = 'dummy_single_param'
        else:
            # Sub_parameter_name is only provided for multidimensional parameters
            sub_param_name = str(row['sub_param_name'])

        default_by = float(row['default_by'])
        end_yr = int(row['end_yr'])
        value_ey = float(row['value_ey'])

        try:
            affected_sector = row['sector']

            if type(affected_sector) is str:
                affected_sector = affected_sector
            else:
                affected_sector = True # replace nan value with True
        except KeyError:
            affected_sector = True

        try:
            diffusion_choice = str(row['diffusion_choice'])
        except KeyError:
            diffusion_choice = 'linear'

        try:
            if math.isnan(row['sig_midpoint']):
                sig_midpoint = 0 # default value
            else:
                sig_midpoint = float(row['sig_midpoint'])
        except KeyError:
            sig_midpoint = 0 # default value

        try:
            if math.isnan(row['sig_steepness']):
                sig_steepness = 1 # default value
            else:
                sig_steepness = float(row['sig_steepness'])
        except KeyError:
            sig_steepness = 1 # default value

        try:
            if str(row['regional_specific']) == 'True':
                regional_specific = True #bool(1)
            else:
                regional_specific = False #bool(0)
        except KeyError:

            # Read from original configuration whether
            #  this variable is regionally specific or not
            if crit_single_dim_param:
                regional_specific = default_streategy_vars['regional_specific']
            else:
                regional_specific = default_streategy_vars[sub_param_name]['regional_specific']

        switch = {
            'default_by': default_by,
            'base_yr': None,
            'end_yr': end_yr,
            'value_by': None,
            'value_ey': value_ey,
            'diffusion_choice': diffusion_choice,
            'sig_midpoint': sig_midpoint,
            'sig_steepness': sig_steepness,
            'regional_specific': regional_specific,
            'affected_sector': affected_sector}

        # Append switch to correct variable
        if sub_param_name in parameter_narratives.keys():
            parameter_narratives[sub_param_name].append(switch)
        else:
            parameter_narratives[sub_param_name] = [switch]

    # ----------------------
    # Autocomplete switches in order that from all
    # end_yrs a complete narrative is generated
    # ----------------------
    autocompleted_parameter_narratives = {}

    for sub_param_name, narratives in parameter_narratives.items():

        autocompleted_parameter_narratives[sub_param_name] = []

        # Get all years of narratives
        all_yrs = []
        for narrative in narratives:
            all_yrs.append(narrative['end_yr'])


        all_yrs.sort()

        # Iterate years
        for year_cnt, year in enumerate(all_yrs):

            # Get correct narative
            for narrative in narratives:
                if narrative['end_yr'] == year:
                    yr_narrative = narrative
                    break

            # Add missing entries to switch
            if year_cnt == 0:

                # Update
                yr_narrative['base_yr'] = simulation_base_yr
                yr_narrative['value_by'] = narrative['default_by']

                # previous value
                previous_yr = narrative['end_yr']
                previous_value = narrative['value_ey']
            else:

                # Update
                yr_narrative['base_yr'] = previous_yr
                yr_narrative['value_by'] = previous_value

                # previous value
                previous_yr = narrative['end_yr']
                previous_value = narrative['value_ey']

            del yr_narrative['default_by']

            autocompleted_parameter_narratives[sub_param_name].append(yr_narrative)

    # IF only single dimension parameter, remove dummy mutliparameter name
    if crit_single_dim_param:
        autocompleted_parameter_narratives = autocompleted_parameter_narratives['dummy_single_param']
    else:
        pass
    return autocompleted_parameter_narratives
