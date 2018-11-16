"""Script to convert fuel to energy service
"""
import numpy as np
from collections import defaultdict

from energy_demand.basic import lookup_tables
from energy_demand.technologies import tech_related
from energy_demand.initalisations import helpers

def init_nested_dict_brackets(first_level_keys, second_level_keys):
    """Initialise a nested dictionary with two levels

    Arguments
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

def init_nested_dict_zero(sector, first_level_keys, second_level_keys):
    """Initialise a nested dictionary with two levels

    Arguments
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
        nested_dict[first_level_key][sector] = {}
        for second_level_key in second_level_keys:
            nested_dict[first_level_key][sector][second_level_key] = 0

    return nested_dict

def sum_2_level_dict(two_level_dict):
    """Sum all entries in a two level dict

    Arguments
    ----------
    two_level_dict : dict
        Nested dict

    Returns
    -------
    tot_sum : float
        Number of all entries in nested dict
    """
    tot_sum = 0
    for j in two_level_dict.values():
        tot_sum += sum(j.values())

    return tot_sum

def sum_fuel_enduse_sectors(data_enduses, enduses):
    """Aggregate fuel for all sectors according to enduse

    Arguments
    --------
    data_enduses : dict
        Fuel per enduse
    enduses : list
        Enduses
    nr_fueltypes : int
        Number of fuetlypes

    Returns
    -------
    aggregated_fuel_enduse : dict
        Arregated fuel per enduse ({enduse: np.array(fueltype)})
    """
    aggregated_fuel_enduse = {}

    for enduse in enduses:
        aggregated_fuel_enduse[enduse] = sum(data_enduses[enduse].values())

    return aggregated_fuel_enduse

def get_s_fueltype_tech(
        enduses,
        fuel_p_tech_by,
        fuels,
        technologies,
        sector=False
    ):
    """Calculate total energy service fractions per technology.
    This calculation converts fuels into energy services (e.g. heating
    for fuel into heat demand) and then calculates how much an invidual
    technology contributes as a fraction of total energy service demand.

    This is calculated to determine how much the technology
    has already diffused up to the base year to define the
    first point on the sigmoid technology diffusion curve.

    Arguments
    ----------
    enduses : dict
        Enduses
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    technologies : object
        Technology of base year (region dependent)

    Return
    ------
    s_tech_by_p : dict
        Percentage of total energy service per technology for base year
    s_fueltype_by_p : dict
        Percentage of energy service per fueltype
    """
    fueltypes =  lookup_tables.basic_lookups()['fueltypes']

    service = init_nested_dict_brackets(fuels, fueltypes.values()) # Energy service per technology for base year
    s_tech_by_p = helpers.init_dict_brackets(fuels) # Percentage of total energy service per technology for base year
    s_fueltype_by_p = init_nested_dict_zero(sector, s_tech_by_p.keys(), range(len(fueltypes))) # Percentage of service per fueltype

    for enduse in enduses:

        # Depending if sector or not sector specific
        fuel = fuels[enduse][sector]

        for fueltype, fuel_fueltype in enumerate(fuel):
            tot_s_fueltype = 0

            # Initialise
            for tech in fuel_p_tech_by[enduse][sector][fueltype]:
                service[enduse][fueltype][tech] = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][sector][fueltype].items():

                # Fuel share based on defined shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype

                # Get efficiency for base year
                if technologies[tech].tech_type == 'heat_pump':
                    eff_tech = tech_related.eff_heat_pump(
                        temp_diff=10,
                        efficiency_intersect=technologies[tech].eff_by)
                else:
                    eff_tech = technologies[tech].eff_by

                # Energy service: Service == Fuel of technoloy * efficiency
                s_fueltype_tech = fuel_tech * eff_tech

                # Add energy service demand
                service[enduse][fueltype][tech] += s_fueltype_tech

                # Total energy service demand within a fueltype
                tot_s_fueltype += s_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][sector][fueltype]:
                if tot_s_fueltype == 0: # No fuel in this fueltype
                    s_fueltype_by_p[enduse][sector][fueltype] += 0
                else:
                    s_fueltype_by_p[enduse][sector][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_s = sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_s_enduse in service[enduse].items():
            for technology, s_tech in technology_s_enduse.items():

                with np.errstate(divide='ignore'):

                    if total_s == 0:
                        s_p_tech = 0
                    else:
                        # Calculate service
                        s_p_tech = s_tech / total_s

                     # Do not add dummy technology with zero service
                    if technology == 'placeholder_tech' and s_p_tech == 0:
                        pass
                    else:
                        try:
                            s_tech_by_p[enduse][technology] += s_p_tech
                        except:
                            s_tech_by_p[enduse][technology] = s_p_tech

        # Convert service per enduse
        for fueltype in s_fueltype_by_p[enduse][sector]:
            with np.errstate(divide='ignore'):
                s_fueltype_by_p[enduse][sector][fueltype] = s_fueltype_by_p[enduse][sector][fueltype] / total_s

    #warnings.filterwarnings('ignore') # Ignore warnings
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service 
    for enduse, s_p_techs in s_tech_by_p.items():
        sum_enduse = sum(s_p_techs.values())
        if round(sum_enduse, 2) != 0: # if total is zero, no demand provided
            assert round(sum_enduse, 2) == 1.0

    return s_tech_by_p, s_fueltype_by_p
