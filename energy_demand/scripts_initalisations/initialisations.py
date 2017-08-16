"""Helper initialising functions
"""
#pylint: disable=I0011, C0321, C0301, C0103, C0325, R0902, R0913, no-member, E0213
def dict_zero(first_level_keys):
    """Initialise a  dictionary with one level

    Parameters
    ----------
    first_level_keys : list
        First level data

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = dict.fromkeys(first_level_keys, 0) # set zero as argument

    return one_level_dict

def service_type_tech_by_p(fueltypes_lu, fuel_enduse_tech_p_by):
    """Initialise dict #TODO: Improve Speed
    """
    service_fueltype_tech_by_p = {}
    for fueltype_int in fueltypes_lu.values():
        service_fueltype_tech_by_p[fueltype_int] = dict.fromkeys(fuel_enduse_tech_p_by[fueltype_int].keys(), 0)

    return service_fueltype_tech_by_p

def init_dict_brackets(first_level_keys):
    """Initialise a  dictionary with one level

    Parameters
    ----------
    first_level_keys : list
        First level data

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = {}

    # Iterate first level
    for first_key in first_level_keys:
        one_level_dict[first_key] = {}

    return one_level_dict

def init_nested_dict_brackets(first_level_keys, second_level_keys):
    """Initialise a nested dictionary with two levels

    Parameters
    ----------
    first_level_keys : list
        First level data
    second_level_keys : list
        Data to add in nested dict

    Returns
    -------
    nested_dict : dict
        Nested 2 level dictionary
    """
    nested_dict = {}

    for first_level_key in first_level_keys:
        nested_dict[first_level_key] = {}
        for second_level_key in second_level_keys:
            nested_dict[first_level_key][second_level_key] = {}

    return nested_dict

def init_nested_dict_zero(first_level_keys, second_level_keys):
    """Initialise a nested dictionary with two levels

    Parameters
    ----------
    first_level_keys : list
        First level data
    second_level_keys : list
        Data to add in nested dict

    Returns
    -------
    nested_dict : dict
        Nested 2 level dictionary
    """
    nested_dict = {}

    for first_level_key in first_level_keys:
        nested_dict[first_level_key] = {}
        for second_level_key in second_level_keys:
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



def initialise_out_dict_av():
    """Helper function to initialise dict
    """
    out_dict_av = {0: {}, 1: {}}
    for dtype in out_dict_av:
        month_dict = {}
        for month in range(12):
            month_dict[month] = {k: 0 for k in range(24)}
        out_dict_av[dtype] = month_dict

    return out_dict_av

def initialise_main_dict():
    """Helper function to initialise dict
    """
    out_dict_av = {0: {}, 1: {}}
    for dtype in out_dict_av:
        month_dict = {}
        for month in range(12):
            month_dict[month] = {k: [] for k in range(24)}
        out_dict_av[dtype] = month_dict

    return out_dict_av
