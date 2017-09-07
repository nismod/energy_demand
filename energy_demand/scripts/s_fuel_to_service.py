"""Script to convert fuel to energy service
"""
import os
import numpy as np
import logging
from energy_demand.technologies import technologies_related

def write_service_fueltype_by_p(path_to_txt, data):
    """Write out function

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}".format(
        'service', 'fueltype', 'service_p') + '\n'
              )

    for service, fueltypes in data.items():
        for fueltype, service_p in fueltypes.items():
            file.write(
                "{}, {}, {}".format(
                    service, fueltype, float(service_p)) + '\n')

    file.close()

    return

def write_service_fueltype_tech_by_p(path_to_txt, data):
    """Write out function

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}, {}".format(
        'service', 'fueltype', 'technology', 'service_p') + '\n'
              )

    for service, fueltype_tech in data.items():
        for fueltype, tech_list in fueltype_tech.items():
            if tech_list == {}:
                file.write("{}, {}, {}, {}".format(
                    service, fueltype, "None", 0) + '\n') #None and 0
            else:
                for tech, service_p in tech_list.items():
                    file.write("{}, {}, {}, {}".format(
                        service, fueltype, tech, float(service_p)) + '\n')

    file.close()

    return

def write_service_tech_by_p(path_to_txt, data):
    """Write out function

    Arguments
    ----------
    path_to_txt : str
        Path to txt file
    data : dict
        Data to write out
    """
    file = open(path_to_txt, "w")
    file.write("{}, {}, {}".format(
        'enduse', 'technology', 'service_p') + '\n'
              )

    for enduse, technologies in data.items():
        for tech, service_p in technologies.items():
            file.write("{}, {}, {}".format(
                str.strip(enduse), str.strip(tech), float(service_p)) + '\n'
                      )

    file.close()

    return

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
    '''tot_sum = 0
    for i in two_level_dict:
        for j in two_level_dict[i]:
            tot_sum += two_level_dict[i][j]
    '''
    tot_sum = 0
    for _, j in two_level_dict.items():
        tot_sum += sum(j.values())

    return tot_sum


def ss_sum_fuel_enduse_sectors(ss_fuel_raw_data_enduses, ss_enduses, nr_fueltypes):
    """Aggregated fuel for all sectors according to enduse
    """
    aggregated_fuel_enduse = {}

    for enduse in ss_enduses:
        aggregated_fuel_enduse[str(enduse)] = np.zeros((nr_fueltypes))

    # Iterate and sum fuel per enduse
    for _, fuels_sector in ss_fuel_raw_data_enduses.items():
        for enduse, fuels_enduse in fuels_sector.items():
            aggregated_fuel_enduse[enduse] += fuels_enduse

    return aggregated_fuel_enduse

def get_service_fueltype_tech(tech_list, hybrid_technologies, lu_fueltypes, fuel_p_tech_by, fuels, tech_stock):
    """Calculate total energy service percentage of each technology
    and energy service percentage within the fueltype

    This calculation converts fuels into energy services (e.g. heating
    for fuel into heat demand) and then calculated how much an invidual
    technology contributes in percent to total energy service demand.

    This is calculated to determine how much the technology
    has already diffused up to the base year to define the
    first point on the sigmoid technology diffusion curve.

    Arguments
    ----------
    lu_fueltypes : dict
        Fueltypes
    fuel_p_tech_by : dict
        Assumed fraction of fuel for each technology within a fueltype
    fuels : array
        Base year fuel demand
    tech_stock : object
        Technology stock of base year (region dependent)

    Return
    ------
    service_tech_by_p : dict
        Percentage of total energy service per technology for base year
    service_fueltype_tech_by_p : dict
        Percentage of energy service witin a fueltype for all
        technologies with this fueltype for base year
    service_fueltype_by_p : dict
        Percentage of energy service per fueltype

    Notes
    -----
    Regional temperatures are not considered because otherwise the initial fuel share of
    hourly dependent technology would differ and thus the technology diffusion within a region.
    Therfore a constant technology efficiency of the full year needs to
    be assumed for all technologies.

    Because regional efficiencies may differ within regions, the fuel distribution within
    the fueltypes may also differ
    """
    # Energy service per technology for base year
    service = init_nested_dict_brackets(fuels, lu_fueltypes.values())

     # Percentage of total energy service per technology for base year
    service_tech_by_p = init_dict_brackets(fuels)

    # Percentage of service per technologies within the fueltypes
    service_fueltype_tech_by_p = init_nested_dict_brackets(fuels, lu_fueltypes.values())

    # Percentage of service per fueltype
    service_fueltype_by_p = init_nested_dict_zero(service_tech_by_p.keys(), range(len(lu_fueltypes)))

    for enduse, fuel in fuels.items():
        for fueltype, fuel_fueltype in enumerate(fuel):
            tot_service_fueltype = 0

            for tech in fuel_p_tech_by[enduse][fueltype]:
                service[enduse][fueltype][tech] = 0

            # Iterate technologies to calculate share of energy service depending on fuel and efficiencies
            for tech, fuel_alltech_by in fuel_p_tech_by[enduse][fueltype].items():

                # Fuel share based on defined fuel shares within fueltype (share of fuel * total fuel)
                fuel_tech = fuel_alltech_by * fuel_fueltype
                #logging.debug("------------Tech: {}  {} ".format(fuel_alltech_by, fuel_fueltype))

                # Get technology type
                tech_type = technologies_related.get_tech_type(tech, tech_list)

                # Get efficiency depending whether hybrid or regular technology or heat pumps for base year
                if tech_type == 'hybrid_tech':
                    eff_tech = hybrid_technologies[tech]['average_efficiency_national_by']
                elif tech_type == 'heat_pump':
                    eff_tech = technologies_related.eff_heat_pump(
                        temp_diff=10,
                        efficiency_intersect=tech_stock[tech]['eff_by']
                        )
                elif tech_type == 'dummy_tech':
                    eff_tech = 1
                else:
                    eff_tech = tech_stock[tech]['eff_by']

                # Energy service of end use: Service == Fuel of technoloy * efficiency
                service_fueltype_tech = fuel_tech * eff_tech
                ###logging.debug("SERVICE NATIONA LCALCUATION: {} {} {}  {}  {}".format(enduse, tech, fuel_tech, eff_tech, service_fueltype_tech))

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
                    service_fueltype_tech_by_p[enduse][fueltype][tech] = (1 / tot_service_fueltype) * service[enduse][fueltype][tech]
                    service_fueltype_by_p[enduse][fueltype] += service[enduse][fueltype][tech]

        # Calculate percentage of service of all technologies
        total_service = sum_2_level_dict(service[enduse])

        # Percentage of energy service per technology
        for fueltype, technology_service_enduse in service[enduse].items():
            for technology, service_tech in technology_service_enduse.items():
                service_tech_by_p[enduse][technology] = (1 / total_service) * service_tech
                #logging.debug("Technology_enduse: " + str(technology) + str("  ") + str(service_tech))

        ###logging.debug("Total Service base year for enduse {}  :  {}".format(enduse, total_service))

        # Convert service per enduse
        for fueltype in service_fueltype_by_p[enduse]:
            service_fueltype_by_p[enduse][fueltype] = (1.0 / total_service) * service_fueltype_by_p[enduse][fueltype]

    '''# Assert does not work for endues with no defined technologies
    # --------
    # Test if the energy service for all technologies is 100%
    # Test if within fueltype always 100 energy service
    '''
    return service_tech_by_p, service_fueltype_tech_by_p, service_fueltype_by_p

