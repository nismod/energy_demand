def crit_dim_var(var):
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
    single_dimension = True

    # Test if list nor not
    if type(var) is list:
        for list_entry in var:
            for key, value in list_entry.items():

                if type(value) is not list:
                    if hasattr(value, 'keys') and key not in ['regional_vals_by', 'regional_vals_cy']:
                        if len(value.keys()) != 0:
                            single_dimension = False
                        else:
                            pass
    else:
       for key, value in var.items():
            if type(value) is not list:
                if hasattr(value, 'keys'):
                    if len(value.keys()) != 0 and key not in ['regional_vals_by', 'regional_vals_cy']:
                        single_dimension = False
            else:
                if value == []:
                    pass
                else:
                    single_dimension = False

    return single_dimension
    
#a = [{'base_yr': 2015, 'end_yr': 2050, 'fueltype_new': 0, 'sig_steepness': 1, 'value_by': 5, 'sig_midpoint': 0, 'regional_specific': False, 'value_ey': 5, 'diffusion_choice': 'linear', 'fueltype_replace': 0}]
#r = crit_dim_var(a)

a =  [
    {
        'sector': 'dummy_sector',
        'regional_specific': True,
        'value_ey': 1.0,
        'regional_vals_by': {'E06000001': 0.05, 'E06000018': 0.05}}]

r = crit_dim_var(a)
print(r)