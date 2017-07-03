def init_dict(first_level_keys, crit):
    """Initialise a  dictionary with one level

    Parameters
    ----------
    first_level_keys : list
        First level data
    crit : str
        Criteria wheater initialised with `{}` or `0`

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = {}

    # Iterate first level
    for first_key in first_level_keys:
        if crit == 'brackets':
            one_level_dict[first_key] = {}
        if crit == 'zero':
            one_level_dict[first_key] = 0

    return one_level_dict

def init_nested_dict(first_level_keys, second_level_keys, crit):
    """Initialise a nested dictionary with two levels

    Parameters
    ----------
    first_level_keys : list
        First level data
    second_level_keys : list
        Data to add in nested dict
    crit : str
        Criteria wheater initialised with `{}` or `0`

    Returns
    -------
    nested_dict : dict
        Nested 2 level dictionary
    """
    nested_dict = {}

    for first_level_key in first_level_keys:
        nested_dict[first_level_key] = {}
        for second_level_key in second_level_keys:
            if crit == 'brackets':
                nested_dict[first_level_key][second_level_key] = {}
            if crit == 'zero':
                nested_dict[first_level_key][second_level_key] = 0

    return nested_dict

def sum_2_level_dict(two_level_dict):
    """Sum all entries in a two level dict

    Parameters
    ----------
    two_level_dict : dict
        Nested dict

    Returns
    -------
    tot_sum : float
        Number of all entries in nested dict
    """
    tot_sum = 0
    for i in two_level_dict:
        for j in two_level_dict[i]:
            tot_sum += two_level_dict[i][j]

    return tot_sum

def initialise_service_fueltype_tech_by_p(fueltypes_lu, fuel_enduse_tech_p_by):
    service_fueltype_tech_by_p = {}

    for fueltype_int in fueltypes_lu.values():
        service_fueltype_tech_by_p[fueltype_int] = {}
        for tech in fuel_enduse_tech_p_by[fueltype_int]:
            service_fueltype_tech_by_p[fueltype_int][tech] = 0

    return service_fueltype_tech_by_p