def run(data):
    """Function to run script
    """
    logging.debug("... start script {}".format(os.path.basename(__file__)))

    # RESIDENTIAL: Convert base year fuel input assumptions to energy service
    rs_service_tech_by_p, rs_service_fueltype_tech_by_p, rs_service_fueltype_by_p = get_service_fueltype_tech(
        data['assumptions']['tech_list'],
        data['assumptions']['hybrid_technologies'],
        data['lookups']['fueltype'],
        data['assumptions']['rs_fuel_tech_p_by'],
        data['fuels']['rs_fuel_raw_data_enduses'],
        data['assumptions']['technologies']
        )

    # SERVICE: Convert base year fuel input assumptions to energy service
    fuels_aggregated_across_sectors = ss_sum_fuel_enduse_sectors(
        data['fuels']['ss_fuel_raw_data_enduses'],
        data['enduses']['ss_all_enduses'],
        data['lookups']['nr_of_fueltypes'])

    ss_service_tech_by_p, ss_service_fueltype_tech_by_p, ss_service_fueltype_by_p = get_service_fueltype_tech(
        data['assumptions']['tech_list'],
        data['assumptions']['hybrid_technologies'],
        data['lookups']['fueltype'],
        data['assumptions']['ss_fuel_tech_p_by'],
        fuels_aggregated_across_sectors,
        data['assumptions']['technologies']
        )

    # INDUSTRY
    fuels_aggregated_across_sectors = ss_sum_fuel_enduse_sectors(
        data['fuels']['is_fuel_raw_data_enduses'],
        data['enduses']['is_all_enduses'],
        data['lookups']['nr_of_fueltypes'])

    is_service_tech_by_p, is_service_fueltype_tech_by_p, is_service_fueltype_by_p = get_service_fueltype_tech(
        data['assumptions']['tech_list'],
        data['assumptions']['hybrid_technologies'],
        data['lookups']['fueltype'],
        data['assumptions']['is_fuel_tech_p_by'],
        fuels_aggregated_across_sectors,
        data['assumptions']['technologies']
        )

    # Write to csv files
    write_service_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'rs_service_tech_by_p.csv'),
        rs_service_tech_by_p)

    write_service_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'ss_service_tech_by_p.csv'),
        ss_service_tech_by_p)
    write_service_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'is_service_tech_by_p.csv'),
        is_service_tech_by_p)
    write_service_fueltype_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'rs_service_fueltype_tech_by_p.csv'), 
        rs_service_fueltype_tech_by_p)
    write_service_fueltype_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'ss_service_fueltype_tech_by_p.csv'),
        ss_service_fueltype_tech_by_p)
    write_service_fueltype_tech_by_p(
        os.path.join(data['local_paths']['dir_services'], 'is_service_fueltype_tech_by_p.csv'),
        is_service_fueltype_tech_by_p)
    write_service_fueltype_by_p(
        os.path.join(data['local_paths']['dir_services'], 'rs_service_fueltype_by_p.csv'),
        rs_service_fueltype_by_p)
    write_service_fueltype_by_p(
        os.path.join(data['local_paths']['dir_services'], 'ss_service_fueltype_by_p.csv'),
        ss_service_fueltype_by_p)
    write_service_fueltype_by_p(
        os.path.join(data['local_paths']['dir_services'], 'is_service_fueltype_by_p.csv'),
        is_service_fueltype_by_p)

    logging.debug("... finished script {}".format(os.path.basename(__file__)))
    return
