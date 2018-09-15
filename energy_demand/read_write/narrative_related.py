"""Functions handling the narratives
"""
import math

def check_multidimensional_var(var):
    """Check if nested dict or not


    """
    print("A " + str(var))
    #if type(var) == list:
    #    single_dimension = True
    #else:
    try:
        for entry in var:
            var[entry].keys()
        single_dimension = False
    except AttributeError:
        single_dimension = True
    
    return single_dimension

def check_if_multidimensional_var(strategy_var):
    """Check if narratives or dict with narratives (multidimensional parameter)
    TODO REMOVE AND REPLACE WITH check_multidimensional_var
    """
    if type(strategy_var) == list:
        multidimensional_var = False
    elif type(strategy_var) == dict:
        multidimensional_var = True
    else:
        pass
    
    return multidimensional_var

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

def create_narratives(raw_csv_file, simulation_base_yr):
    """Create multidimensional narratives

    Arguments
    ---------
    base_yr : int
        Model base year of simulation
    """

    parameter_narratives = {}

    for _index, row in raw_csv_file.iterrows():

        # Properties enduse,base_yr,value_by,end_yr,value_ey,diffusion_choice,sig_midpoint,sig_steepness,regional_specific
        enduse = str(row['enduse'])
        default_by = float(row['default_by'])
        #base_yr = int(row['base_yr'])
        #value_by = float(row['value_by'])
        end_yr = int(row['end_yr'])
        value_ey = float(row['value_ey'])
        diffusion_choice = str(row['diffusion_choice'])
        
        '''# Replacy if any entry is 'True' or 'False' with True or False
        if scenario_value == 'True':
            scenario_value = True
        elif scenario_value == 'False':
            scenario_value = False
        else:
            pass'''
        try:
            if math.isnan(row['sig_midpoint']): # Left empty in csv file
                sig_midpoint = 0 # default value
            else:
                sig_midpoint = float(row['sig_midpoint'])
        except KeyError:
            sig_midpoint = 0 # default value
        
        try:
            if math.isnan(row['sig_steepness']): # Left empty in csv file
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
            regional_specific = True

        # Additional
        # affected_enduse
        # sector?

        # Switch
        switch = {
            'default_by': default_by,
            'base_yr': None,
            'end_yr': end_yr,
            'value_by': None,
            'value_ey': value_ey,
            'diffusion_choice': diffusion_choice,
            'sig_midpoint': sig_midpoint,
            'sig_steepness': sig_steepness,
            'regional_specific': regional_specific}

        # Append switch to correct variable
        if enduse in parameter_narratives.keys():
            parameter_narratives[enduse].append(switch)
        else:
            parameter_narratives[enduse] = [switch]
    
    # ----------------------
    # Autocomplete switches in order that from all end_yrs a complete 
    # narrative is generated
    # ----------------------
    autocompleted_parameter_narratives = {}

    for enduse, narratives in parameter_narratives.items():

        autocompleted_parameter_narratives[enduse] = []

        # Get all years of narratives
        all_yrs = []
        for narrative in narratives:
            all_yrs.append(narrative['end_yr'])

        # Sort
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

            autocompleted_parameter_narratives[enduse].append(yr_narrative)

    return autocompleted_parameter_narratives
