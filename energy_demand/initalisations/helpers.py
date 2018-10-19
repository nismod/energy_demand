"""Short diverse helper functions
"""
from collections import defaultdict
from energy_demand.basic import basic_functions

def copy_fractions_all_sectors(
        fuel_tech_p_by,
        sectors,
        affected_enduses
    ):
    """Copy all defined fractions
    for an enduse to all setors

    Arguments
    ---------
    fuel_tech_p_by : dict
        Fuel shares per technolgy for an enduse
    sectors : list
        All sectors with this induse where the identical
        shares want to be transferred
    affected_enduses : list
        Enduses for which the values should be copied

    Returns
    -------
    out_dict : dict
        Fuel shares for all sectors
        i.e. {enduse: {sector: {fueltype: {tech: {share}}}}}
    """
    out_dict = defaultdict(dict)
    for sector in sectors:
        for enduse, techs in fuel_tech_p_by.items():
            if enduse in affected_enduses:
                out_dict[enduse][sector] = dict(techs) #dict necessary
            else:
                out_dict[enduse] = dict(techs)
    out_dict = dict(out_dict)

    return out_dict

def init_fuel_tech_p_by(all_enduses_with_fuels, fueltypes_nr):
    """Helper function to define stocks for all enduse and fueltype

    Arguments
    ----------
    all_enduses_with_fuels : dict
        Provided fuels
    fueltypes_nr : int
        Nr of fueltypes

    Returns
    -------
    fuel_tech_p_by : dict

    """
    fuel_tech_p_by = {}

    fueltpe_dicts= dict.fromkeys(range(fueltypes_nr), {})

    for enduse in all_enduses_with_fuels:
        fuel_tech_p_by[enduse] = dict(fueltpe_dicts)

    return fuel_tech_p_by

def init_dict_brackets(first_level_keys):
    """Initialise a  dictionary with one level

    Arguments
    ----------
    first_level_keys : list
        First level data

    Returns
    -------
    one_level_dict : dict
         dictionary
    """
    one_level_dict = {}

    for first_key in first_level_keys:
        one_level_dict[first_key] = {}

    return one_level_dict

def add_undef_techs(heat_pumps, specified_tech_enduse, enduses):
    """Add technology to dict

    Arguments
    ----------
    heat_pumps : list
        List with heat pumps
    specified_tech_enduse_by : dict
        Technologey per enduse
    enduses : list
        Enduses

    Return
    -------
    specified_tech_enduse : dict
        Specified techs per enduse
    """
    for enduse in enduses:
        for heat_pump in heat_pumps:
            for sector in specified_tech_enduse[enduse]:
                if heat_pump not in specified_tech_enduse[enduse][sector]:
                    specified_tech_enduse[enduse][sector].append(heat_pump)

    return specified_tech_enduse

def get_def_techs(fuel_tech_p_by):
    """Collect all technologies across all
    fueltypes for each endues

    Arguments
    ----------
    fuel_tech_p_by : dict
        Fuel share per technology for base year
    sector_crit : bool
        Criteria wheter fuel is given by sector or not

    Returns
    -------
    all_defined_tech_service_ey : dict
        All defined technologies with service in end year
    """
    all_defined_tech_service_ey = {}

    for enduse in fuel_tech_p_by:
        all_defined_tech_service_ey[enduse] = {}

        sector_crit = basic_functions.test_if_sector(
            fuel_tech_p_by[enduse])

        if sector_crit:
            for sector in fuel_tech_p_by[enduse]:
                all_defined_tech_service_ey[enduse][sector] = set()
                for fueltype in fuel_tech_p_by[enduse][sector]:
                    for tech in list(fuel_tech_p_by[enduse][sector][fueltype].keys()):
                        all_defined_tech_service_ey[enduse][sector].add(tech)
                all_defined_tech_service_ey[enduse][sector] = list(all_defined_tech_service_ey[enduse][sector]) 
        else:
            all_defined_tech_service_ey[enduse][None] = set()
            for fueltype in fuel_tech_p_by[enduse]:
                for tech in fuel_tech_p_by[enduse][fueltype]:
                    all_defined_tech_service_ey[enduse][None].add(tech)
            all_defined_tech_service_ey[enduse][None] = list(all_defined_tech_service_ey[enduse][None])

    return all_defined_tech_service_ey

def get_nested_dict_key(nested_dict):
    """Get all keys of nested dict

    Arguments
    ----------
    nested_dict : dict
        Nested dictionary

    Return
    ------
    all_nested_keys : list
        Key of nested dict
    """
    all_nested_keys = []

    for values in nested_dict.values():
        all_nested_keys += values.keys()

    return all_nested_keys

def set_same_eff_all_tech(technologies, f_eff_achieved=1):
    """Helper function to assing same achieved efficiency

    Arguments
    ----------
    technologies : dict
        Technologies
    f_eff_achieved : float,default=1
        Factor showing the fraction of how much an efficiency is achieved

    Returns
    -------
    technologies : dict
        Adapted technolog
    """
    for technology in technologies:
        technologies[technology].eff_achieved = f_eff_achieved

    return technologies
