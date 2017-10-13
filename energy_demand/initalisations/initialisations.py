"""Helper initialising functions
"""

def init_fuel_tech_p_by(all_enduses_with_fuels, nr_of_fueltypes):
    """Helper function to define stocks for all enduse and fueltype

    Arguments
    ----------
    all_enduses_with_fuels : dict
        Provided fuels
    nr_of_fueltypes : int
        Nr of fueltypes

    Returns
    -------
    fuel_tech_p_by : dict

    """
    fuel_tech_p_by = {}

    for enduse in all_enduses_with_fuels:
        fuel_tech_p_by[enduse] = dict.fromkeys(range(nr_of_fueltypes), {})

    return fuel_tech_p_by

def dict_zero(first_level_keys):
    """Initialise a dictionary with one level and
    set zero as the value

    Arguments
    ----------
    first_level_keys : list
        First level data

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = dict.fromkeys(first_level_keys, 0)

    return one_level_dict

def service_type_tech_by_p(lu_fueltypes, fuel_tech_p_by):
    """Initialise dict and fill with zeros

    Arguments
    ----------
    lu_fueltypes : dict
        Look-up dictionary
    fuel_tech_p_by : dict
        Fuel fraction per technology for base year

    Return
    -------
    service_fueltype_tech_by_p : dict
        Fraction of service per fueltype and technology for base year
    """
    service_fueltype_tech_by_p = {}
    for fueltype_int in lu_fueltypes.values():
        service_fueltype_tech_by_p[fueltype_int] = dict.fromkeys(fuel_tech_p_by[fueltype_int].keys(), 0)

    return service_fueltype_tech_by_p
