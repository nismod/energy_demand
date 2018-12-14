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
    if type(var) is list:
        single_dimension = True

        #Test if multidmensional in list
        single_dimension = True
        for list_entry in var:
            for key, value in list_entry.items():
                # If list is in ndested dict, then multidimensional
                if type(value) is not list:
                    if hasattr(value, 'keys') and not value:
                        # Empty dictionary counts as single dimensional
                        pass
                    elif hasattr(value, 'keys') and value:
                        # Populated dict counts as multidimensional
                        single_dimension = False

        print("AAA================================")
        print(var)
    else:
        single_dimension = True
        for key, value in var.items():
            # If list is in ndested dict, then multidimensional
            if type(value) is not list:
                if hasattr(value, 'keys') and not value:
                    # Empty dictionary counts as single dimensional
                    pass
                elif hasattr(value, 'keys') and value:
                    # Populated dict counts as multidimensional
                    single_dimension = False

    return single_dimension
    
a = [{'base_yr': 2015, 'end_yr': 2050, 'fueltype_new': 0, 'sig_steepness': 1, 'value_by': 5, 'sig_midpoint': 0, 'regional_specific': False, 'value_ey': 5, 'diffusion_choice': 'linear', 'fueltype_replace': 0}]


r = crit_dim_var(a)

print(r)