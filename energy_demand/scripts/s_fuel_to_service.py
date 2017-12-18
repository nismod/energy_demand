"""Script to convert fuel to energy service
"""
import warnings
import numpy as np
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

def init_nested_dict_zero(first_level_keys, second_level_keys):
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
            nested_dict[first_level_key][second_level_key] = 0

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
    for  j in two_level_dict.values():
        tot_sum += sum(j.values())

    return tot_sum

def sum_fuel_enduse_sectors(data_enduses, enduses, nr_fueltypes):
    """Aggregated fuel for all sectors according to enduse

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
        aggregated_fuel_enduse[str(enduse)] = np.zeros((nr_fueltypes), dtype=float)

    # Iterate and sum fuel per enduse
    for fuels_sector in data_enduses.values():
        for enduse, fuels_enduse in fuels_sector.items():
            aggregated_fuel_enduse[enduse] += fuels_enduse

    return aggregated_fuel_enduse

def get_service_fueltype_tech(tech_list, lu_fueltypes, fuel_p_tech_by, fuels, technologies):
    """Calculate total energy service fractions per technology.
    Tis calculation converts fuels into energy services (e.g. heating
    for fuel into heat demand) and then calculated how much an invidual
    technology contributes as a fraction of total energy service demand.

    This is calculated to determine how much the technology
    has already diffused up to the base year to define the
    first point on the sigmoid technology diffusion curve.

    Arguments
    ----------
    tech_list : list
        Technologies
    lu_fueltypes : dict
        Fueltypes
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    technologies : object
        Technology of base year (region dependent)

    Return
    ------
    service_tech_by_p : dict
        Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p : dict
        Percentage of energy service witin a fueltype for all
        technologies with this fueltype for base year
    service_fueltype_by_p : dict
        Percentage of energy service per fueltype
    """
    # Energy service per technology for base year
    service = init_nested_dict_brackets(fuels, lu_fueltypes.values())

     # Percentage of total energy service per technology for base year
    service_tech_by_p = helpers.init_dict_brackets(fuels)

    # Percentage of service per technologies within the fueltypes
    service_fueltype_tech_by_p = init_nested_dict_brackets(fuels, lu_fueltypes.values())

    # Percentage of service per fueltype
    service_fueltype_by_p = init_nested_dict_zero(
        service_tech_by_p.keys(),
        range(len(lu_fueltypes)))

    for enduse, fuel in fuels.items():
        for fueltype, fuel_fueltype in enumerate(fuel): #Iterate array
            tot_service_fueltype = 0

            for tech in fuel_p_tech_by[enduse][fueltype]:
                service[enduse][fueltype][tech] = 0

            # Iterate technologies to calculate share of energy
            # service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype].items():

                # Fuel share based on defined shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype

                # Get technology type
                tech_type = tech_related.get_tech_type(tech, tech_list)

                # Get efficiency for base year
                if tech_type == 'heat_pump':
                    eff_tech = tech_related.eff_heat_pump(
                        temp_diff=10,
                        efficiency_intersect=technologies[tech].eff_by)
                elif tech_type == 'dummy_tech':
                    eff_tech = 1
                else:
                    eff_tech = technologies[tech].eff_by

                # Energy service of end use: Service == Fuel of technoloy * efficiency
                service_fueltype_tech = fuel_tech * eff_tech

                # Add energy service demand
                service[enduse][fueltype][tech] += service_fueltype_tech

                # Total energy service demand within a fueltype
                tot_service_fueltype += service_fueltype_tech

            # Calculate percentage of service enduse within fueltype
            for tech in fuel_p_tech_by[enduse][fueltype]:
                if tot_service_fueltype == 0: # No fuel in this fueltype
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = 0
                    service_fueltype_by_p[enduse][fueltype] += 0
                else:
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = service[enduse][fueltype][tech] / tot_service_fueltype
                    service_fueltype_by_p[enduse][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_service = sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():

                with np.errstate(divide='ignore'):
                    service_tech_by_p[enduse][technology] = service_tech / total_service
                    warnings.filterwarnings('ignore')

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:

            #OptimizeWarning: Covariance of the parameters could not be estimated
            with np.errstate(divide='ignore'):
                service_fueltype_by_p[enduse][fueltype] = service_fueltype_by_p[enduse][fueltype] / total_service

    # Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p
